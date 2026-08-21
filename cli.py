"""Interface de linha de comando do sistema de reconhecimento de obras.

Exemplos:

    python main.py init

    python main.py add-obra --titulo "Os Lusíadas" --autor "Luís de Camões" \\
        --local "Lisboa" --editora "Antônio Gonçalves" --data "1572"

    python main.py identify --imagem caminho/marca.jpg --tipo ex_libris

    python main.py add-marca --imagem caminho/marca.jpg --tipo ex_libris \\
        --obra-id 1 --confirmar

    python main.py feedback --marca-id 3 --obra-id 1

    python main.py list-obras
"""

import argparse
import shutil
import uuid
from pathlib import Path

import config
from recognizer import ObraRecognizer


def _copiar_para_acervo(imagem_path: str) -> str:
    origem = Path(imagem_path)
    destino = Path(config.IMAGES_DIR) / f"{uuid.uuid4().hex}{origem.suffix.lower()}"
    shutil.copy2(origem, destino)
    return str(destino)


def cmd_init(args):
    ObraRecognizer(db_path=args.db)
    print(f"Banco de dados pronto em: {args.db}")


def cmd_add_obra(args):
    r = ObraRecognizer(db_path=args.db)
    obra_id = r.cadastrar_obra(args.titulo, args.autor, args.local, args.editora, args.data)
    print(f"Obra cadastrada com id={obra_id}: {args.titulo}")


def cmd_list_obras(args):
    from database import listar_obras

    for obra in listar_obras(args.db):
        print(f"[{obra['id']}] {obra['titulo']} — {obra['autor'] or '?'} "
              f"({obra['local'] or '?'}, {obra['editora'] or '?'}, {obra['data'] or '?'})")


def cmd_identify(args):
    r = ObraRecognizer(db_path=args.db)
    resultado = r.identificar(args.imagem, tipo=args.tipo, top_k=args.top_k)

    if resultado["novidade"]:
        print("Nenhuma correspondência confiável encontrada — marca possivelmente nova.")
    else:
        print("Marcas semelhantes encontradas:")
        for v in resultado["vizinhos"]:
            titulo = v["obra"]["titulo"] if v["obra"] else "(sem obra vinculada)"
            print(f"  marca={v['marca_id']} tipo={v['tipo']} score={v['score']:.3f} obra={titulo}")

    print("\nObras candidatas (para localizar a obra):")
    if not resultado["obras_candidatas"]:
        print("  nenhuma")
    for c in resultado["obras_candidatas"]:
        print(f"  score={c['score']:.3f} -> [{c['obra']['id']}] {c['obra']['titulo']}")

    return resultado


def cmd_add_marca(args):
    r = ObraRecognizer(db_path=args.db)

    resultado = r.identificar(args.imagem, tipo=args.tipo, top_k=1)
    caminho_salvo = _copiar_para_acervo(args.imagem)

    confirmado = bool(args.confirmar or args.obra_id)
    marca_id = r.registrar_marca(
        caminho_salvo, args.tipo, embedding=resultado["embedding"],
        obra_id=args.obra_id, descricao=args.descricao, confirmado=confirmado,
    )

    if resultado["novidade"]:
        print(f"Marca nova registrada (id={marca_id}). ", end="")
    else:
        print(f"Marca registrada (id={marca_id}), semelhante a marcas existentes. ", end="")

    if args.obra_id:
        print(f"Vinculada à obra id={args.obra_id}.")
    else:
        print("Sem vínculo com obra ainda — use 'feedback' após identificar a obra correta.")


def cmd_feedback(args):
    r = ObraRecognizer(db_path=args.db)
    r.confirmar_vinculo(args.marca_id, args.obra_id)
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


if __name__ == "__main__":
    main()
