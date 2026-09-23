# Claude harness do projeto Ex Libris

Este projeto separa duas coisas, no mesmo espírito do harness do Codex (veja [codex-harness.md](codex-harness.md)):

- `skills`: contexto durável do projeto, carregado automaticamente pelo Claude Code conforme a descrição bate com a tarefa (ou via `/nome-da-skill`).
- `agents`: papéis operacionais (subagentes) que aplicam uma skill a um tipo específico de trabalho, com um conjunto de ferramentas restrito ao papel.

## Estrutura recomendada

- `.claude/skills/exlibris-architecture`
  Regras para evolução de arquitetura, limites entre camadas e decisões de stack.
- `.claude/skills/exlibris-delivery`
  Convenções de branch, commit, PR e fechamento de tarefas.
- `.claude/skills/exlibris-pr-review`
  Critérios de revisão com foco em regressão, documentação e higiene de entrega.
- `.claude/skills/exlibris-testing`
  Layout de testes (`pytest`, um diretório por camada), estratégia por camada e como lidar com não-determinismo de ML/similaridade.
- `.claude/skills/exlibris-ci`
  O que colocar (e o que não colocar) num workflow de CI para o projeto.
- `.claude/skills/exlibris-migration`
  Regras para evoluir o schema SQLite sem quebrar bancos já existentes.
- `.claude/agents/exlibris-architect.md`
  Subagente somente leitura (`Read, Grep, Glob, Bash`) que aplica a skill de arquitetura e devolve uma proposta, sem editar código.
- `.claude/agents/exlibris-executor.md`
  Subagente com acesso a edição (`Edit, Write` inclusos) que aplica a skill de delivery para implementar a mudança.
- `.claude/agents/exlibris-reviewer.md`
  Subagente somente leitura que aplica a skill de PR review antes de abrir um PR.
- `.claude/agents/exlibris-tester.md`
  Subagente com acesso a edição que aplica a skill de testing para adicionar ou expandir cobertura de testes.
- `.claude/agents/exlibris-bugfix.md`
  Subagente com acesso a edição, sem skill própria: compõe `exlibris-architecture` (isolar a camada certa), `exlibris-testing` (teste de regressão) e `exlibris-delivery` (branch/commit) para corrigir um bug de ponta a ponta.

O conteúdo de cada skill (`SKILL.md` + `references/`) é espelhado a partir de `.codex/skills/` quando existe um equivalente lá — hoje `exlibris-testing`, `exlibris-ci` e `exlibris-migration` existem apenas em `.claude/`. Como os harnesses mantêm cópias independentes, qualquer mudança de convenção (branch, commit, checklist de review) deve ser replicada nos dois lugares até que isso seja consolidado em uma fonte única; skills novas não precisam necessariamente de um espelho em `.codex/` a menos que o fluxo do Codex também vá usá-las.

## Modelo operacional

1. Arquiteto (`exlibris-architect`)
   Use quando a tarefa mexe em fronteiras de módulo, novas integrações, API futura, troca de storage ou mudança de stack. Devolve uma proposta, não a implementação.

2. Executor (`exlibris-executor`)
   Use para implementar a mudança já escopada, mantendo a entrega pequena e revisável.

3. Testador (`exlibris-tester`)
   Use para adicionar ou expandir testes automatizados de um módulo, ou fechar um bug fix com um teste de regressão.

4. Corretor de bugs (`exlibris-bugfix`)
   Use para um bug reportado ou reproduzido: reproduz, isola por camada, corrige, adiciona teste de regressão e entrega.

5. Revisor (`exlibris-reviewer`)
   Use antes de abrir PR ou quando quiser uma leitura crítica de regressão. Não edita arquivos.

`exlibris-ci` e `exlibris-migration` não têm agente dedicado — são skills de uso pontual, aplicadas diretamente pelo executor quando a tarefa exige CI ou migração de schema.

Para tarefas simples, invocar a skill diretamente (sem subagente) também é válido — os agentes existem para isolar o papel em um subcontexto próprio quando isso ajuda.

## Padrões de trabalho

- Branches no padrão Gitflow: `feature/<area>-<intent>`, `fix/<area>-<intent>`, `hotfix/<area>-<intent>`, `release/<versao>`, `docs/<area>-<intent>`, `refactor/<area>-<intent>`, `test/<area>-<intent>` ou `chore/<area>-<intent>`. Partem de `develop`, exceto `hotfix/*`, que parte de `main`.
- Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`.
- PRs: devem explicar mudança, motivação, verificação e risco residual.

Essas convenções são as mesmas do harness do Codex (`docs/codex-harness.md`) e do [CONTRIBUTING.md](../CONTRIBUTING.md) — os três devem permanecer consistentes.

## Sequência prática por tarefa

1. Se a mudança é estrutural, começar com a skill/agent `exlibris-architecture` / `exlibris-architect`.
2. Se é a correção de um bug, usar `exlibris-bugfix` diretamente (ele já invoca architecture e testing internamente).
3. Implementar com `exlibris-delivery` / `exlibris-executor`.
4. Cobrir com testes usando `exlibris-testing` / `exlibris-tester`.
5. Se a tarefa envolve schema SQLite, aplicar `exlibris-migration` antes de implementar.
6. Se a tarefa envolve CI, aplicar `exlibris-ci`.
7. Revisar com `exlibris-pr-review` / `exlibris-reviewer`.
8. Abrir PR com o template do repositório.

## Próximos passos úteis

- Consolidar os `references/*.md` de arquitetura, delivery e review em uma fonte única compartilhada entre `.codex/` e `.claude/`, em vez de cópias paralelas.
- Decidir se `exlibris-testing`, `exlibris-ci` e `exlibris-migration` devem ganhar um espelho em `.codex/skills/` ou permanecer específicas do Claude.
- Uma vez que `exlibris-testing` esteja em uso, considerar adicionar de fato o workflow de CI (`exlibris-ci`) e o grupo de dependências `dev` em `pyproject.toml` — hoje as skills só orientam, não fazem essa mudança no código.
