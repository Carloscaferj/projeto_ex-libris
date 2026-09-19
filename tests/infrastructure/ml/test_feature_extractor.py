"""Smoke test do extrator de embeddings.

Marcado como `slow`: carrega o backbone ResNet-50 real (baixa pesos do
ImageNet na primeira execução) e roda inferência de verdade. Não faz parte
do "pytest -m 'not slow'" rodado no CI (sem GPU nem download de pesos) —
é para rodar manualmente quando o ambiente já tem os pesos em cache.
"""

import numpy as np
import pytest
from PIL import Image

from exlibris.infrastructure.ml.feature_extractor import extrair_embedding


@pytest.mark.slow
def test_extrair_embedding_retorna_vetor_l2_normalizado(tmp_path):
    imagem_path = tmp_path / "marca.png"
    Image.new("RGB", (64, 64), color=(120, 60, 200)).save(imagem_path)

    embedding = extrair_embedding(str(imagem_path))

    assert embedding.dtype == np.float32
    assert embedding.shape == (2048,)
    assert np.linalg.norm(embedding) == pytest.approx(1.0, abs=1e-3)
