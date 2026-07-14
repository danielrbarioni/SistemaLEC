## Why

Os menus Home, Exemplos e Admin não estão sendo utilizados no sistema e poluem a navegação lateral. Precisam ser removidos para melhorar a experiência do usuário.

## What Changes

- **Layout Lateral (Sidebar)**: Remoção das opções de navegação Home, Exemplos e Admin do menu.
- **Roteador**: Remoção das definições de rotas dos componentes excluídos e redirecionamento da rota raiz `/` diretamente para o `/interacoes` (Sistema LEC).

## Capabilities

### New Capabilities
- Nenhuma

### Modified Capabilities
- `navigation`: Remoção de links e rotas antigas/inativas.

## Impact

- **Frontend**: `DefaultLayout.vue` e `router/index.ts`.
