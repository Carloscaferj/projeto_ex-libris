"""Extração de embeddings visuais para marcas de proveniência e ex-libris.

Usamos uma ResNet-50 pré-treinada (ImageNet) como backbone congelado: a
camada final de classificação é removida e ficamos com o vetor de 2048
dimensões produzido pelo global average pooling. Esse vetor captura textura,
forma e composição gráfica — suficiente para comparar selos, carimbos,
brasões e gravuras de ex-libris por similaridade, sem precisar de milhares
de exemplos rotulados para treinar uma rede do zero.

O "aprendizado a cada leitura" não acontece por back-propagation nesse
backbone (isso exigiria retreinar a rede inteira a cada imagem, o que é
inviável e arriscado). Em vez disso, o aprendizado incremental acontece na
camada seguinte: o índice vetorial (vector_index.py) e os protótipos por
obra (recognizer.py), que crescem e se refinam a cada novo exemplo
confirmado — uma estratégia de aprendizado por memória (retrieval-based
continual learning), robusta e sem esquecimento catastrófico.
"""

import threading

import numpy as np
from PIL import Image

import config

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
        modelo.fc = torch.nn.Identity()  # remove a camada de classificação
        modelo.eval()

        _device = _resolver_device()
        modelo.to(_device)

        _modelo = modelo
        _transform = weights.transforms()


def extrair_embedding(imagem_path: str) -> np.ndarray:
    """Retorna o embedding L2-normalizado (float32, shape=(EMBEDDING_DIM,))."""
    import torch

    _carregar_modelo()

    with Image.open(imagem_path) as img:
        img = img.convert("RGB")
        tensor = _transform(img).unsqueeze(0).to(_device)

    with torch.no_grad():
        vetor = _modelo(tensor).squeeze(0).cpu().numpy().astype(np.float32)

    norma = np.linalg.norm(vetor)
    if norma > 0:
        vetor = vetor / norma
    return vetor
