# Tasks

## 1. Modelo de Dados e Backend (`solicitacoes`)

- [x] 1.1 Adicionar as colunas `procedimento_alvo_id` e `especialidade_anterior` em `src/models/solicitacao.py` e as migrações `ALTER TABLE solicitacoes ADD COLUMN` em `src/main.py`, verificando a criação sem erros de sintaxe
- [x] 1.2 Atualizar os schemas `SolicitacaoCreate` e `SolicitacaoUpdate` em `src/routers/solicitacao.py` e o provider `src/providers/implementations/solicitacao_sqlite_provider.py` para persistir, listar, editar e propagar `procedimento_alvo_id` e `especialidade_anterior` (incluindo a atualização de `pac_obj.especialidade` ao aprovar `EDITAR`)
- [x] 1.3 Atualizar `src/controllers/solicitacao_controller.py` para validar a permissão de alteração de especialidade (`ADMIN`, `GESTAO_LEC`, ou usuário com perfil cadastrado na especialidade anterior e na especialidade de destino) e considerar `procedimento_alvo_id` e `especialidade_anterior` na validação de duplicidade e reconstrução de procedimentos ativos

## 2. Seleção de Procedimentos Duplicados e Edição de Especialidade no Frontend

- [x] 2.1 Atualizar `buscarDados()` e o seletor de procedimentos em `frontend/src/views/InteracoesLec.vue` para manter todas as instâncias ativas de procedimentos em lista (sem sobrescrever registros com mesma especialidade e procedimento) e exibir Swalis, Médico Responsável e Data/Hora de Inserção em cada opção do seletor
- [x] 2.2 Habilitar a edição condicional do campo Especialidade na aba `Solicitar Edição` em `frontend/src/views/InteracoesLec.vue` (exibindo todas as especialidades para `ADMIN`/`GESTAO_LEC` ou apenas as especialidades nas quais o usuário possui perfil quando tiver perfil na especialidade atual e em outra(s)), enviando `procedimento_alvo_id` e `especialidade_anterior` e exibindo a transição de especialidade nas tabelas e modais
- [x] 2.3 Atualizar `frontend/src/views/Pacientes.vue` e `frontend/src/views/Historico.vue` para localizar a instância alvo por `procedimento_alvo_id` (ou fallback unitário `findIndex` + `splice` e `especialidade_anterior || especialidade`) e exibir a mudança de especialidade no histórico e linha do tempo

## 3. Verificação, Build e Deploy

- [x] 3.1 Compilar o frontend (`npm run build`) verificando zero erros de TypeScript (`vue-tsc`) e Vite
- [x] 3.2 Implantar as alterações do backend e frontend na VM de produção (`10.34.0.202`), aplicar as novas colunas no SQLite (`app.db`) e reiniciar o serviço `sistemalec.service` verificando seu status ativo
