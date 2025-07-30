import requests
from django.conf import settings


def enviar_mensagem_whatsapp(numero: str, texto: str, instancia: str):
    url = f"{settings.EVOLUTION_API_URL}/message/sendText/{instancia}"
    print(url)
    payload = {
        "number": numero,
        "text": texto
    }

    headers = {
        "apikey": settings.EVOLUTION_API_TOKEN
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.status_code, response.json()
