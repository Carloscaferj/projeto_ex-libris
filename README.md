# Reconhecimento de Marcas de Proveniência e Ex-Libris

Sistema para catalogar obras (título, autor, local, editora, data) e
identificar, a partir de uma foto de uma marca de proveniência ou de um
ex-libris, a qual obra catalogada ela pertence — aprendendo com cada nova
leitura.

## Como funciona

1. **Extração de características** (`feature_extractor.py`): cada imagem de
   marca é convertida num vetor de 2048 números por uma ResNet-50
   pré-treinada (ImageNet), usada como extrator de características fixo.
   Esse vetor captura forma, textura e composição gráfica — bom o
   suficiente para comparar selos, carimbos e gravuras sem precisar de
   milhares de exemplos rotulados.

2. **Memória vetorial** (`vector_index.py`): todas as marcas já confirmadas
   ficam guardadas como pontos num índice de busca por similaridade (FAISS,
   com fallback em NumPy). Uma nova leitura é comparada contra tudo que já
   foi visto.

3. **Protótipos por obra** (`recognizer.py`): além da busca por vizinhos, o
   sistema mantém a média dos embeddings de cada obra, atualizada
   incrementalmente a cada confirmação — um classificador "de baixo custo"
   que melhora sozinho a cada exemplo novo, sem retreinar nada.

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

python main.py init

python main.py add-obra --titulo "Os Lusíadas" --autor "Luís de Camões" \
    --local "Lisboa" --editora "Antônio Gonçalves" --data "1572"

# Busca sem gravar nada (útil para tentar localizar a obra de uma marca solta)
python main.py identify --imagem foto_ex_libris.jpg --tipo ex_libris

# Registra a marca e já vincula a uma obra conhecida (ensina o sistema)
python main.py add-marca --imagem foto_ex_libris.jpg --tipo ex_libris --obra-id 1

# Corrige/confirma o vínculo de uma marca cadastrada anteriormente como "novidade"
python main.py feedback --marca-id 3 --obra-id 1

python main.py list-obras
```

## Estrutura

- `config.py` — parâmetros (limiar de similaridade, caminhos, dimensão do embedding).
- `database.py` — esquema e acesso ao SQLite (`obras`, `marcas`, `identificacoes`).
- `feature_extractor.py` — extração de embeddings de imagem.
- `vector_index.py` — índice de busca por similaridade (FAISS ou NumPy).
- `recognizer.py` — orquestração: identificar, registrar marca, confirmar vínculo.
- `cli.py` / `main.py` — interface de linha de comando.

## Extensões possíveis

- Trocar a ResNet-50 por um modelo tipo CLIP para robustez a variações de
  iluminação/ângulo de foto.
- Adicionar detecção automática da região da marca dentro de uma página
  escaneada (hoje o sistema assume que a imagem já está recortada na marca).
- Expor a API via um servidor HTTP (FastAPI) para uso por um front-end web.
