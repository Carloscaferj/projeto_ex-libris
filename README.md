# Reconhecimento de Marcas de Proveniência e Ex-Libris

Sistema para catalogar obras (título, autor, local, editora, data) e
identificar, a partir de uma foto de uma marca de proveniência ou de um
ex-libris, a qual obra catalogada ela pertence — aprendendo com cada nova
leitura.

O contrato de domínio do MVP (obra, exemplar e marca, fluxo de curadoria,
campos obrigatórios e roteiro de homologação) está registrado em
[docs/contrato-mvp.md](docs/contrato-mvp.md). O domínio atual descrito abaixo
ainda não tem o conceito de exemplar físico — essa mudança de esquema fica
para uma issue de migração futura.

## Como funciona

1. **Extração de características** (`src/exlibris/infrastructure/ml/feature_extractor.py`): cada imagem de
   marca é convertida num vetor de 2048 números por uma ResNet-50
   pré-treinada (ImageNet), usada como extrator de características fixo.
   Esse vetor captura forma, textura e composição gráfica — bom o
   suficiente para comparar selos, carimbos e gravuras sem precisar de
   milhares de exemplos rotulados.

2. **Memória vetorial** (`src/exlibris/infrastructure/search/vector_index.py`): todas as marcas já confirmadas
   ficam guardadas como pontos num índice de busca por similaridade (FAISS,
   com fallback em NumPy). Uma nova leitura é comparada contra tudo que já
   foi visto.

3. **Serviço de reconhecimento** (`src/exlibris/application/recognition_service.py`):
   além da busca por vizinhos, o sistema mantém a média dos embeddings de
   cada obra, atualizada incrementalmente a cada confirmação — um
   classificador "de baixo custo" que melhora sozinho a cada exemplo novo,
   sem retreinar nada.

4. **Curadoria humana / aprendizado ativo**: quando a similaridade da melhor
   correspondência fica abaixo do limiar (`config.SIMILARITY_THRESHOLD`), a
   marca é tratada como possível novidade e fica pendente (`confirmado=0`)
   até alguém confirmar o vínculo com `feedback`. Isso evita que erros
   entrem na memória e "envenenem" buscas futuras.

### Por que não é uma rede neural "aprendendo do zero" a cada imagem?

Retreinar uma CNN inteira a cada nova leitura seria lento, instável (risco
de esquecimento catastrófico) e desnecessário. A abordagem aqui —
aprendizado contínuo baseado em memória/recuperação (*retrieval-based
continual learning*) — é o que sistemas reais de reconhecimento de
marcas/logotipos/obras de arte usam na prática: o backbone fica congelado e
o conhecimento novo entra por meio do índice vetorial e dos protótipos, que
crescem indefinidamente e nunca "esquecem" o que já foi visto.

## Uso

```bash
pip install -r requirements.txt

python -m exlibris init

python -m exlibris add-obra --titulo "Os Lusíadas" --autor "Luís de Camões" \
    --local "Lisboa" --editora "Antônio Gonçalves" --data "1572"

# Busca sem gravar nada (útil para tentar localizar a obra de uma marca solta)
python -m exlibris identify --imagem foto_ex_libris.jpg --tipo ex_libris

# Registra a marca e já vincula a uma obra conhecida (ensina o sistema)
python -m exlibris add-marca --imagem foto_ex_libris.jpg --tipo ex_libris --obra-id 1

# Corrige/confirma o vínculo de uma marca cadastrada anteriormente como "novidade"
python -m exlibris feedback --marca-id 3 --obra-id 1

python -m exlibris list-obras
```

O `requirements.txt` instala o projeto em modo editável. Depois da
instalação, a CLI deve ser executada pelo pacote com
`python -m exlibris ...`.

Se você acabou de clonar o repositório e ainda não instalou as dependências,
`python -m exlibris ...` não vai funcionar.

## Testes

Em uma instalação limpa (Python 3.10+):

```bash
pip install -e ".[dev]"

pytest -m "not slow"
```

`pytest -m "not slow"` roda a suíte usada no CI: testes de domínio,
aplicação (com embeddings sintéticos, sem carregar o modelo real),
persistência SQLite (arquivo temporário) e um smoke test de ponta a ponta
da CLI — sem GPU e sem baixar pesos do modelo. Para rodar a suíte completa,
incluindo o smoke test do extrator de embeddings que carrega a ResNet-50
real (baixa pesos na primeira execução), use `pytest`.

Os testes usam embeddings sintéticos e bancos SQLite temporários, sem baixar o
modelo ResNet-50 nem depender do FAISS estar instalado (o backend NumPy é
usado como fallback automaticamente) — exceto o smoke test marcado `slow`.

## Estrutura

- `src/exlibris/config.py` — parâmetros globais do sistema.
- `src/exlibris/interface/cli.py` — interface de linha de comando.
- `src/exlibris/application/recognition_service.py` — fluxo principal da aplicação.
- `src/exlibris/domain/models.py` — modelos tipados do domínio.
- `src/exlibris/infrastructure/persistence/sqlite_catalog.py` — persistência SQLite.
- `src/exlibris/infrastructure/ml/feature_extractor.py` — extração de embeddings.
- `src/exlibris/infrastructure/search/vector_index.py` — índice vetorial.

## Extensões possíveis

- Trocar a ResNet-50 por um modelo tipo CLIP para robustez a variações de
  iluminação/ângulo de foto.
- Adicionar detecção automática da região da marca dentro de uma página
  escaneada (hoje o sistema assume que a imagem já está recortada na marca).
- Expor a API via um servidor HTTP (FastAPI) para uso por um front-end web.
