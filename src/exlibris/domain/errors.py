"""Taxonomia estável de erros dos casos de uso.

Estas classes são o único contrato de erro que a camada de aplicação expõe
para as interfaces (CLI hoje, HTTP no futuro). Cada uma carrega um
``codigo`` estável — pensado para virar código de saída de processo ou
status HTTP — e mensagens que nunca vazam detalhes de SQLite, Pillow ou
outra infraestrutura para quem consome o caso de uso.
"""


class ExLibrisError(Exception):
    """Erro base de negócio do Ex Libris."""

    codigo = "erro_interno"


class ErroValidacao(ExLibrisError):
    """Entrada rejeitada antes de qualquer efeito colateral."""

    codigo = "validacao"


class TituloInvalido(ErroValidacao):
    pass


class TipoMarcaInvalido(ErroValidacao):
    pass


class TopKInvalido(ErroValidacao):
    pass


class EmbeddingInvalido(ErroValidacao):
    pass


class VinculoInvalido(ErroValidacao):
    pass


class ImagemInvalida(ErroValidacao):
    pass


class ErroNaoEncontrado(ExLibrisError):
    """Referência a um identificador que não existe no catálogo."""

    codigo = "nao_encontrado"


class ObraNaoEncontrada(ErroNaoEncontrado):
    pass


class MarcaNaoEncontrada(ErroNaoEncontrado):
    pass


class ErroConflito(ExLibrisError):
    """O estado atual do catálogo impede a operação solicitada."""

    codigo = "conflito"


class ErroInfraestrutura(ExLibrisError):
    """Falha ao acessar SQLite, o modelo de ML ou o sistema de arquivos."""

    codigo = "infraestrutura"
