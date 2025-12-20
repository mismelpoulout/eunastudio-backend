def send_plan_warning_email(email: str, hours_left: int):
    subject = "⚠️ Tu plan está por vencer"
    body = f"""
    Hola 👋

    Tu plan vencerá en aproximadamente {hours_left} horas.

    Para evitar el bloqueo del acceso, renueva tu plan desde la plataforma.

    👉 https://eunastudio.cl/suscripciones
    """

    send_email(
        to=email,
        subject=subject,
        body=body
    )