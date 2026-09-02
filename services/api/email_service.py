from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"
SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def _send_via_resend(to_email: str, subject: str, html_body: str) -> None:
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY no configurada")

    payload = json.dumps(
        {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        RESEND_API_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status >= 300:
            raise RuntimeError(f"Resend respondio con status {response.status}")


def _send_via_sendgrid(to_email: str, subject: str, html_body: str) -> None:
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL")
    if not api_key or not from_email:
        raise RuntimeError("SENDGRID_API_KEY o SENDGRID_FROM_EMAIL no configuradas")

    payload = json.dumps(
        {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_body}],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        SENDGRID_API_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status >= 300:
            raise RuntimeError(f"SendGrid respondio con status {response.status}")


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """Envia el correo de recuperacion. Devuelve False si no se pudo enviar (sin filtrar el error al cliente)."""
    provider = os.getenv("EMAIL_PROVIDER", "").strip().lower()
    subject = "Recupera tu contraseña - Brasaland"
    html_body = (
        "<p>Recibimos una solicitud para restablecer tu contraseña.</p>"
        f'<p><a href="{reset_link}">Haz click aquí para crear una nueva contraseña</a></p>'
        "<p>Este enlace expira en 15 minutos. Si no solicitaste este cambio, ignora este mensaje.</p>"
    )

    try:
        if provider == "resend":
            _send_via_resend(to_email, subject, html_body)
        elif provider == "sendgrid":
            _send_via_sendgrid(to_email, subject, html_body)
        else:
            logger.warning(
                "EMAIL_PROVIDER no configurado; no se envio email real. Enlace de recuperacion: %s", reset_link
            )
            return False
    except (urllib.error.URLError, RuntimeError) as error:
        logger.error("No se pudo enviar el email de recuperacion: %s", error)
        return False

    return True
