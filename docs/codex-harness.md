# Codex harness do projeto Ex Libris

Este projeto passa a separar duas coisas:

- `skills`: contexto durável do projeto, reutilizável em várias tarefas.
- `agents`: papéis operacionais temporários, escolhidos conforme o tipo de trabalho.

## Estrutura recomendada

- `.codex/skills/exlibris-architecture`
  Regras para evolução de arquitetura, limites entre camadas e decisões de stack.
- `.codex/skills/exlibris-delivery`
  Convenções de branch, commit, PR e fechamento de tarefas.
- `.codex/skills/exlibris-pr-review`
  Critérios de revisão com foco em regressão, documentação e higiene de entrega.

## Modelo operacional

Use papéis simples. Não precisa criar um agente diferente para cada detalhe.

1. Arquiteto
   Use quando a tarefa mexe em fronteiras de módulo, novas integrações, API futura, troca de storage ou mudança de modelo.
   Prompt sugerido: `Use $exlibris-architecture para propor a implementação de <tarefa>.`

2. Executor
   Use para implementar a mudança e manter a entrega pequena e revisável.
   Prompt sugerido: `Use $exlibris-delivery para implementar <tarefa>.`

3. Revisor
   Use antes de abrir PR ou quando quiser uma leitura crítica de regressão.
   Prompt sugerido: `Use $exlibris-pr-review para revisar as mudanças em <arquivos ou diff>.`

## Padrões de trabalho

- Branches: `codex/<area>-<intent>`
- Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`
- PRs: devem explicar mudança, motivação, verificação e risco residual

## Sequência prática por tarefa

1. Se a mudança é estrutural, começar com `$exlibris-architecture`.
2. Implementar com `$exlibris-delivery`.
3. Revisar com `$exlibris-pr-review`.
4. Abrir PR com o template do repositório.

## Próximos passos úteis

- Adicionar testes automatizados para `CatalogRecognitionService` e fluxos de CLI.
- Criar uma skill futura de `exlibris-testing` quando houver harness de testes mais estável.
- Se o projeto ganhar API HTTP, criar uma skill específica para contrato e versionamento da interface.
