## Why

Atualmente, o menu Histórico registra apenas os envios de solicitações e não reflete com clareza as respostas/avaliações (aprovação, rejeição, etc.) executadas pelos perfis ADMIN ou GESTÃO LEC, nem indica o menu de origem em que a ação ocorreu (como Sistema LEC ou Navegação).
Ademais, a lista de especialidades no formulário do Sistema LEC utiliza um array fixo em código (*hardcoded*), o que causa inconsistências quando novas especialidades são cadastradas ou gerenciadas dinamicamente no menu Perfis.

## What Changes

- **Menu Histórico**:
  - Incluir uma nova coluna **"Origem / Menu"** posicionada logo no início da tabela, logo após a coluna "Data / Hora", indicando em qual menu/módulo a ação foi originada (ex: *Sistema LEC*, *Navegação*).
  - Exibir no histórico tanto o evento inicial da solicitação quanto os eventos de resposta (aprovação, rejeição, alteração de status) realizados pelos gestores/administradores (ADMIN / GESTÃO LEC), fornecendo uma linha do tempo completa de auditoria.

- **Menu Sistema LEC (Interações LEC)**:
  - Substituir a lista estática de especialidades pelo carregamento dinâmico obtido a partir das especialidades cadastradas no módulo de **Perfis** (`/api/perfis`).
  - Garantir que as opções disponíveis nos seletores e filtros de especialidade correspondam sempre às especialidades vigentes cadastradas no sistema.

## Capabilities

### New Capabilities
- `historico-respostas-e-origem`: Exibição de ações de resposta (ADMIN/GESTÃO LEC) e coluna de origem do menu no Histórico.
- `especialidades-dinamicas-perfis`: Carregamento dinâmico das especialidades no Sistema LEC a partir dos perfis cadastrados.

### Modified Capabilities
(Nenhuma)

## Impact

- **Frontend**: `frontend/src/views/Historico.vue`, `frontend/src/views/InteracoesLec.vue`, `frontend/src/stores/perfis.ts`, `frontend/src/services/api.ts`.
- **Backend**: `src/routers/solicitacao.py`, `src/controllers/solicitacao_controller.py`, `src/providers/implementations/solicitacao_sqlite_provider.py`, `src/providers/implementations/solicitacao_csv_provider.py`.
