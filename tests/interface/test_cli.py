"""Testes da CLI: cobertura unitária contra uma camada de aplicação fake,
mais um pequeno smoke test de ponta a ponta do caminho feliz.

O smoke test usa `CatalogRecognitionService` real (SQLite temporário real,
índice vetorial real) e substitui apenas o extrator de embeddings por um
fake — sem GPU nem download de pesos, como pedem os critérios do CI.
"""

from dataclasses import dataclass, field

import numpy as np
import pytest

from exlibris import config
from exlibris.application.recognition_service import CatalogRecognitionService
from exlibris.domain.models import MarcaVizinha, ObraCandidata, Obra, ResultadoIdentificacao
from exlibris.interface import cli


@dataclass
class FakeService:
    """Stub da camada de aplicação usado para testar apenas o wiring da CLI
    (parsing de argumentos, formatação de saída), sem SQLite nem ML real."""

    db_path: str
    obras: list = field(default_factory=list)
    resultado_identificar: ResultadoIdentificacao | None = None
    chamadas: list = field(default_factory=list)
    proximo_marca_id: int = 1

    def cadastrar_obra(self, titulo, autor=None, local=None, editora=None, data=None):
        self.chamadas.append(("cadastrar_obra", titulo, autor, local, editora, data))
        return 42

    def listar_obras(self):
        self.chamadas.append(("listar_obras",))
        return self.obras

    def identificar(self, imagem_path, tipo=None, top_k=5):
        self.chamadas.append(("identificar", imagem_path, tipo, top_k))
        return self.resultado_identificar

    def registrar_marca(self, imagem_path, tipo, embedding=None, obra_id=None,
                         descricao=None, confirmado=False):
        self.chamadas.append(
            ("registrar_marca", imagem_path, tipo, obra_id, descricao, confirmado)
        )
        marca_id = self.proximo_marca_id
        self.proximo_marca_id += 1
        return marca_id

    def confirmar_vinculo(self, marca_id, obra_id):
        self.chamadas.append(("confirmar_vinculo", marca_id, obra_id))


class FakeServiceFactory:
    """Substitui `cli.CatalogRecognitionService`. Cada chamada devolve um novo
    `FakeService`, pré-configurado com o que o teste ajustar em `config` antes
    de invocar `cli.main(...)`, e guardado em `instancias` para inspeção."""

    def __init__(self):
        self.config: dict = {"obras": [], "resultado_identificar": None}
        self.instancias: list[FakeService] = []

    def __call__(self, db_path: str) -> FakeService:
        service = FakeService(
            db_path=db_path,
            obras=self.config["obras"],
            resultado_identificar=self.config["resultado_identificar"],
        )
        self.instancias.append(service)
        return service

    @property
    def ultima(self) -> FakeService:
        return self.instancias[-1]


@pytest.fixture
def fake_service(monkeypatch) -> FakeServiceFactory:
    factory = FakeServiceFactory()
    monkeypatch.setattr(cli, "CatalogRecognitionService", factory)
    return factory


@pytest.fixture(autouse=True)
def isolar_acervo_de_imagens(tmp_path, monkeypatch):
    # `cmd_add_marca` chama `_copiar_para_acervo`, que grava em
    # `config.IMAGES_DIR` (fixo no módulo de config), independentemente do
    # `--db` informado ou de o serviço estar faked. Sem isolar isso aqui,
    # qualquer teste de `add-marca` gravaria arquivos reais em
    # `data/marcas` do repositório.
    acervo_dir = tmp_path / "marcas"
    acervo_dir.mkdir()
    monkeypatch.setattr(config, "IMAGES_DIR", str(acervo_dir))


def _resultado_vazio(tipo=None) -> ResultadoIdentificacao:
    return ResultadoIdentificacao(
        embedding=np.zeros(3, dtype=np.float32), vizinhos=[], obras_candidatas=[],
        novidade=True, tipo_consultado=tipo,
    )


# --- wiring de cada subcomando ----------------------------------------------------

def test_cmd_init_cria_servico_com_o_db_informado(fake_service):
    cli.main(["--db", "banco.db", "init"])

    assert fake_service.ultima.db_path == "banco.db"


def test_cmd_add_obra_repassa_todos_os_campos(fake_service, capsys):
    cli.main([
        "add-obra", "--titulo", "Os Lusíadas", "--autor", "Camões",
        "--local", "Lisboa", "--editora", "Antônio", "--data", "1572",
    ])

    assert fake_service.ultima.chamadas[0] == (
        "cadastrar_obra", "Os Lusíadas", "Camões", "Lisboa", "Antônio", "1572"
    )
    assert "id=42" in capsys.readouterr().out


