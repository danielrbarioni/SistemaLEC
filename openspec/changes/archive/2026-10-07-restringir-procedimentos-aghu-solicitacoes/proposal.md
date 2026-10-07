# Proposal

## Why

Atualmente, o dropdown de procedimentos nas telas de solicitações de inclusão e edição (`InteracoesLec.vue`) agrega os procedimentos oficiais do AGHU juntamente com procedimentos históricos encontrados na base local (`extraProcs`). Isso permitiu que textos legados sem ID ou nomes não oficiais (como "CERVICAL" na Cirurgia Geral ou "PROCEDIMENTO 706") apareçam como opções selecionáveis para novos agendamentos, gerando inconsistências com as filas de procedimentos do Sistema da Sede e do AGHU.

## What Changes

- **Restrição a procedimentos oficiais do AGHU nas solicitações**: No formulário de inclusão e edição (`InteracoesLec.vue`), o campo de procedimento passa a listar exclusivamente procedimentos oficiais ativos do AGHU correspondentes à especialidade selecionada (todos contendo identificador padronizado `ID XXX`).
- **Preservação dos registros legados existentes**: Nenhum procedimento histórico gravado em solicitações ou pacientes anteriores é alterado ou renomeado; nomes existentes (mesmo sem ID ou genéricos) permanecem intactos.
- **Preservação de filtros no menu Pacientes**: O menu Pacientes (`Pacientes.vue`) continua mantendo no seu dropdown de filtro tanto os procedimentos do AGHU quanto os procedimentos históricos locais, permitindo localizar e filtrar pacientes antigos com procedimentos legados.

## Capabilities

### New Capabilities

### Modified Capabilities
- `specialty-procedures-aghu`: Restringe a oferta de opções de procedimentos cirúrgicos em novas solicitações de inclusão e edição exclusivamente ao catálogo oficial de procedimentos do AGHU para a especialidade informada.

## Impact

- **Frontend**: `frontend/src/views/InteracoesLec.vue` (ajuste na lista reativa de procedimentos oferecida no formulário para considerar estritamente o catálogo do AGHU).
- **Backend / Banco de Dados**: Nenhuma alteração estrutural; integridade dos dados históricos preservada.
