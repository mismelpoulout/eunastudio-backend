def analyze_performance(history):
    stats = {}

    for h in history:
        esp = h.get("especialidad")
        if not esp:
            continue

        correctas = h.get("correctas", 0)
        total = h.get("totalPreguntas", 1)

        porcentaje = (correctas / total) * 100
        stats.setdefault(esp, []).append(porcentaje)

    return {
        esp: sum(vals) / len(vals)
        for esp, vals in stats.items()
    }