def test_cmd_list_obras_imprime_cada_obra(fake_service, capsys):
    fake_service.config["obras"] = [
        Obra(id=1, titulo="Obra", autor="Autor", local="Local",
             editora="Editora", data="2024", criado_em="2024-01-01T00:00:00+00:00")
    ]

    cli.main(["list-obras"])

    saida = capsys.readouterr().out
    assert "Obra" in saida
    assert "Autor" in saida


def test_cmd_identify_imprime_novidade_quando_sem_correspondencia(fake_service, capsys):
    fake_service.config["resultado_identificar"] = _resultado_vazio()

    cli.main(["identify", "--imagem", "foto.jpg", "--tipo", "ex_libris"])

    assert "possivelmente nova" in capsys.readouterr().out


def test_cmd_identify_imprime_vizinhos_quando_ha_correspondencia(fake_service, capsys):
    obra = Obra(id=1, titulo="Obra Encontrada", autor=None, local=None,
                editora=None, data=None, criado_em="2024-01-01T00:00:00+00:00")
    fake_service.config["resultado_identificar"] = ResultadoIdentificacao(
        embedding=np.zeros(3, dtype=np.float32),
        vizinhos=[MarcaVizinha(marca_id=1, tipo="ex_libris", obra=obra, score=0.95)],
        obras_candidatas=[ObraCandidata(obra=obra, score=0.95)],
        novidade=False, tipo_consultado="ex_libris",
    )

    cli.main(["identify", "--imagem", "foto.jpg"])

    saida = capsys.readouterr().out
    assert "Obra Encontrada" in saida
    assert "0.950" in saida


def test_cmd_add_marca_confirma_quando_obra_id_informado(fake_service, tmp_path):
    fake_service.config["resultado_identificar"] = _resultado_vazio()
    imagem = tmp_path / "foto.jpg"
    imagem.write_bytes(b"conteudo-fake")

    cli.main(["add-marca", "--imagem", str(imagem), "--tipo", "ex_libris", "--obra-id", "7"])

    chamada = fake_service.ultima.chamadas[-1]
    assert chamada[0] == "registrar_marca"
    assert chamada[3] == 7  # obra_id
    assert chamada[5] is True  # confirmado, forçado por --obra-id


def test_cmd_add_marca_nao_confirma_sem_obra_id_nem_flag(fake_service, tmp_path):
    fake_service.config["resultado_identificar"] = _resultado_vazio()
    imagem = tmp_path / "foto.jpg"
    imagem.write_bytes(b"conteudo-fake")

    cli.main(["add-marca", "--imagem", str(imagem), "--tipo", "outro"])

    assert fake_service.ultima.chamadas[-1][5] is False  # confirmado


def test_cmd_feedback_confirma_vinculo(fake_service, capsys):
    cli.main(["feedback", "--marca-id", "3", "--obra-id", "1"])

    assert fake_service.ultima.chamadas[0] == ("confirmar_vinculo", 3, 1)
    assert "Marca 3" in capsys.readouterr().out


# --- smoke test de ponta a ponta (caminho feliz, sem ML real) -------------------

def test_caminho_feliz_de_ponta_a_ponta_sem_carregar_modelo_real(tmp_path, monkeypatch, capsys):
    embeddings: dict[str, np.ndarray] = {}

    def fake_extrator(imagem_path):
        return embeddings[imagem_path]

    def real_service_factory(db_path):
        return CatalogRecognitionService(db_path=db_path, dimensao=3,
                                          extrator_embedding=fake_extrator)

    monkeypatch.setattr(cli, "CatalogRecognitionService", real_service_factory)

    db_path = str(tmp_path / "catalogo.db")
    imagem_conhecida = tmp_path / "conhecida.jpg"
    imagem_conhecida.write_bytes(b"fake")
    embeddings[str(imagem_conhecida)] = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    cli.main(["--db", db_path, "init"])
    cli.main(["--db", db_path, "add-obra", "--titulo", "Os Lusíadas", "--autor", "Camões"])

    cli.main([
        "--db", db_path, "add-marca", "--imagem", str(imagem_conhecida),
        "--tipo", "ex_libris", "--obra-id", "1",
    ])

    imagem_consulta = tmp_path / "consulta.jpg"
    imagem_consulta.write_bytes(b"fake-consulta")
    embeddings[str(imagem_consulta)] = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    cli.main(["--db", db_path, "identify", "--imagem", str(imagem_consulta)])
    assert "Os Lusíadas" in capsys.readouterr().out

    cli.main(["--db", db_path, "list-obras"])
    assert "Os Lusíadas" in capsys.readouterr().out
