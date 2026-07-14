## Why

Atualmente, os procedimentos cirúrgicos no formulário de inserção/edição do Sistema LEC são estáticos ou mockados. Com a integração com o AGHU ativa, ao selecionar a especialidade "Plástica" (ID 1884), o sistema deve listar dinamicamente os procedimentos cadastrados e ativos no AGHU para essa especialidade específica.

## What Changes

- **Backend**:
  - Nova rota `/api/especialidades/{id_especialidade}/procedimentos` para buscar procedimentos de uma especialidade.
  - Consulta SQL ao banco PostgreSQL do AGHU (tabela `agh.mbc_procedimento_cirurgicos` combinada com especialidades) filtrando por `ind_situacao = 'A'`.
- **Frontend**:
  - Ao selecionar a especialidade "Plástica" no formulário do Sistema LEC, fazer uma requisição para a nova rota e popular o dropdown de procedimentos.

## Capabilities

### New Capabilities
- `get-specialty-procedures`: Obtenção de procedimentos ativos de uma especialidade do AGHU.

### Modified Capabilities
- `interacoes-lec`: Atualização dinâmica do dropdown de procedimentos.

## Impact

- **Banco de Dados**: Consultas somente leitura no AGHU (Postgres).
- **Frontend**: Requisição dinâmica no `InteracoesLec.vue`.
