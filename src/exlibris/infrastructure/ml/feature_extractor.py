"""Extração de embeddings visuais para marcas de proveniência e ex-libris."""

import threading

import numpy as np
from PIL import Image, UnidentifiedImageError

from exlibris import config
from exlibris.domain.errors import ImagemInvalida

_lock = threading.Lock()
_modelo = None
_transform = None
_device = None


def _resolver_device():
    import torch

    if config.DEVICE != "auto":
        return torch.device(config.DEVICE)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _carregar_modelo():
    """Carrega o backbone sob demanda (lazy) e o mantém em cache no processo."""
    global _modelo, _transform, _device
    with _lock:
        if _modelo is not None:
            return
        import torch
        from torchvision.models import ResNet50_Weights, resnet50

        weights = ResNet50_Weights.IMAGENET1K_V2
        modelo = resnet50(weights=weights)
        modelo.fc = torch.nn.Identity()
        modelo.eval()

        _device = _resolver_device()
        modelo.to(_device)

        _modelo = modelo
        _transform = weights.transforms()


def extrair_embedding(imagem_path: str) -> np.ndarray:
    """Retorna o embedding L2-normalizado (float32, shape=(EMBEDDING_DIM,))."""
    import torch

    # Valida a imagem antes de carregar o modelo (evita baixar pesos/gastar
    # inferência para depois descobrir que a entrada é inválida).
    try:
        with Image.open(imagem_path) as img:
            imagem_rgb = img.convert("RGB")
    except (FileNotFoundError, UnidentifiedImageError, OSError) as erro:
        raise ImagemInvalida(
            f"Não foi possível ler a imagem em {imagem_path!r}."
        ) from erro

    _carregar_modelo()
    tensor = _transform(imagem_rgb).unsqueeze(0).to(_device)

    with torch.no_grad():
        vetor = _modelo(tensor).squeeze(0).cpu().numpy().astype(np.float32)

    norma = np.linalg.norm(vetor)
    if norma > 0:
        vetor = vetor / norma
    return vetor
