"""Índice vetorial em memória para busca por similaridade entre marcas.

Tenta usar FAISS (rápido, escala bem) e cai para busca por força bruta em
NumPy caso a biblioteca não esteja instalada — o suficiente para acervos de
até algumas dezenas de milhares de marcas.

O índice é reconstruído a partir do banco de dados na inicialização e
atualizado incrementalmente (`adicionar`) a cada nova marca confirmada, sem
nunca precisar recalcular os vetores já existentes.
"""

import numpy as np

try:
    import faiss  # type: ignore
    _TEM_FAISS = True
except ImportError:
    _TEM_FAISS = False


class IndiceVetorial:
    def __init__(self, dimensao: int):
        self.dimensao = dimensao
        self._ids = []  # posição -> marca_id
        if _TEM_FAISS:
            self._indice = faiss.IndexFlatIP(dimensao)
        else:
            self._matriz = np.empty((0, dimensao), dtype=np.float32)

    def __len__(self):
        return len(self._ids)

    def adicionar(self, marca_id: int, embedding: np.ndarray) -> None:
        vetor = np.asarray(embedding, dtype=np.float32).reshape(1, -1)
        if _TEM_FAISS:
            self._indice.add(vetor)
        else:
            self._matriz = np.vstack([self._matriz, vetor])
        self._ids.append(marca_id)

    def buscar(self, embedding: np.ndarray, top_k: int = 5):
        """Retorna lista de (marca_id, score_similaridade) ordenada decrescente."""
        if len(self._ids) == 0:
            return []

        vetor = np.asarray(embedding, dtype=np.float32).reshape(1, -1)
        top_k = min(top_k, len(self._ids))

        if _TEM_FAISS:
            scores, posicoes = self._indice.search(vetor, top_k)
            scores, posicoes = scores[0], posicoes[0]
        else:
            # embeddings já normalizados -> produto interno == cosseno
            similaridades = (self._matriz @ vetor.T).ravel()
            posicoes = np.argsort(-similaridades)[:top_k]
            scores = similaridades[posicoes]

        resultados = []
        for pos, score in zip(posicoes, scores):
            if pos < 0:
                continue
            resultados.append((self._ids[pos], float(score)))
        return resultados

    @classmethod
    def construir_a_partir_do_banco(cls, marcas: list, dimensao: int) -> "IndiceVetorial":
        indice = cls(dimensao)
        for marca in marcas:
            indice.adicionar(marca["id"], marca["embedding"])
        return indice
