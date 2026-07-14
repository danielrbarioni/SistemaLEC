## 1. Modelos e Estrutura de Banco de Dados

- [x] 1.1 Criar modelo SQLAlchemy para Paciente em `src/models/paciente.py`
- [x] 1.2 Criar modelo SQLAlchemy para Solicitação em `src/models/solicitacao.py`
- [x] 1.3 Criar modelo SQLAlchemy para StatusLocal em `src/models/status_local.py`
- [x] 1.4 Importar todos os modelos em `src/main.py` para criação automática das tabelas no startup

## 2. Provedores de Dados SQLite e AGHU

- [x] 2.1 Criar PacienteSqliteProvider em `src/providers/implementations/paciente_sqlite_provider.py`
- [x] 2.2 Criar SolicitacaoSqliteProvider in `src/providers/implementations/solicitacao_sqlite_provider.py`
- [x] 2.3 Atualizar fábricas de dependência em `src/dependencies.py` para instanciar provedores SQLite e conexão híbrida

## 3. Migração de Dados dos CSVs

- [x] 3.1 Desenvolver script de migração em `scratch/migrate_csv_to_sqlite.py`
- [x] 3.2 Executar migração localmente para importar os dados demográficos e de filas

## 4. Endpoints de API e Integração no Frontend

- [x] 4.1 Criar rota de busca de prontuário GET `/api/pacientes/{codigo}` no roteador do FastAPI
- [x] 4.2 Integrar o campo de prontuário em `frontend/src/views/Solicitacoes.vue` para preenchimento automático do nome
