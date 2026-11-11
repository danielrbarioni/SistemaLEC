# Proposal: Ajustes no Filtro de Ação e Registro de Edição de Perfil no Histórico (`ajuste-filtro-acao-historico`)

## Why
No menu **Histórico**, o filtro **Ação** (`#filtroAcaoTipo`) atualmente exibe a opção `Solicitação APA` (`SOLICITAR_APA`), que não é mais utilizada no sistema e deve ser retirada.
Além disso, no grupo **Menu Usuários**, existem as opções `Criação de Perfil` (`CRIAR_PERFIL`) e `Exclusão de Perfil` (`EXCLUIR_PERFIL`), mas falta a ação **`Edição de Perfil` (`EDITAR_PERFIL`)**, tanto no filtro e na formatação/badge do histórico (mesmo fundo lilás dos perfis, com letra azul, seguindo o padrão visual das ações de edição de Usuário e Categorização) quanto no registro de auditoria do backend quando um perfil é editado.

## What Changes
1. **Remoção de `Solicitação APA` do filtro Ação no menu Histórico**:
   - Retirar `<option value="SOLICITAR_APA">Solicitação APA</option>` do seletor `#filtroAcaoTipo` em `frontend/src/views/Historico.vue`.
2. **Inclusão de `Edição de Perfil` (`EDITAR_PERFIL`) no menu Histórico e Backend**:
   - Adicionar `<option value="EDITAR_PERFIL">Edição de Perfil</option>` no `<optgroup label="Menu Usuários">` do filtro **Ação** em `frontend/src/views/Historico.vue`.
   - Adicionar o mapeamento `'EDITAR_PERFIL': 'Edição de Perfil'` em `formatarTipo` e a estilização com fundo lilás e letra azul (`bg-purple-100 text-blue-800 border border-purple-300`) em `getTipoBadgeClass`, além de incluir `EDITAR_PERFIL` na ordenação de prioridade de perfis em `Historico.vue`.
   - Registrar o evento `EDITAR_PERFIL` no histórico em `PUT /api/perfis/{perfil_id}` (`src/routers/perfil.py`) via `registrar_evento_historico`, informando os detalhes da edição realizada.

## Capabilities

### New Capabilities
- `ajuste-filtro-acao-historico`: Atualização das opções do filtro Ação no menu Histórico (remoção de `Solicitação APA` e inclusão de `Edição de Perfil` com badge de fundo lilás e letra azul) e registro automático de eventos `EDITAR_PERFIL` ao editar perfis.

### Modified Capabilities
- Nenhuma capability anterior conflitante.

## Impact
- **Frontend (`frontend/src/views/Historico.vue`)**: Ajuste no `<select id="filtroAcaoTipo">`, `formatarTipo`, `getTipoBadgeClass` e `getPriority`.
- **Backend (`src/routers/perfil.py`)**: Chamada a `registrar_evento_historico` com `tipo="EDITAR_PERFIL"` em `update_perfil`.

