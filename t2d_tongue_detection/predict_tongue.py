"""T2D probability for tongue photos with the final model from tongue_features.ipynb (final_model.joblib).

Pipeline (same code as the notebook): seeded GrabCut tongue mask -> two inputs, surroundings (outside the mask
dilated by ~5%) and tongue (mask only), filled with the ImageNet mean colour -> frozen torchvision ResNet-50,
mean embedding over 10 views (FiveCrop at 90% x flip) -> concatenated [surroundings, tongue] -> saved head.
Input photos should be tight, centred tongue crops like the training data (data/preprocessedcropped).

Usage: python predict_tongue.py final_model.joblib IMAGE [IMAGE ...]
Research use only: trained on one photo collection (106 people); not a diagnostic device.
"""
import sys
import cv2
import joblib
import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from torchvision.models import resnet50, ResNet50_Weights

MIN_AREA, MAX_AREA, WORK = 0.20, 0.85, 300
MEAN_RGB = np.array([124, 116, 104], np.uint8)


def circle_mask(h, w):
    yy, xx = np.mgrid[-1:1:h * 1j, -1:1:w * 1j]
    return ((xx ** 2 + yy ** 2) <= 0.85 ** 2).astype(np.uint8)


def tongue_mask(img_bgr):
    h, w = img_bgr.shape[:2]
    small = cv2.resize(img_bgr, (WORK, WORK))
    yy, xx = np.mgrid[-1:1:WORK * 1j, -1:1:WORK * 1j]
    gc = np.full((WORK, WORK), cv2.GC_PR_BGD, np.uint8)
    gc[(xx / 0.8) ** 2 + (yy / 0.9) ** 2 <= 1] = cv2.GC_PR_FGD
    gc[(xx / 0.4) ** 2 + (yy / 0.45) ** 2 <= 1] = cv2.GC_FGD
    b = int(0.03 * WORK)
    gc[:b], gc[-b:], gc[:, :b], gc[:, -b:] = cv2.GC_BGD, cv2.GC_BGD, cv2.GC_BGD, cv2.GC_BGD
    fg = np.zeros((WORK, WORK), np.uint8)
    if (gc == cv2.GC_PR_FGD).any():
        try:
            cv2.setRNGSeed(0)
            cv2.grabCut(small, gc, None, np.zeros((1, 65)), np.zeros((1, 65)), 5, cv2.GC_INIT_WITH_MASK)
            fg = ((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)).astype(np.uint8)
        except cv2.error:
            pass
    n, lab, stats, _ = cv2.connectedComponentsWithStats(fg)
    if n > 1:
        fg = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
        holes = fg.copy()
        cv2.floodFill(holes, np.zeros((WORK + 2, WORK + 2), np.uint8), (0, 0), 1)
        fg = fg | (1 - holes)
    if not MIN_AREA <= fg.mean() <= MAX_AREA:
        return circle_mask(h, w)
    return cv2.resize(fg, (w, h), interpolation=cv2.INTER_NEAREST)


def inputs(img_bgr):
    """(surroundings, tongue) RGB PIL images, as the notebook's 'bg' and 'seg' variants."""
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h = rgb.shape[0]
    tongue = tongue_mask(img_bgr)
    k = max(3, int(0.05 * h)) | 1
    surround = 1 - cv2.dilate(tongue, np.ones((k, k), np.uint8))
    return [Image.fromarray(np.where(m[..., None] == 1, rgb, MEAN_RGB).astype(np.uint8)) for m in (surround, tongue)]


def views(img, size=224):
    big = transforms.Resize((round(size / 0.9), round(size / 0.9)), interpolation=transforms.InterpolationMode.BICUBIC)(img)
    out = []
    for c in transforms.FiveCrop(size)(big):
        t = transforms.ToTensor()(c)
        out += [t, torch.flip(t, dims=[2])]
    return out


@torch.no_grad()
def embed(model, img, device):
    norm = transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    return model(torch.stack([norm(v) for v in views(img)]).to(device)).float().mean(0).cpu().numpy()


def main(model_path, images):
    bundle = joblib.load(model_path)
    assert [k[1] for k in bundle['features']] == ['bg', 'seg'], bundle['features']
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    net = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
    net.fc = torch.nn.Identity()
    net.eval().to(device)
    for path in images:
        img = cv2.imread(path)
        if img is None:
            print(f'{path}\tcould not read image')
            continue
        x = np.concatenate([embed(net, im, device) for im in inputs(img)])[None]
        p = float(bundle['clf'].predict_proba(x)[0, 1])
        print(f"{path}\tP(T2D) = {p:.3f}\t{'T2D' if p >= bundle['threshold'] else 'non-T2D'} (threshold {bundle['threshold']:.2f})")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
