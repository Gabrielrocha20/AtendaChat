import base64
import os

import requests
from django.conf import settings


def criar_instancia_evolution(instance_name: str, integration: str = "WHATSAPP-BAILEYS"):
    url = f"{settings.EVOLUTION_API_URL}/instance/create"
    headers = {
        "apikey": settings.EVOLUTION_API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "instanceName": instance_name,
        "qrcode": True,
        "integration": integration,
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def salvar_qrcode_base64(base64_str: str, instance_name: str) -> str:
    # Remove o prefixo "data:image/png;base64," se existir
    if base64_str.startswith("data:image"):
        base64_str = base64_str.split(",")[1]

    # Decodifica o base64
    imagem = base64.b64decode(base64_str)

    # Define o caminho para salvar a imagem
    pasta = os.path.join(settings.MEDIA_ROOT, 'qrcode')
    os.makedirs(pasta, exist_ok=True)

    caminho_arquivo = os.path.join(pasta, f"{instance_name}.png")

    # Salva a imagem
    with open(caminho_arquivo, "wb") as f:
        f.write(imagem)

    # Retorna o caminho relativo (usado por ImageField ou links)
    return f"qrcode/{instance_name}.png"