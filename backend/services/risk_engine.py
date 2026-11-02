RISK_LEVELS = {
    1: {
        "label": "Low Risk",
        "color": "#2a8a5f",
        "advice": "Within healthy range.",
        "score": 18,
    },
    2: {
        "label": "Low-Medium Risk",
        "color": "#8fbf4f",
        "advice": "Slightly elevated. Continue normal movement and monitor.",
        "score": 34,
    },
    3: {
        "label": "Moderate Risk",
        "color": "#d9a32a",
        "advice": "Ease off high-impact activity and keep monitoring.",
        "score": 54,
    },
    4: {
        "label": "Elevated Risk",
        "color": "#e08a4a",
        "advice": "Reduce load and avoid aggressive ankle movement.",
        "score": 74,
    },
    5: {
        "label": "High Risk",
        "color": "#d65a4a",
        "advice": "Avoid loading the ankle and consider contacting your physician.",
        "score": 92,
    },
}


OVERALL_LEVELS = {
    "GREEN": {
        "level": 1,
        "score": 18,
        "label": "Healthy",
        "color": "#2a8a5f",
    },
    "GREEN-YELLOW": {
        "level": 2,
        "score": 34,
        "label": "Low-Medium",
        "color": "#8fbf4f",
    },
    "GREEN YELLOW": {
        "level": 2,
        "score": 34,
        "label": "Low-Medium",
        "color": "#8fbf4f",
    },
    "YELLOW": {
        "level": 3,
        "score": 54,
        "label": "Monitor",
        "color": "#d9a32a",
    },
    "ORANGE": {
        "level": 4,
        "score": 74,
        "label": "Elevated",
        "color": "#e08a4a",
    },
    "RED": {
        "level": 5,
        "score": 92,
        "label": "High",
        "color": "#d65a4a",
    },
}


def calculate_risk(max_strain, gradient, variability):
    max_strain = float(max_strain or 0)
    gradient = float(gradient or 0)
    variability = float(variability or 0)

    if max_strain >= 8 or gradient >= 4 or variability >= 1.5:
        level = 5
    elif max_strain >= 6 or gradient >= 3 or variability >= 1.0:
        level = 4
    elif max_strain >= 4 or gradient >= 2 or variability >= 0.5:
        level = 3
    elif max_strain >= 2 or gradient >= 1 or variability >= 0.25:
        level = 2
    else:
        level = 1

    return {"level": level, **RISK_LEVELS[level]}


def _label_for_score(score):
    if score >= 85:
        return {"level": 5, "label": "High", "color": RISK_LEVELS[5]["color"]}
    if score >= 65:
        return {"level": 4, "label": "Elevated", "color": RISK_LEVELS[4]["color"]}
    if score >= 45:
        return {"level": 3, "label": "Monitor", "color": RISK_LEVELS[3]["color"]}
    if score >= 25:
        return {"level": 2, "label": "Low-Medium", "color": RISK_LEVELS[2]["color"]}
    return {"level": 1, "label": "Healthy", "color": RISK_LEVELS[1]["color"]}


def calculate_overall(ligaments, overall_value=None):
    if overall_value is not None:
        try:
            score = round(float(overall_value))
            score = max(0, min(100, score))
            return {"score": score, "source": overall_value, **_label_for_score(score)}
        except (TypeError, ValueError):
            key = str(overall_value).strip().upper()
            if key in OVERALL_LEVELS:
                return {"source": overall_value, **OVERALL_LEVELS[key]}

    if not ligaments:
        return {
            "level": 1,
            "score": 0,
            "label": "Healthy",
            "color": RISK_LEVELS[1]["color"],
            "source": overall_value,
        }

    levels = [item["risk"]["level"] for item in ligaments.values()]
    scores = [item["risk"]["score"] for item in ligaments.values()]
    level = max(levels)
    score = round(max(scores) * 0.6 + (sum(scores) / len(scores)) * 0.4)

    if level <= 2:
        label = "Healthy"
    elif level == 3:
        label = "Monitor"
    elif level == 4:
        label = "Elevated"
    else:
        label = "High"

    return {
        "level": level,
        "score": score,
        "label": label,
        "color": RISK_LEVELS[level]["color"],
        "source": overall_value,
    }
