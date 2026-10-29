# Tasks

## 1. Consultas ao AGHU e Provedores de Pacientes (Backend)

- [x] 1.1 Criar função utilitária `resolver_nome_paciente(nome, nome_social)` em `src/helpers/string_helper.py` que prioriza `nome_social` quando preenchido e formata como `<NOME_SOCIAL> (Nome Social)` de forma idempotente, verificando com testes rápidos de chamada Python.
- [x] 1.2 Atualizar `src/providers/sql/paciente/obter_paciente.sql` e `src/providers/sql/paciente/listar_pacientes.sql` para selecionar a coluna `nome_social` de `agh.aip_pacientes` e verificar a sintaxe SQL dos arquivos.
- [x] 1.3 Atualizar `PacientePostgresProvider` (`src/providers/implementations/paciente_postgres_provider.py`), `HybridPacienteProvider` (`src/providers/implementations/paciente_hybrid_provider.py`), `PacienteSqliteProvider` (`src/providers/implementations/paciente_sqlite_provider.py`) e `excel_import_helper.py` (`src/helpers/excel_import_helper.py`) para consultar `nome_social` e aplicar `resolver_nome_paciente`, retornando `nome` substituído pelo nome social com indicação `(Nome Social)` e `possui_nome_social`.
- [x] 1.4 Adicionar suporte opcional à coluna `nome_social` no modelo local `Paciente` (`src/models/paciente.py`) e migração automática segura em `src/main.py` (`ALTER TABLE pacientes ADD COLUMN nome_social TEXT;`), verificando que a inicialização do banco não apresenta erros.

## 2. Sincronização do Nome Social nas Solicitações e Histórico (Backend)

- [x] 2.1 Atualizar `criar_solicitacao` e `editar_solicitacao` em `src/controllers/solicitacao_controller.py` para garantir que solicitações de qualquer tipo (`INSERIR`, `EDITAR`, `STANDBY`, `EXCLUIR`) utilizem o nome resolvido pelo `paciente_provider` (com nome social e indicação `(Nome Social)` quando existir no AGHU).
- [x] 2.2 Atualizar `GET /api/solicitacoes` em `src/routers/solicitacao.py` para enriquecer o `nome_paciente` das solicitações listadas com o nome resolvido do AGHU (`paciente_provider`), garantindo que registros já existentes de pacientes com nome social passem a exibir o nome social.

## 3. Exibição e Indicação Visual no Frontend (Todos os Menus)

- [x] 3.1 Atualizar `frontend/src/views/InteracoesLec.vue` (menu `Solicitações LEC`) para exibir o nome social e um selo/indicação visual de `Nome Social` ao buscar o prontuário em `Solicitar Inclusão`, `Solicitar Edição`, `Solicitar Standby` e `Solicitar Exclusão`, bem como na tabela de Acompanhamento das Solicitações e nos modais de detalhes, rejeição e cancelamento.
- [x] 3.2 Atualizar `frontend/src/views/Pacientes.vue` (menu `Pacientes`) para priorizar o nome vindo do AGHU (com nome social) em `todosPacientesMap` e destacar visualmente a indicação de Nome Social na tabela principal e no modal de detalhes do paciente.
- [x] 3.3 Atualizar `frontend/src/views/Historico.vue` (menu `Histórico`) para priorizar o nome resolvido do AGHU no mapeamento de pacientes (`carregarHistorico`), exibir a indicação de Nome Social na tabela e no modal de detalhes da ação e manter a indicação `(Nome Social)` na exportação para Excel.
- [x] 3.4 Verificar as demais telas que exibem nomes de pacientes (`NavegacaoLec.vue`, `EspecialidadesLec.vue`, `CentralMarcacao.vue`) e realizar o build do frontend (`npm run build`) garantindo ausência de erros de compilação TypeScript/Vue.
