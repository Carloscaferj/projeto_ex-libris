# Contribuindo com o Ex Libris

## Fluxo de trabalho

- Use branches curtas com o padrão `codex/<area>-<intent>`.
- Mantenha cada alteração focada em um único objetivo sempre que possível.
- Atualize documentação quando a mudança afetar CLI, arquitetura, setup ou comportamento funcional.

## Convenção de commits

Formato recomendado:

`<tipo>(<escopo-opcional>): <resumo>`

Tipos sugeridos:

- `feat`
- `fix`
- `refactor`
- `docs`
- `test`
- `chore`

Exemplos:

- `feat(cli): adicionar confirmação assistida`
- `fix(search): evitar falha com índice vazio`
- `refactor(application): separar fluxo de identificação`

## Pull requests

Todo PR deve deixar claro:

- o que mudou
- por que mudou
- como foi verificado
- quais riscos ou limites permanecem

## Organização de código

- `domain` para modelos e regras estáveis do domínio
- `application` para orquestração dos casos de uso
- `infrastructure` para SQLite, busca vetorial e ML
- `interface` para CLI e adaptação de entrada e saída

Evite mover lógica de negócio para a CLI ou para classes de infraestrutura.
