"""Serviço de aplicação para reconhecimento e catalogação de obras."""

from collections import defaultdict

import numpy as np

from exlibris import config
from exlibris.infrastructure.ml.feature_extractor import extrair_embedding
from exlibris.infrastructure.persistence.sqlite_catalog import SQLiteCatalogRepository
from exlibris.infrastructure.search.vector_index import IndiceVetorial


class ObraRecognizer:
    def __init__(self, db_path: str = config.DB_PATH,
                 dimensao: int = config.EMBEDDING_DIM,
                 limiar_similaridade: float = config.SIMILARITY_THRESHOLD):
        self.db_path = db_path
        self.limiar = limiar_similaridade
        self._repository = SQLiteCatalogRepository(db_path)
        self._repository.iniciar_banco()

        self._marcas_por_id = {}
        self._prototipos = defaultdict(lambda: np.zeros(dimensao, dtype=np.float32))
        self._contagem_prototipo = defaultdict(int)

        marcas = self._repository.listar_marcas()
        self._indice = IndiceVetorial.construir_a_partir_do_banco(marcas, dimensao)
        for marca in marcas:
            self._marcas_por_id[marca["id"]] = marca
            if marca["obra_id"] and marca["confirmado"]:
                self._atualizar_prototipo(marca["obra_id"], marca["embedding"])

    def _atualizar_prototipo(self, obra_id: int, embedding: np.ndarray) -> None:
        n = self._contagem_prototipo[obra_id]
        media_atual = self._prototipos[obra_id]
        nova_media = (media_atual * n + embedding) / (n + 1)
        norma = np.linalg.norm(nova_media)
        self._prototipos[obra_id] = nova_media / norma if norma > 0 else nova_media
        self._contagem_prototipo[obra_id] += 1

    def _pontuar_obras_candidatas(self, embedding: np.ndarray, vizinhos: list) -> dict:
        pontos = defaultdict(float)
        for marca_id, score in vizinhos:
            marca = self._marcas_por_id[marca_id]
            if marca["obra_id"]:
                pontos[marca["obra_id"]] = max(pontos[marca["obra_id"]], score)

        for obra_id, prototipo in self._prototipos.items():
            score_prototipo = float(np.dot(prototipo, embedding))
            if obra_id in pontos:
                pontos[obra_id] = 0.5 * pontos[obra_id] + 0.5 * score_prototipo
            elif score_prototipo >= self.limiar:
                pontos[obra_id] = score_prototipo

        return pontos

    def cadastrar_obra(self, titulo, autor=None, local=None, editora=None, data=None) -> int:
        return self._repository.inserir_obra(titulo, autor, local, editora, data)

    def listar_obras(self):
        return self._repository.listar_obras()

    def identificar(self, imagem_path: str, tipo: str = None, top_k: int = config.TOP_K_PADRAO):
        embedding = extrair_embedding(imagem_path)
        vizinhos_brutos = self._indice.buscar(embedding, top_k=top_k)

        vizinhos = []
        for marca_id, score in vizinhos_brutos:
            marca = self._marcas_por_id[marca_id]
            obra = self._repository.buscar_obra(marca["obra_id"]) if marca["obra_id"] else None
            vizinhos.append({
                "marca_id": marca_id,
                "tipo": marca["tipo"],
                "obra": obra,
                "score": score,
            })

        pontos_obras = self._pontuar_obras_candidatas(embedding, vizinhos_brutos)
        obras_candidatas = sorted(
            (
                {"obra": self._repository.buscar_obra(obra_id), "score": score}
                for obra_id, score in pontos_obras.items()
            ),
            key=lambda x: -x["score"],
        )

        melhor_score = vizinhos[0]["score"] if vizinhos else 0.0
        novidade = melhor_score < self.limiar

        melhor_marca_id = vizinhos[0]["marca_id"] if vizinhos else None
        melhor_obra_id = obras_candidatas[0]["obra"]["id"] if obras_candidatas else None
        self._repository.registrar_identificacao(
            imagem_path, melhor_marca_id, melhor_obra_id, melhor_score
        )

        return {
            "embedding": embedding,
            "vizinhos": vizinhos,
            "obras_candidatas": obras_candidatas,
            "novidade": novidade,
            "tipo_consultado": tipo,
        }

    def registrar_marca(self, imagem_path: str, tipo: str, embedding: np.ndarray = None,
                        obra_id: int = None, descricao: str = None,
                        confirmado: bool = False) -> int:
        if embedding is None:
            embedding = extrair_embedding(imagem_path)

        marca_id = self._repository.inserir_marca(
            imagem_path, embedding, tipo, obra_id, descricao, confirmado
        )
        self._marcas_por_id[marca_id] = self._repository.buscar_marca(marca_id)
        self._marcas_por_id[marca_id]["embedding"] = np.asarray(embedding, dtype=np.float32)
        self._indice.adicionar(marca_id, embedding)

        if obra_id and confirmado:
            self._atualizar_prototipo(obra_id, np.asarray(embedding, dtype=np.float32))

        return marca_id

    def confirmar_vinculo(self, marca_id: int, obra_id: int) -> None:
        self._repository.atualizar_vinculo_marca(marca_id, obra_id, confirmado=True)
        marca = self._repository.buscar_marca(marca_id)
        embedding = np.frombuffer(marca["embedding"], dtype=np.float32)
        self._marcas_por_id[marca_id]["obra_id"] = obra_id
        self._marcas_por_id[marca_id]["confirmado"] = 1
        self._atualizar_prototipo(obra_id, embedding)
