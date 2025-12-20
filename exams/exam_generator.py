import random
from .base_distribution import BASE_DISTRIBUTION
from .performance_analyzer import analyze_performance


def normalize_distribution(dist, target=90):
    total = sum(dist.values())
    factor = target / total

    normalized = {
        esp: max(1, round(qty * factor))
        for esp, qty in dist.items()
    }

    diff = target - sum(normalized.values())
    keys = list(normalized.keys())

    i = 0
    while diff != 0:
        normalized[keys[i % len(keys)]] += 1 if diff > 0 else -1
        diff += -1 if diff > 0 else 1
        i += 1

    return normalized


def adjust_distribution(base, performance):
    adjusted = {}

    for esp, qty in base.items():
        score = performance.get(esp, 70)

        if score < 50:
            factor = 1.3
        elif score < 65:
            factor = 1.15
        else:
            factor = 0.9

        adjusted[esp] = max(1, round(qty * factor))

    return adjusted


def generate_personalized_exam(history, questions_json, total=90):
    base = normalize_distribution(BASE_DISTRIBUTION, total)
    performance = analyze_performance(history)

    adjusted = adjust_distribution(base, performance)
    adjusted = normalize_distribution(adjusted, total)

    exam = []

    for esp, qty in adjusted.items():
        pool = questions_json.get(esp, [])
        if not pool:
            continue

        exam.extend(random.sample(pool, min(qty, len(pool))))

    random.shuffle(exam)
    return exam[:total]