"""Orquestração do reconhecimento: identifica marcas e localiza a obra.

Estratégia de aprendizado contínuo (retrieval-based continual learning):

1. Memória vetorial (vector_index.IndiceVetorial) — cada marca confirmada
   vira um novo ponto de referência. Buscar = comparar a nova imagem contra
   tudo que já foi visto. Adicionar conhecimento é O(1): não há retreino.

2. Protótipos por obra (self._prototipos) — a média (normalizada) dos
   embeddings de todas as marcas confirmadas de uma mesma obra. Funciona
   como um classificador incremental: `partial_fit` natural, pois basta
   atualizar a média a cada novo exemplo. Combina com a busca por vizinhos
   mais próximos para decidir a que obra uma marca pertence, mesmo quando
   ela é uma variação (selo desbotado, ex-libris com dano) de algo já visto.

3. Limiar de novidade (config.SIMILARITY_THRESHOLD) — abaixo dele a marca é
   tratada como desconhecida e fica pendente de curadoria humana
   (`confirmado = 0`), disparando o fluxo de rotulagem antes de entrar
   definitivamente na memória. Isso evita que ruído ou falsos-positivos
   contaminem o aprendizado (aprendizado ativo / human-in-the-loop).
"""

from collections import defaultdict

import numpy as np

import config
import database
import feature_extractor


class ObraRecognizer:
    def __init__(self, db_path: str = config.DB_PATH,
                 dimensao: int = config.EMBEDDING_DIM,
                 limiar_similaridade: float = config.SIMILARITY_THRESHOLD):
        self.db_path = db_path
        self.limiar = limiar_similaridade
        database.iniciar_banco(db_path)

        self._marcas_por_id = {}
        self._prototipos = defaultdict(lambda: np.zeros(dimensao, dtype=np.float32))
        self._contagem_prototipo = defaultdict(int)

        from vector_index import IndiceVetorial

        marcas = database.listar_marcas(db_path)
        self._indice = IndiceVetorial.construir_a_partir_do_banco(marcas, dimensao)
        for marca in marcas:
            self._marcas_por_id[marca["id"]] = marca
            if marca["obra_id"] and marca["confirmado"]:
                self._atualizar_prototipo(marca["obra_id"], marca["embedding"])

    # ------------------------------------------------------------- utils --

    def _atualizar_prototipo(self, obra_id: int, embedding: np.ndarray) -> None:
        n = self._contagem_prototipo[obra_id]
        media_atual = self._prototipos[obra_id]
        nova_media = (media_atual * n + embedding) / (n + 1)
        norma = np.linalg.norm(nova_media)
        self._prototipos[obra_id] = nova_media / norma if norma > 0 else nova_media
        self._contagem_prototipo[obra_id] += 1

    def _pontuar_obras_candidatas(self, embedding: np.ndarray, vizinhos: list) -> dict:
        """Combina o score dos vizinhos mais próximos com o score de protótipo."""
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

    # ---------------------------------------------------------------- API --

    def cadastrar_obra(self, titulo, autor=None, local=None, editora=None, data=None) -> int:
        return database.inserir_obra(titulo, autor, local, editora, data, self.db_path)

    def identificar(self, imagem_path: str, tipo: str = None, top_k: int = config.TOP_K_PADRAO):
        """Busca marcas/obras conhecidas parecidas com a imagem, sem gravar nada.

        Retorna dict com:
          - embedding: vetor extraído (útil para depois chamar registrar_marca)
          - vizinhos: [{marca_id, obra, tipo, score}]
          - obras_candidatas: [{obra, score}] ordenado por score
          - novidade: bool — True se nada supera o limiar de similaridade
        """
        embedding = feature_extractor.extrair_embedding(imagem_path)
        vizinhos_brutos = self._indice.buscar(embedding, top_k=top_k)

        vizinhos = []
        for marca_id, score in vizinhos_brutos:
            marca = self._marcas_por_id[marca_id]
            obra = database.buscar_obra(marca["obra_id"], self.db_path) if marca["obra_id"] else None
            vizinhos.append({
                "marca_id": marca_id,
                "tipo": marca["tipo"],
                "obra": obra,
                "score": score,
            })

        pontos_obras = self._pontuar_obras_candidatas(embedding, vizinhos_brutos)
        obras_candidatas = sorted(
            (
                {"obra": database.buscar_obra(obra_id, self.db_path), "score": score}
                for obra_id, score in pontos_obras.items()
            ),
            key=lambda x: -x["score"],
        )

        melhor_score = vizinhos[0]["score"] if vizinhos else 0.0
        novidade = melhor_score < self.limiar

        melhor_marca_id = vizinhos[0]["marca_id"] if vizinhos else None
        melhor_obra_id = obras_candidatas[0]["obra"]["id"] if obras_candidatas else None
        database.registrar_identificacao(
            imagem_path, melhor_marca_id, melhor_obra_id, melhor_score, self.db_path
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
        """Passo de aprendizado: incorpora uma marca (nova ou confirmada) à memória.

        Se `embedding` não for passado, é extraído da imagem agora. Chamar
        isso é o que efetivamente "ensina" o sistema — a marca passa a
        contar nas próximas buscas e, se `obra_id` e `confirmado=True`,
        também atualiza o protótipo incremental daquela obra.
        """
        if embedding is None:
            embedding = feature_extractor.extrair_embedding(imagem_path)

        marca_id = database.inserir_marca(
            imagem_path, embedding, tipo, obra_id, descricao, confirmado, self.db_path
        )
        self._marcas_por_id[marca_id] = database.buscar_marca(marca_id, self.db_path)
        self._marcas_por_id[marca_id]["embedding"] = np.asarray(embedding, dtype=np.float32)
        self._indice.adicionar(marca_id, embedding)

        if obra_id and confirmado:
            self._atualizar_prototipo(obra_id, np.asarray(embedding, dtype=np.float32))

        return marca_id

    def confirmar_vinculo(self, marca_id: int, obra_id: int) -> None:
        """Curadoria humana: liga (ou corrige) o vínculo de uma marca a uma obra.

        Isso reforça o aprendizado — a marca passa a contribuir para o
        protótipo da obra correta a partir de agora.
        """
        database.atualizar_vinculo_marca(marca_id, obra_id, confirmado=True, db_path=self.db_path)
        marca = database.buscar_marca(marca_id, self.db_path)
        embedding = np.frombuffer(marca["embedding"], dtype=np.float32)
        self._marcas_por_id[marca_id]["obra_id"] = obra_id
        self._marcas_por_id[marca_id]["confirmado"] = 1
        self._atualizar_prototipo(obra_id, embedding)
