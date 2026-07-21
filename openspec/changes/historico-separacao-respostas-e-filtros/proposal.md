## Why

Atualmente, ao aprovar ou rejeitar uma solicitação, o registro original é sobrescrito no banco de dados, substituindo o histórico da Solicitação inicial. O comportamento correto de auditoria exige que a Solicitação permaneça salva em sua própria linha no Histórico e que cada Resposta (aprovação ou rejeição) seja registrada como um novo evento / linha independente no Histórico.

Além disso, a busca no menu **Histórico de Solicitações/Respostas** necessita de filtros completos adicionais para permitir uma auditoria detalhada:
1. **Origem/Menu** (seletor: Todas, Sistema LEC, Navegação, etc.)
2. **Prontuário/Paciente** (campo texto para busca por prontuário ou nome)
3. **Ação/Tipo** (seletor: Todas, Inclusão, Edição, Standby, Exclusão)
4. **Solicitação ou Resposta** (seletor: Todas, Solicitação, Resposta)
5. **Status** (seletor: Todos, PENDENTE, APROVADO, REJEITADO)
6. **Usuário Executor** (campo texto para busca pelo usuário Ebserh)

## What Changes

- **Preservação de Registros & Registro de Resposta Independente**:
  - Na aprovação ou rejeição de solicitações, manter a solicitação original intacta no banco de dados com seu status e criar um novo registro no Histórico especificamente marcado como `is_resposta = True` (ou `origem_menu` correspondente), contendo a data/hora da ação, o usuário executor da avaliação e o perfil executor (ADMIN / GESTÃO LEC).
- **Ampliação dos Filtros no Histórico (`Historico.vue`)**:
  - Adicionar no topo do Histórico a grade completa com os 8 filtros:
    - Especialidade
    - Data De
    - Data Até
    - Origem / Menu
    - Prontuário / Paciente
    - Ação / Tipo
    - Solicitação ou Resposta
    - Status
    - Usuário Executor

## Capabilities

### New Capabilities
- `historico-resposta-evento-separado`: Gravação de respostas/decisões como novas linhas independentes no Histórico de auditoria, preservando as solicitações originais.
- `historico-filtros-avancados`: Disponibilização dos 8 filtros de busca no menu Histórico de Solicitações/Respostas.

### Modified Capabilities
(Nenhuma)

## Impact

- **Frontend**: `frontend/src/views/Historico.vue`, `frontend/src/views/InteracoesLec.vue`.
- **Backend**: `src/routers/solicitacao.py`, `src/controllers/solicitacao_controller.py`, `src/providers/implementations/solicitacao_sqlite_provider.py`.
