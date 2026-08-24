"""Interface de linha de comando do sistema de reconhecimento de obras."""

import argparse
import shutil
import uuid
from pathlib import Path

from exlibris import config
from exlibris.application.recognition_service import CatalogRecognitionService


def _copiar_para_acervo(imagem_path: str) -> str:
    origem = Path(imagem_path)
    destino = Path(config.IMAGES_DIR) / f"{uuid.uuid4().hex}{origem.suffix.lower()}"
    shutil.copy2(origem, destino)
    return str(destino)


def cmd_init(args):
    CatalogRecognitionService(db_path=args.db)
    print(f"Banco de dados pronto em: {args.db}")


def cmd_add_obra(args):
    service = CatalogRecognitionService(db_path=args.db)
    obra_id = service.cadastrar_obra(args.titulo, args.autor, args.local, args.editora, args.data)
    print(f"Obra cadastrada com id={obra_id}: {args.titulo}")


def cmd_list_obras(args):
    service = CatalogRecognitionService(db_path=args.db)
    for obra in service.listar_obras():
        print(f"[{obra.id}] {obra.titulo} - {obra.autor or '?'} "
              f"({obra.local or '?'}, {obra.editora or '?'}, {obra.data or '?'})")


def cmd_identify(args):
    service = CatalogRecognitionService(db_path=args.db)
    resultado = service.identificar(args.imagem, tipo=args.tipo, top_k=args.top_k)

    if resultado.novidade:
        print("Nenhuma correspondência confiável encontrada - marca possivelmente nova.")
    else:
        print("Marcas semelhantes encontradas:")
        for vizinho in resultado.vizinhos:
            titulo = vizinho.obra.titulo if vizinho.obra else "(sem obra vinculada)"
            print(
                f"  marca={vizinho.marca_id} tipo={vizinho.tipo} "
                f"score={vizinho.score:.3f} obra={titulo}"
            )

    print("\nObras candidatas (para localizar a obra):")
    if not resultado.obras_candidatas:
        print("  nenhuma")
    for candidata in resultado.obras_candidatas:
        print(f"  score={candidata.score:.3f} -> [{candidata.obra.id}] {candidata.obra.titulo}")

    return resultado


def cmd_add_marca(args):
    service = CatalogRecognitionService(db_path=args.db)

    resultado = service.identificar(args.imagem, tipo=args.tipo, top_k=1)
    caminho_salvo = _copiar_para_acervo(args.imagem)

    confirmado = bool(args.confirmar or args.obra_id)
    marca_id = service.registrar_marca(
        caminho_salvo, args.tipo, embedding=resultado.embedding,
        obra_id=args.obra_id, descricao=args.descricao, confirmado=confirmado,
    )

    if resultado.novidade:
        print(f"Marca nova registrada (id={marca_id}). ", end="")
    else:
        print(f"Marca registrada (id={marca_id}), semelhante a marcas existentes. ", end="")

    if args.obra_id:
        print(f"Vinculada à obra id={args.obra_id}.")
    else:
        print("Sem vínculo com obra ainda - use 'feedback' após identificar a obra correta.")


def cmd_feedback(args):
    service = CatalogRecognitionService(db_path=args.db)
    service.confirmar_vinculo(args.marca_id, args.obra_id)
    print(f"Marca {args.marca_id} vinculada/confirmada à obra {args.obra_id}. "
          f"Protótipo da obra atualizado.")


def construir_parser():
    parser = argparse.ArgumentParser(
        description="Reconhecimento de marcas de proveniência e ex-libris para "
                    "localizar obras catalogadas.")
    parser.add_argument("--db", default=config.DB_PATH, help="Caminho do banco SQLite")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("init", help="Cria/atualiza o esquema do banco de dados")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("add-obra", help="Cadastra uma obra no catálogo")
    p.add_argument("--titulo", required=True)
    p.add_argument("--autor")
    p.add_argument("--local")
    p.add_argument("--editora")
    p.add_argument("--data")
    p.set_defaults(func=cmd_add_obra)

    p = sub.add_parser("list-obras", help="Lista as obras cadastradas")
    p.set_defaults(func=cmd_list_obras)

    p = sub.add_parser("identify", help="Busca marcas/obras parecidas (não grava nada)")
    p.add_argument("--imagem", required=True)
    p.add_argument("--tipo", choices=["ex_libris", "proveniencia", "outro"])
    p.add_argument("--top-k", type=int, default=config.TOP_K_PADRAO)
    p.set_defaults(func=cmd_identify)

    p = sub.add_parser("add-marca", help="Registra uma marca e ensina o sistema")
    p.add_argument("--imagem", required=True)
    p.add_argument("--tipo", required=True, choices=["ex_libris", "proveniencia", "outro"])
    p.add_argument("--obra-id", type=int, help="Vincula diretamente a uma obra já cadastrada")
    p.add_argument("--descricao")
    p.add_argument("--confirmar", action="store_true",
                   help="Marca como confirmada mesmo sem --obra-id (uso avançado)")
    p.set_defaults(func=cmd_add_marca)

    p = sub.add_parser("feedback", help="Confirma/corrige o vínculo de uma marca a uma obra")
    p.add_argument("--marca-id", type=int, required=True)
    p.add_argument("--obra-id", type=int, required=True)
    p.set_defaults(func=cmd_feedback)

    return parser


def main(argv=None):
    parser = construir_parser()
    args = parser.parse_args(argv)
    args.func(args)
