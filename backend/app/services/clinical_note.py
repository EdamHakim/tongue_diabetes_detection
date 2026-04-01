from __future__ import annotations


def make_clinical_note(*, risk_band: str, probability_diabetes: float) -> str:
    pct = round(probability_diabetes * 100.0, 1)
    if risk_band == "low":
        return (
            f"Tongue image analysis suggests low likelihood of T2DM-related features (est. risk {pct}%). "
            "This tool is a screening aid only; consider clinical context and confirmatory testing if indicated."
        )
    if risk_band == "moderate":
        return (
            f"Tongue image analysis suggests moderate likelihood of T2DM-related features (est. risk {pct}%). "
            "Recommend clinical correlation and consider confirmatory testing (e.g., fasting glucose, HbA1c)."
        )
    return (
        f"Tongue image analysis suggests high likelihood of T2DM-related features (est. risk {pct}%). "
        "Recommend prompt clinical evaluation and confirmatory testing."
    )


def confidence_pct(probability_diabetes: float) -> float:
    # Treat probability as model confidence around the predicted class.
    p = float(probability_diabetes)
    c = p if p >= 0.5 else (1.0 - p)
    return round(c * 100.0, 1)

