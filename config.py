"""Configurações globais do sistema de reconhecimento de obras."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "marcas")
DB_PATH = os.path.join(DATA_DIR, "catalogo.db")

os.makedirs(IMAGES_DIR, exist_ok=True)

# Dimensão do vetor de embedding gerado pelo backbone (ResNet50 sem a camada
# de classificação final -> saída do global average pooling).
EMBEDDING_DIM = 2048

# Similaridade de cosseno mínima para considerar uma marca como "já
# conhecida". Abaixo disso a marca é tratada como novidade e aguarda
# curadoria humana antes de entrar de vez na base.
SIMILARITY_THRESHOLD = 0.75

# Número de vizinhos mais próximos retornados nas buscas.
TOP_K_PADRAO = 5

DEVICE = os.environ.get("RECONHECIMENTO_DEVICE", "auto")
