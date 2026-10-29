# Proposal

## Why

No banco de dados do AGHU (`agh.aip_pacientes`), alguns pacientes possuem `nome_social` cadastrado além do nome civil (`nome`). Para garantir o respeito à identidade do paciente e a conformidade com as normas institucionais e legais de uso do nome social no SUS/Ebserh, o sistema Comunicação Cirúrgica deve apresentar o nome social em substituição ao nome civil original sempre que ele existir no AGHU, indicando claramente que se trata do Nome Social em todos os menus, formulários, tabelas, modais e relatórios.

## What Changes

- **Consultas ao AGHU e Provedores de Pacientes**:
  - Atualizar as queries SQL (`obter_paciente.sql`, `listar_pacientes.sql`, `HybridPacienteProvider.listar_pacientes` e `excel_import_helper.py`) para consultar a coluna `nome_social` na tabela `agh.aip_pacientes`.
  - Sempre que `nome_social` estiver preenchido (não nulo e não vazio), substituir o campo `nome` retornado pela API pelo nome social acrescido da indicação `(Nome Social)` (ex.: `MARIA DA SILVA (Nome Social)`), além de expor metadados auxiliares (`nome_social`, `possui_nome_social: true`) sem exibir o nome civil original.
- **Sincronização em Solicitações e Histórico (Backend)**:
  - Garantir na criação, edição e listagem de solicitações (`solicitacao_controller.py` e `routers/solicitacao.py`) que o `nome_paciente` utilize o nome social formatado com a indicação `(Nome Social)` quando o paciente possuir nome social no AGHU.
- **Exibição em Todos os Menus e Campos de Nome (Frontend)**:
  - **Menu Solicitações LEC (`InteracoesLec.vue`)**: Ao buscar um prontuário em qualquer aba (`Solicitar Inclusão`, `Solicitar Edição`, `Solicitar Standby`, `Solicitar Exclusão`), preencher o campo de nome do paciente com o nome social e a indicação `(Nome Social)` (além de badge visual indicativo), bem como exibir na tabela de Acompanhamento das Solicitações e nos modais de detalhes, rejeição e cancelamento.
  - **Menu Pacientes (`Pacientes.vue`)**: Exibir o nome social com a indicação `(Nome Social)` na tabela principal de pacientes/procedimentos e no cabeçalho/detalhes do modal do paciente.
  - **Menu Histórico (`Historico.vue`)**: Exibir o nome social com a indicação `(Nome Social)` na listagem do histórico de ações, no modal de detalhes da ação e na exportação para planilha Excel (`.xlsx`).
  - **Demais telas de listagem (`NavegacaoLec.vue`, `EspecialidadesLec.vue`, `CentralMarcacao.vue`)**: Garantir que os campos de nome reflitam a mesma padronização.

## Capabilities

### New Capabilities
- `patient-social-name`: Priorização e exibição padronizada do Nome Social do paciente (com indicação explícita de que se trata do nome social e substituição do nome civil original) em todas as consultas ao AGHU, endpoints de API e interfaces de usuário (Solicitações LEC, Pacientes, Histórico e exportações).

### Modified Capabilities
- `patient-autofetch`: Atualização do requisito de autopreenchimento de dados do paciente por prontuário para priorizar o nome social (com indicação de Nome Social) quando cadastrado no AGHU.
- `patient-demographics-aghu`: Inclusão do tratamento de `nome_social` nos dados demográficos provenientes da tabela `agh.aip_pacientes`.

## Impact

- **Backend (`src/`)**:
  - `src/providers/sql/paciente/obter_paciente.sql`
  - `src/providers/sql/paciente/listar_pacientes.sql`
  - `src/providers/implementations/paciente_postgres_provider.py`
  - `src/providers/implementations/paciente_hybrid_provider.py`
  - `src/providers/implementations/paciente_sqlite_provider.py`
  - `src/models/paciente.py` e `src/main.py` (coluna opcional `nome_social` no SQLite local)
  - `src/controllers/solicitacao_controller.py` e `src/routers/solicitacao.py`
  - `src/helpers/excel_import_helper.py`
- **Frontend (`frontend/src/`)**:
  - `frontend/src/views/InteracoesLec.vue`
  - `frontend/src/views/Pacientes.vue`
  - `frontend/src/views/Historico.vue`
  - `frontend/src/views/NavegacaoLec.vue`

