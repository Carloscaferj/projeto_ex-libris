# Roadmap — MVP web de curadoria Ex Libris

## Issues publicadas

Issue central: https://github.com/Carloscaferj/projeto_ex-libris/issues/4

- 01: [#5 — [M0][P0] Fechar o contrato do MVP e o roteiro de homologação](https://github.com/Carloscaferj/projeto_ex-libris/issues/5)
- 02: [#6 — [M0][P0] Corrigir reconstrução do índice com os modelos Marca](https://github.com/Carloscaferj/projeto_ex-libris/issues/6)
- 03: [#7 — [M0][P0] Criar uma base de testes determinísticos e CI](https://github.com/Carloscaferj/projeto_ex-libris/issues/7)
- 04: [#8 — [M0][P0] Separar sugestões de vínculos confirmados e tornar feedback idempotente](https://github.com/Carloscaferj/projeto_ex-libris/issues/8)
- 05: [#9 — [M0][P0] Definir validação e erros estáveis dos casos de uso](https://github.com/Carloscaferj/projeto_ex-libris/issues/9)
- 06: [#10 — [M0][P0] Versionar o esquema e preparar migração segura dos dados](https://github.com/Carloscaferj/projeto_ex-libris/issues/10)
- 07: [#11 — [M0][P0] Corrigir contrato de identificação, filtro por tipo e histórico](https://github.com/Carloscaferj/projeto_ex-libris/issues/11)
- 08: [#12 — [M1][P0] Implementar entrada segura e armazenamento gerenciado de imagens](https://github.com/Carloscaferj/projeto_ex-libris/issues/12)
- 09: [#13 — [M1][P0] Completar consulta e manutenção do catálogo](https://github.com/Carloscaferj/projeto_ex-libris/issues/13)
- 10: [#14 — [M1][P0] Entregar fila de curadoria com decisão e trilha de auditoria](https://github.com/Carloscaferj/projeto_ex-libris/issues/14)
- 11: [#15 — [M1][P0] Entregar exportação versionada do catálogo e da curadoria](https://github.com/Carloscaferj/projeto_ex-libris/issues/15)
- 12: [#16 — [M1][P0] Expor API HTTP dos casos de uso com contrato documentado](https://github.com/Carloscaferj/projeto_ex-libris/issues/16)
- 13: [#17 — [M1][P0] Restringir o piloto à equipe e identificar ações de curadoria](https://github.com/Carloscaferj/projeto_ex-libris/issues/17)
- 14: [#18 — [M1][P0] Criar interface web para catálogo e envio de imagens](https://github.com/Carloscaferj/projeto_ex-libris/issues/18)
- 15: [#19 — [M1][P0] Criar interface de reconhecimento e revisão humana](https://github.com/Carloscaferj/projeto_ex-libris/issues/19)
- 16: [#20 — [M2][P0] Preparar instalação reproduzível e configuração do piloto](https://github.com/Carloscaferj/projeto_ex-libris/issues/20)
- 17: [#21 — [M2][P0] Garantir consistência do índice e limites de concorrência](https://github.com/Carloscaferj/projeto_ex-libris/issues/21)
- 18: [#22 — [M2][P0] Entregar backup e restauração verificável do acervo](https://github.com/Carloscaferj/projeto_ex-libris/issues/22)
- 19: [#23 — [M2][P1] Adicionar diagnóstico operacional e logs rastreáveis](https://github.com/Carloscaferj/projeto_ex-libris/issues/23)
- 20: [#24 — [M2][P0] Avaliar reconhecimento e homologar o MVP com a equipe](https://github.com/Carloscaferj/projeto_ex-libris/issues/24)

## Objetivo
Uma equipe de acervo consegue cadastrar obras, enviar imagens recortadas de marcas, consultar candidatos, confirmar/corrigir/rejeitar vínculos e exportar dados por uma interface web simples. O reconhecimento auxilia a decisão humana.

## Base da análise
Inspeção do código local em 2026-09-08, HEAD 20f3363, branch padrão remota main. Sem alterações locais prévias e sem issues ou PRs abertos encontrados na consulta inicial. Há CLI, serviço de aplicação, SQLite, ResNet-50 e índice em memória com FAISS opcional/NumPy. Não foram encontrados testes ou CI. Não houve execução do modelo real nem avaliação de qualidade.
A reconstrução do índice com uma dataclass Marca foi reproduzida e falhou com TypeError. Por inspeção, pendentes entram no índice, feedback repetido/corrigido distorce protótipos, tipo não filtra e a promessa de identify sem gravação diverge do histórico persistido.

## Escopo
- Piloto interno de uma equipe, acesso restrito e uma instância.
- SQLite e extrator atual mantidos inicialmente; imagem já recortada.
- Fluxo: catálogo → ingestão → candidatos/sem correspondência → curadoria → catálogo confirmado → exportação.
- Backup/restauração, validação, rastreabilidade e testes fazem parte do MVP.
- Fora do MVP: SaaS público, múltiplas instituições, cobrança, microserviços, GPU obrigatória, OCR, recorte automático, troca de modelo e integrações bibliográficas.
- Obra versus exemplar e marcas compartilhadas precisam de decisão com os curadores na tarefa 01. A interface web foi confirmada pelo solicitante; demais parâmetros de escala ainda são hipóteses a validar.

## Sequência e gates
1. **M0 — Contrato e núcleo confiável:** tarefas 01–07. Saída: banco existente reabre, pendentes não contaminam busca, feedback é idempotente e os contratos têm regressões automatizadas.
2. **M1 — Ciclo web completo:** tarefas 08–15. Saída: equipe autenticada realiza cadastro → imagem → revisão → exportação pelo navegador.
3. **M2 — Operação e homologação:** tarefas 16–20. Saída: instalação limpa, reinício, restauração e critérios de qualidade/capacidade do piloto demonstrados.

As dependências de cada issue determinam a ordem real; tarefas sem dependência entre si podem ser executadas em paralelo. Começar por 01, 02 e 03. P0 é essencial/bloqueante; P1 vem depois do núcleo, mas também integra o gate final. Não há promessa de prazo antes de validar equipe, volume e disponibilidade.

## Como executar
Uma issue por entrega coesa, refinada em PRs pequenos quando necessário. Antes de começar: dependências concluídas, entradas e decisão de domínio disponíveis. Antes de fechar: critérios de aceite demonstrados, testes pertinentes passando, docs atualizadas e riscos registrados. Não fechar uma issue apenas porque existe uma tela ou endpoint sem seu fluxo de erro. Usar branches codex/<area>-<intent> e convenções do CONTRIBUTING.

## Pós-MVP, condicionado a evidência
Importação em lote com preview/validação por linha; integrações com catálogos institucionais; melhor modelo/recorte/OCR após benchmark; tarefas assíncronas quando a latência justificar; PostgreSQL/múltiplas instâncias quando limites medidos do piloto justificarem. Estes itens não bloqueiam o primeiro MVP e não foram transformados em compromissos de implementação.

## Backlog refinado

### 01 — [M0][P0] Fechar o contrato do MVP e o roteiro de homologação

**Depende de:** nenhuma

O README associa marcas a obras, mas não distingue obra bibliográfica, exemplar físico e marca compartilhada entre exemplares. Essa decisão afeta cadastro, reconhecimento e exportação.

**Critérios de aceite**

- [ ] Validar com a equipe de acervo o significado de obra, exemplar e marca; registrar exemplos de uma mesma marca em diferentes exemplares e impedir promessa de identificação única sem evidência.
- [ ] Documentar o fluxo cadastro → imagem recortada → candidatos ou sem correspondência → confirmação/correção/rejeição → exportação.
- [ ] Definir campos obrigatórios, vocabulário de tipos, quem pode consultar/curar e política de retenção das imagens.
- [ ] Acordar coleção piloto, volume esperado, usuários simultâneos, hardware e metas mensuráveis de latência/qualidade; registrar pendências com responsável, sem inventar resultados.
- [ ] Aprovar roteiro de homologação com catálogo vazio, correspondência conhecida, desconhecida, imagem inválida, correção e restauração.

**Limites da entrega:** Documento curto e exemplos de dados; nenhuma reformulação ampla de domínio antes dessa decisão.

### 02 — [M0][P0] Corrigir reconstrução do índice com os modelos Marca

**Depende de:** nenhuma

`IndiceVetorial.construir_a_partir_do_banco` usa marca['id']/marca['embedding'], mas o repositório retorna dataclasses Marca. Reprodução local com uma Marca produziu TypeError: 'Marca' object is not subscriptable.

**Critérios de aceite**

- [ ] Construir o índice usando o contrato tipado retornado pelo repositório.
- [ ] Inicializar o serviço com banco vazio e com marcas persistidas sem erro.
- [ ] Adicionar teste de regressão persistir → fechar → reabrir → buscar com embeddings sintéticos, sem download de modelo.
- [ ] Verificar resultado equivalente no fallback NumPy e no backend FAISS quando instalado.

**Limites da entrega:** Corrigir a incompatibilidade sem alterar critérios de reconhecimento nesta issue.

### 03 — [M0][P0] Criar uma base de testes determinísticos e CI

**Depende de:** nenhuma

Não foram encontrados testes nem workflow de CI no snapshot analisado; regras de estado e persistência não têm proteção automatizada.

**Critérios de aceite**

- [ ] Configurar dependências de desenvolvimento e execução documentada de testes em instalação limpa.
- [ ] Permitir injetar extrator e adaptadores no serviço, mantendo padrões de produção; testes de aplicação usam embeddings sintéticos.
- [ ] Executar testes de domínio/aplicação/SQLite temporário e smoke da CLI no CI, sem GPU nem download de pesos.
- [ ] Validar instalação do pacote e CLI em Windows e Linux na versão mínima de Python suportada.
- [ ] Falhas de testes bloqueiam o check do PR; fixtures não usam dados reais de acervo.

**Limites da entrega:** Introduzir apenas os pontos de substituição necessários; não reescrever toda a arquitetura.

### 04 — [M0][P0] Separar sugestões de vínculos confirmados e tornar feedback idempotente

**Depende de:** 02, 03

O registro e a reconstrução indexam todas as marcas. Confirmar novamente incrementa contagens; mover o vínculo não remove contribuição da obra anterior. A média é renormalizada a cada passo, alterando os pesos dos exemplos.

**Critérios de aceite**

- [ ] Somente marcas elegíveis e confirmadas compõem a memória de reconhecimento; pendentes continuam disponíveis para curadoria.
- [ ] Confirmar duas vezes não altera índice, contagens ou ranking.
- [ ] Corrigir obra A para B remove contribuição de A; rejeitar/desvincular remove a marca da memória.
- [ ] Calcular protótipos pela soma e contagem reais, normalizando apenas o vetor usado na comparação.
- [ ] Após cada transição, comparar busca em memória com reconstrução do banco; incluir regressões para repetição, correção e rejeição.

**Limites da entrega:** SQLite é a fonte de verdade; atualização do índice só após persistência bem-sucedida.

### 05 — [M0][P0] Definir validação e erros estáveis dos casos de uso

**Depende de:** 01, 03

Entradas chegam quase diretamente ao SQLite/ML; IDs inexistentes, título vazio e parâmetros inválidos não têm respostas de negócio consistentes.

**Critérios de aceite**

- [ ] Rejeitar título vazio, tipo inválido, top_k não positivo/fora do limite e IDs inexistentes antes de efeitos colaterais.
- [ ] Validar embeddings: dimensão, valores finitos e norma utilizável; rejeitar vetores incompatíveis.
- [ ] Impedir estado confirmado sem vínculo válido segundo o contrato de domínio.
- [ ] Definir erros de validação, não encontrado, conflito e infraestrutura, mapeáveis para CLI e HTTP.
- [ ] Cobrir chamadas diretas ao serviço, além da CLI; erros de entrada não deixam registros parciais.

**Limites da entrega:** Regras em domain/application; detalhes de SQLite/Pillow não devem vazar para mensagens do usuário.

### 06 — [M0][P0] Versionar o esquema e preparar migração segura dos dados

**Depende de:** 01, 03

`iniciar_banco` apenas executa CREATE TABLE IF NOT EXISTS; alterações futuras não atualizam bancos existentes.

**Critérios de aceite**

- [ ] Introduzir versão de esquema e migrações ordenadas para banco novo e legado.
- [ ] Preservar IDs, imagens referenciadas e embeddings existentes em fixture de migração.
- [ ] Falha de migração não deixa esquema parcialmente aplicado; documentar recuperação a partir de cópia válida.
- [ ] Aplicar restrições e índices coerentes com o contrato do MVP; detectar inconsistências legadas sem descartar dados silenciosamente.
- [ ] Testar migração e reexecução; registrar política para banco criado por versão mais recente.

**Limites da entrega:** Preservar SQLite no piloto. Alterar o modelo bibliográfico apenas se decidido na tarefa 01.

### 07 — [M0][P0] Corrigir contrato de identificação, filtro por tipo e histórico

**Depende de:** 04, 05, 06

`tipo` é retornado mas não filtra a busca. O score gravado vem do vizinho enquanto a obra sugerida vem de outro ranking. identify promete não gravar, mas grava histórico; registrar_feedback não está ligado ao fluxo de curadoria.

**Critérios de aceite**

- [ ] Aplicar filtro de tipo antes da seleção top_k, com comportamento documentado para busca sem filtro.
- [ ] Retornar candidatos, score de similaridade, motivo de ausência de correspondência e versão do modelo; score não é apresentado como probabilidade calibrada.
- [ ] Persistir sugestão e score coerentes, com ID de identificação retornado para rastrear a decisão humana.
- [ ] Escolher e documentar busca transitória versus busca com histórico; alinhar CLI, README e futura API.
- [ ] Testar catálogo vazio, tipos misturados, limiar, empate e divergência entre ranking de marcas e obras.

**Limites da entrega:** A política de vínculo continua humana; a busca não confirma automaticamente.

### 08 — [M1][P0] Implementar entrada segura e armazenamento gerenciado de imagens

**Depende de:** 05, 06

A cópia de arquivo está na CLI; caminhos ficam persistidos e uma falha posterior pode deixar arquivos órfãos. Não há limites de upload ou política de validação.

**Critérios de aceite**

- [ ] Mover orquestração de ingestão para application e armazenamento para adapter em infrastructure, reutilizável por CLI e web.
- [ ] Aceitar formatos acordados, conferir conteúdo decodificável, limitar bytes/pixels e tratar orientação EXIF; nomes externos não controlam caminhos internos.
- [ ] Usar identificador gerado e checksum, com política explícita de duplicatas; reenvio/retry não cria cópias involuntárias.
- [ ] Persistir arquivo e registro com compensação em falhas; testar disco indisponível e erro de banco.
- [ ] Imagens ficam fora da árvore do código, têm localização configurável e acesso HTTP controlado; arquivos inválidos não acionam inferência.

**Limites da entrega:** MVP recebe foto já recortada da marca; detecção automática e editor avançado ficam fora.

### 09 — [M1][P0] Completar consulta e manutenção do catálogo

**Depende de:** 05, 06

A aplicação permite inserir e listar obras, mas não oferece busca, detalhes, edição nem paginação para uma equipe operar o acervo.

**Critérios de aceite**

- [ ] Disponibilizar listagem paginada, busca por título/autor/identificador e detalhe com marcas associadas.
- [ ] Permitir edição dos metadados definidos em 01 e arquivamento com política explícita de vínculos.
- [ ] Marcas de registros arquivados deixam de aparecer como candidatas quando essa for a regra acordada; histórico continua rastreável.
- [ ] Tratar conflitos de edição para evitar sobrescrita silenciosa entre curadores.
- [ ] Testar CRUD permitido e restrições sem excluir definitivamente imagens ou histórico.

**Limites da entrega:** Não incluir catalogação bibliográfica completa ou integrações institucionais.

### 10 — [M1][P0] Entregar fila de curadoria com decisão e trilha de auditoria

**Depende de:** 04, 06, 07, 09

Existe feedback de vínculo por ID, mas não há fila, rejeição, histórico de correções ou conexão entre sugestão e decisão.

**Critérios de aceite**

- [ ] Listar pendentes com paginação, filtros e detalhe contendo imagem, candidatos e metadados.
- [ ] Permitir confirmar, escolher outra obra, rejeitar sugestão e manter pendente com justificativa.
- [ ] Registrar ator, data, estado anterior/novo, motivo e identificação associada; nunca confundir sugestão com confirmação.
- [ ] Decisões repetidas são idempotentes; decisões concorrentes conflitantes produzem conflito visível.
- [ ] Testar ciclo completo e comprovar que só decisões elegíveis alteram a memória de reconhecimento.

**Limites da entrega:** Ator deve vir da identidade autenticada na web; integração de acesso é tratada em 13.

### 11 — [M1][P0] Entregar exportação versionada do catálogo e da curadoria

**Depende de:** 06, 09, 10

Não existe fluxo de saída estruturado; dados ficam no banco e em texto no terminal.

**Critérios de aceite**

- [ ] Exportar metadados em CSV e formato JSON versionado, com identificadores, vínculos, estados e datas; definir dicionário de campos.
- [ ] Permitir selecionar catálogo completo ou filtro e explicitar se pendentes/arquivados estão incluídos.
- [ ] Garantir encoding, acentos, aspas e quebras de linha; neutralizar fórmulas em CSV destinado a planilhas.
- [ ] Exportar um snapshot consistente e usar referências estáveis de imagem, sem expor caminhos absolutos internos.
- [ ] Testar arquivo vazio e catálogo com correções; documentar diferença entre exportação e backup restaurável.

**Limites da entrega:** Exportação não inclui blobs de embeddings nem vira uma integração externa genérica.

### 12 — [M1][P0] Expor API HTTP dos casos de uso com contrato documentado

**Depende de:** 07, 08, 09, 10, 11

O projeto possui somente CLI. A web deve reutilizar a aplicação e evitar duplicar regras de reconhecimento e curadoria.

**Critérios de aceite**

- [ ] Adicionar adapter HTTP sob interface para catálogo, upload/registro, identificação, pendências, decisões e exportação.
- [ ] Publicar contrato de requests/responses, paginação, erros e limites de upload, sem retornar embeddings ou caminhos internos.
- [ ] Definir retry/idempotência das operações de escrita e proteção contra perda de atualização.
- [ ] Gerenciar serviço/modelo no ciclo de vida do processo; limitar inferência concorrente e responder ocupação de forma explícita.
- [ ] Testar contratos com extrator substituto e demonstrar fluxo completo via HTTP; preservar comandos existentes da CLI.

**Limites da entrega:** Selecionar framework em decisão curta considerando dependências e manutenção; sem microserviços ou filas distribuídas no MVP.

### 13 — [M1][P0] Restringir o piloto à equipe e identificar ações de curadoria

**Depende de:** 01, 12

Não existe autenticação; a interface de equipe precisa proteger imagens, metadados e operações de escrita.

**Critérios de aceite**

- [ ] Escolher integração de identidade simples para o ambiente piloto e documentar provisionamento/revogação.
- [ ] Proteger API, imagens e exportações; identidade do ator deve ser obtida no servidor, nunca confiada ao payload.
- [ ] Aplicar permissões de consulta e curadoria conforme 01, com padrão de acesso negado.
- [ ] Tratar sessões/credenciais, segredos de configuração e proteção CSRF se houver cookies; documentar HTTPS no ambiente compartilhado.
- [ ] Testar acesso anônimo, usuário sem permissão, sessão expirada e revogação; auditoria de decisões recebe ator correto.

**Limites da entrega:** Sem cadastro público, cobrança, multi-instituição ou sistema de permissões genérico.

### 14 — [M1][P0] Criar interface web para catálogo e envio de imagens

**Depende de:** 12, 13

Curadores não devem depender de terminal para cadastrar e consultar o acervo.

**Critérios de aceite**

- [ ] Implementar entrada autenticada, busca/listagem paginada, formulário de cadastro/edição e detalhe da obra.
- [ ] Oferecer envio de imagem com prévia, tipo e vínculo opcional, apresentando limites antes do envio.
- [ ] Mostrar progresso/estado de processamento, validação por campo e recuperação de falha sem duplicar registro.
- [ ] Cobrir estados vazio, carregando, sem permissão e indisponível; navegação por teclado e rótulos acessíveis.
- [ ] Testar uma jornada de cadastro → upload → detalhe em navegador, com dados fictícios.

**Limites da entrega:** Escolher a solução de frontend mais simples de manter; nenhum design system próprio ou painel analítico.

### 15 — [M1][P0] Criar interface de reconhecimento e revisão humana

**Depende de:** 10, 14

A equipe precisa comparar visualmente a entrada e os candidatos e tomar decisões rastreáveis.

**Critérios de aceite**

- [ ] Oferecer consulta de imagem com tipo opcional e candidatos mostrando imagem de referência, obra e similaridade.
- [ ] Diferenciar sem correspondência de erro técnico; permitir registrar pendência ou cadastro manual sem vínculo forçado.
- [ ] Entregar fila de pendências e ações de confirmar/corrigir/rejeitar com motivo e feedback claro.
- [ ] Exibir conflito se outra pessoa já revisou; manter histórico consultável e impedir duplo envio acidental.
- [ ] Disponibilizar exportação e testar jornada cadastro → reconhecimento → decisão → nova consulta → exportação.

**Limites da entrega:** Similaridade não é certeza de procedência; textos devem refletir a ambiguidade definida em 01.

### 16 — [M2][P0] Preparar instalação reproduzível e configuração do piloto

**Depende de:** 06, 12, 13

Dependências não têm versões delimitadas; diretórios são criados ao importar config e dados dependem da localização do pacote. Pesos são baixados na primeira inferência.

**Critérios de aceite**

- [ ] Definir política reproduzível de dependências e versões suportadas; documentar backend de busca efetivamente usado.
- [ ] Configurar banco, imagens, logs, dispositivo e cache do modelo fora da instalação; evitar escrita ao importar config.
- [ ] Oferecer comando/receita de inicialização e execução em CPU no ambiente piloto escolhido, com segredos fora do repositório.
- [ ] Preparar pesos explicitamente e informar falhas de download/incompatibilidade; restart com cache disponível funciona sem novo download.
- [ ] Verificar instalação limpa, migração, readiness e reinício preservando dados.

**Limites da entrega:** Sem exigir GPU, Kubernetes ou múltiplos serviços para o piloto.

### 17 — [M2][P0] Garantir consistência do índice e limites de concorrência

**Depende de:** 04, 06, 12

O serviço carrega catálogo e índice inteiro em memória. Instâncias separadas não recebem atualizações e o fallback NumPy cresce com vstack por marca.

**Critérios de aceite**

- [ ] Definir operação suportada em uma instância e coordenar escritas/atualizações para buscas não usarem estado parcial.
- [ ] Detectar mudança de versão do catálogo e invalidar/reconstruir memória, incluindo alteração feita pela CLI, ou bloquear explicitamente essa concorrência.
- [ ] Banco permanece fonte de verdade; falha de atualização em memória aciona recuperação rastreável antes de servir resultado obsoleto.
- [ ] Testar duas sessões, correção durante busca, reinício e bloqueio SQLite com resposta controlada.
- [ ] Medir carga de inicialização, memória e latência nos volumes de 01; registrar limites e evidência para eventual otimização, sem prometer escala não medida.

**Limites da entrega:** Multiworker só após resolver sincronização; não migrar banco ou busca por antecipação.

### 18 — [M2][P0] Entregar backup e restauração verificável do acervo

**Depende de:** 06, 08, 16

SQLite e imagens compõem o acervo; copiar apenas o banco não garante uma restauração completa.

**Critérios de aceite**

- [ ] Criar procedimento de backup consistente de banco, imagens e metadados de versão/configuração necessários, excluindo segredos.
- [ ] Usar snapshot SQLite suportado ou manutenção que pause escrita; manifest/checksums detectam arquivo ausente ou corrompido.
- [ ] Restaurar em diretório vazio e validar migrações, vínculos, imagens e reconstrução do índice.
- [ ] Impedir sobrescrita acidental do acervo ativo e documentar retenção, responsável e frequência do piloto.
- [ ] Executar e registrar ensaio de restauração com busca e exportação funcionando; medir tempo e perda máxima de dados.

**Limites da entrega:** Backup é distinto da exportação de uso dos curadores; sem serviço de nuvem obrigatório.

### 19 — [M2][P1] Adicionar diagnóstico operacional e logs rastreáveis

**Depende de:** 12, 16, 17

Não há diagnóstico de prontidão, métricas ou correlação entre falhas, consultas e decisões.

**Critérios de aceite**

- [ ] Disponibilizar liveness/readiness com estado de banco, armazenamento e modelo, sem expor dados sensíveis.
- [ ] Registrar IDs de requisição, duração, resultado e falhas por etapa; não registrar imagem, embeddings, segredos ou caminhos privados desnecessariamente.
- [ ] Medir erros, latência de inferência/busca, tamanho do catálogo e fila pendente com solução mínima.
- [ ] Documentar ações para disco cheio, banco bloqueado, pesos ausentes e índice inconsistente.
- [ ] Testar falhas simuladas e confirmar que o usuário recebe erro útil e o operador consegue rastreá-lo.

**Limites da entrega:** P1 significa depois do núcleo, mas ainda obrigatório para liberar o piloto.

### 20 — [M2][P0] Avaliar reconhecimento e homologar o MVP com a equipe

**Depende de:** 01, 03, 15, 16, 17, 18, 19

Não há dataset de avaliação nem evidência de que o limiar 0.75 atende o acervo. O README faz afirmações de qualidade não sustentadas por medições no projeto.

**Critérios de aceite**

- [ ] Montar conjunto autorizado de marcas conhecidas, desconhecidas e variações reais, separando referências/ajuste de avaliação e evitando duplicatas entre partições.
- [ ] Medir Recall@k, falsos vínculos/aceites e comportamento de desconhecidos; calibrar limiar só no conjunto de ajuste e registrar modelo/preprocessamento/dataset.
- [ ] Executar roteiro de 01 com curadores no ambiente piloto, incluindo estados de erro, conflitos, exportação e recuperação.
- [ ] Comparar qualidade, latência, memória e concorrência com metas acordadas; registrar resultados, limitações e bloqueadores sem inventar métricas.
- [ ] Publicar guia rápido, procedimento operacional e checklist de release; liberar piloto somente com critérios cumpridos ou exceções formalmente aceitas.

**Limites da entrega:** Troca de modelo, OCR e detecção de região dependem dos resultados e são pós-MVP.
