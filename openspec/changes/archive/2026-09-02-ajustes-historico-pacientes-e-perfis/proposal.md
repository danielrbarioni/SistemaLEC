## Why

No menu Histórico, as ações de importação de planilha realizadas a partir do menu Pacientes estavam sendo gravadas com a origem literal "Importação Planilha", o que impedia que fossem localizadas pelo filtro de origem/menu "Pacientes". Além disso, faltava o registro da ação de "Edição de Categorização" de profissionais com sua devida estilização (marrom claro com letra azul), o suporte a tipo de evento "Importação" (verde claro), e a garantia de que a especialidade de ações administrativas (criação/exclusão de perfis de especialidade, criação/exclusão de usuários de especialidade e categorizações) seja exibida e filtrada pela coluna Especialidade do Histórico.

## What Changes

- **Ajuste de Origem e Tipo para Importação em Pacientes**:
  - Origem / Menu: `"Pacientes"` (com suporte retroativo a registros com `"Importação Planilha"`).
  - Ação: `"Inclusão de Procedimento"` (cor verde).
  - Tipo de Evento: `"Importação"` (badge verde claro).
  - Filtro de Origem / Menu: Selecionar "Pacientes" traz todas as importações e alterações originadas na aba Pacientes.
- **Registro de Edição de Categorização de Profissional**:
  - Ação: `"Edição de Categorização"` (badge marrom claro com texto azul).
  - Tipo de Evento: `"Execução"`.
  - Descrição: Profissional + especialidade com a categorização editada (novas categorias e renomeações).
- **Exibição e Filtragem por Especialidade em Ações Administrativas**:
  - Ações de criação/exclusão de perfil com especialidade, solicitações/respostas de usuários de especialidade e ações de categorização gravam e exibem a especialidade na coluna correspondente, permitindo filtragem normal pelo seletor de Especialidade.
  - A coluna "Especialidade / Procedimento" oculta a parte de procedimento quando este for ausente ou administrativo (`"—"`).
- **Carga Retroativa de Eventos de Perfis/Categorizações**:
  - Inclusão de rotina para popular o histórico com os perfis, usuários e categorizações atualmente existentes no banco para que o histórico não fique vazio.

## Capabilities

### New Capabilities
- `historico-pacientes-importacao`: Padronização de eventos de importação de planilha sob origem "Pacientes", ação "Inclusão de Procedimento" e tipo de evento "Importação" (verde claro).
- `historico-edicao-categorizacao-e-especialidades`: Registro de edição de categorizações (marrom claro com letra azul) e exibição/filtragem universal de especialidade para ações administrativas.

### Modified Capabilities

## Impact

- **Backend**: `src/helpers/excel_import_helper.py`, `src/routers/categorizacao_profissional.py`, `src/routers/paciente.py`.
- **Frontend**: `frontend/src/views/Historico.vue`.
- **Banco de Dados**: Registros retroativos de auditoria para os perfis e categorizações existentes.
