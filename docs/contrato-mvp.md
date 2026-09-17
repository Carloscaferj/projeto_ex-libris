# Contrato do MVP e roteiro de homologação

Issue: [#5 — Fechar o contrato do MVP e o roteiro de homologação](https://github.com/Carloscaferj/projeto_ex-libris/issues/5)
Decisão registrada por: Heitor Bianchi, representando a equipe de acervo neste piloto. 2026-09-17.

## 1. Obra, exemplar e marca

O README e o domínio atual (`src/exlibris/domain/models.py`) só têm `Obra` e `Marca`,
com a marca ligada direto à obra bibliográfica. Isso não distingue cópias físicas
diferentes da mesma edição. Decisão:

- **Obra** — registro bibliográfico (título, autor, local, editora, data). Sem mudança.
- **Exemplar** (novo) — cópia física de uma obra. Uma obra pode ter N exemplares
  (`Obra 1:N Exemplar`).
- **Marca** — imagem recortada de um ex-libris/marca de proveniência. Cada marca
  vincula-se a exatamente um exemplar (`Exemplar 1:N Marca`, FK obrigatória
  `Marca.exemplar_id`); um mesmo exemplar pode acumular mais de uma marca ao
  longo do tempo (ex.: ex-libris e carimbo de proveniência no mesmo livro).

Esta é uma decisão de contrato, não uma implementação: introduzir `Exemplar` no
esquema fica para a issue #10 (versionamento/migração) e para o ajuste de
contrato da issue #11. Nenhum código de domínio é alterado por este documento.

### Exemplo — mesma marca em exemplares diferentes

Um carimbo de proveniência idêntico pode aparecer em dois exemplares distintos
(ex.: dois volumes que passaram pela mesma biblioteca particular antes de
chegarem ao acervo). Cada leitura gera um registro de `Marca` próprio, com seu
próprio `exemplar_id`. O reconhecimento pode apontar as duas marcas como
visualmente semelhantes e sugerir obras/exemplares candidatos, mas **nunca
promete identificação única**: a similaridade indica candidatos prováveis para
decisão humana, não uma prova de que a marca pertence a um único exemplar ou
obra. Duas marcas parecidas continuam sendo dois registros distintos, cada um
com seu próprio histórico de confirmação/correção.

## 2. Fluxo

```
cadastro (obra + exemplar)
  -> imagem recortada da marca
    -> candidatos (acima do limiar) ou sem correspondência (novidade)
      -> confirmação | correção (troca de exemplar/obra) | rejeição
        -> exportação (catálogo + curadoria)
```

- **Cadastro**: obra e exemplar são cadastrados antes ou durante o envio da marca.
- **Imagem recortada**: o MVP recebe a foto já recortada na marca (fora de escopo:
  recorte automático).
- **Candidatos / sem correspondência**: a busca por similaridade retorna
  candidatos com score, ou marca a leitura como novidade (pendente) quando
  nada ultrapassa o limiar.
- **Confirmação/correção/rejeição**: decisão humana. Confirmar vincula a marca
  ao exemplar sugerido; corrigir troca o vínculo; rejeitar remove a sugestão
  sem vincular. Só marcas confirmadas entram na memória de reconhecimento
  (issue #4/#8).
- **Exportação**: catálogo confirmado e trilha de curadoria, versionados
  (issue #11/#15).

## 3. Campos, vocabulário, papéis e retenção

**Campos obrigatórios**

| Entidade | Obrigatórios | Opcionais |
|---|---|---|
| Obra | título | autor, local, editora, data |
| Exemplar | obra_id, identificador/localização física (cota ou código de tombo) | observações |
| Marca | exemplar_id, tipo, imagem | descrição |

**Vocabulário de tipo de marca** — mantido o existente em `MarcaTipo`:
`ex_libris`, `proveniencia`, `outro`. Nenhuma mudança proposta nesta issue.

**Papéis de acesso** — papel único "equipe do piloto": todo usuário autenticado
pode consultar o catálogo e curar (confirmar/corrigir/rejeitar). Sem distinção
leitor/curador nesta fase. Revisar se o piloto crescer além de uma equipe
pequena (acompanha issue #13).

**Retenção de imagens**:
- Marcas confirmadas (vinculadas a um exemplar) são retidas indefinidamente
  enquanto o vínculo existir — a imagem é evidência do vínculo e alimenta a
  memória de reconhecimento.
- Marcas rejeitadas ou nunca vinculadas (sem correspondência e nunca
  confirmadas) são descartadas depois de um prazo. **Prazo exato: pendente**
  (ver seção 5).

## 4. Piloto: coleção, volume, usuários, hardware, metas

**Pendente.** Não há coleção piloto, volume esperado, número de usuários
simultâneos, hardware alvo ou metas de latência/qualidade definidos até o
momento — não é inventado neste documento.

- Responsável: Heitor Bianchi, junto à equipe de acervo a ser confirmada.
- Sem data-limite definida.
- Bloqueia diretamente a issue #20 (avaliação/homologação final), que depende
  desses números para medir Recall@k, latência e capacidade.

## 5. Roteiro de homologação

Roteiro aprovado para exercitar o MVP fim a fim (execução real fica para a
issue #20, quando M1/M2 estiverem prontos):

1. **Catálogo vazio** — instância nova, sem obras/exemplares/marcas. Cadastrar
   a primeira obra e exemplar, enviar a primeira marca e confirmar que o
   sistema retorna "sem correspondência" (novidade), sem falhar por índice
   vazio (cobre a regressão da issue #6).
2. **Correspondência conhecida** — consultar uma imagem de marca já
   confirmada (ou uma leitura nova do mesmo exemplar) e verificar que o
   exemplar/obra correto aparece entre os candidatos, com score coerente e
   filtro de tipo aplicado (issue #7).
3. **Correspondência desconhecida** — consultar uma marca sem vínculo prévio
   no acervo e verificar que o sistema aponta "sem correspondência"/novidade,
   sem forçar um vínculo.
4. **Imagem inválida** — enviar um arquivo corrompido, não decodificável ou
   fora do formato aceito; verificar erro de validação claro e nenhum
   registro parcial no banco (issue #5/#8).
5. **Correção** — corrigir um vínculo já confirmado (mover marca do exemplar A
   para o exemplar B) e verificar que a busca deixa de sugerir A, passa a
   refletir B, e que repetir a confirmação não distorce contagens/pesos
   (issue #4).
6. **Restauração** — a partir de um backup (issue #18), restaurar banco e
   imagens em ambiente limpo e repetir os cenários 1–3 obtendo os mesmos
   resultados.

Critério de aprovação do MVP: os seis cenários executados com sucesso pela
equipe do piloto, com pendências registradas (não escondidas) quando algum
cenário não puder ser demonstrado.

## 6. Pendências registradas

| Pendência | Responsável | Bloqueia |
|---|---|---|
| Coleção piloto, volume esperado, usuários simultâneos, hardware, metas de latência/qualidade | Heitor Bianchi + equipe de acervo (a confirmar) | Issue #20 |
| Prazo de retenção para imagens rejeitadas/sem correspondência | Heitor Bianchi + equipe de acervo (a confirmar) | Política final de armazenamento (issue #8/#18) |

## 7. Limites desta entrega

Este documento fecha o contrato de domínio e o roteiro de homologação. Não
altera esquema, código ou testes. A introdução de `Exemplar` no banco depende
da issue #10; o ajuste do contrato de identificação/filtro depende da
issue #11.
