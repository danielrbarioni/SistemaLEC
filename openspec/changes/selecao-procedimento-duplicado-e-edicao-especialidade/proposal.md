# Proposal

## Why

Atualmente, no menu **Solicitações LEC**, existem duas limitações operacionais nas abas **Solicitar Edição**, **Solicitar Standby** e **Solicitar Exclusão**:
1. Quando um paciente possui dois ou mais registros ativos do **mesmo procedimento na mesma especialidade** (procedimento e especialidade duplicados), o sistema agrupa os registros pela chave `especialidade||procedimento` e sobrescreve as instâncias anteriores, deixando de perguntar ao usuário qual das ocorrências ele deseja editar, colocar em standby ou excluir.
2. Na aba **Solicitar Edição**, o campo **Especialidade** encontra-se permanentemente bloqueado (`disabled`), impedindo que um procedimento seja transferido de uma especialidade para outra mesmo quando o usuário possui perfil nas duas especialidades envolvidas (ou quando possui perfil `ADMIN` / `GESTÃO LEC`).

## What Changes

- **1. Seleção individualizada de procedimentos duplicados (Edição, Standby e Exclusão)**:
  - Reconstruir a lista de procedimentos ativos do paciente em `InteracoesLec.vue` preservando cada instância individual aprovada (sem sobrescrever registros que compartilham a mesma dupla `especialidade + procedimento`).
  - Exibir o seletor de procedimentos (`Qual procedimento deseja editar / excluir / colocar em standby?`) sempre que o paciente possuir mais de 1 procedimento ativo (inclusive quando forem o mesmo procedimento na mesma especialidade), diferenciando cada item por **Swalis**, **Médico Responsável** e **Data/Hora de Inserção** (além de Lateralidade e Categorização).
  - Vincular a solicitação (`EDITAR`, `STANDBY`, `CANCELAR_STANDBY`, `EXCLUIR`) à instância específica selecionada (`procedimento_alvo_id`), garantindo que a validação de duplicidade e a efetivação da aprovação atuem exclusivamente sobre a instância escolhida.

- **2. Edição de Especialidade em Solicitar Edição com controle de permissão por perfil**:
  - Habilitar o campo **Especialidade** na aba **Solicitar Edição** (`InteracoesLec.vue`) após o carregamento do paciente:
    - Perfis **`ADMIN`** e **`GESTÃO LEC`**: podem alterar a especialidade do procedimento para **qualquer especialidade** cadastrada.
    - Perfis de **`ESPECIALIDADE`**: podem alterar a especialidade do procedimento desde que o usuário logado possua perfil cadastrado **tanto na especialidade atual do procedimento (`especialidade_anterior`) quanto na especialidade de destino (`especialidade`)**; o dropdown exibirá apenas as especialidades nas quais o usuário possui perfil.
  - Registrar `especialidade_anterior` na solicitação de edição (`solicitacoes`), validar a permissão no backend (`solicitacao_controller.py`), exibir a transição `Especialidade Anterior ➔ Nova Especialidade` nas listagens/modais/histórico e propagar a mudança de especialidade ao aprovar a solicitação.

## Capabilities

### New Capabilities
- `selecao-procedimento-duplicado-e-edicao-especialidade`: Seleção individualizada de instâncias de procedimentos duplicados (diferenciados por Swalis, Médico Responsável e Data/Hora de Inserção) nas abas de Edição, Standby e Exclusão, e permissão de alteração de Especialidade na aba Solicitar Edição conforme os perfis do usuário.

### Modified Capabilities

## Impact

- **Backend**:
  - `src/models/solicitacao.py` e `src/main.py`: adição das colunas opcionais `procedimento_alvo_id` e `especialidade_anterior` na tabela `solicitacoes`.
  - `src/routers/solicitacao.py`: inclusão de `procedimento_alvo_id` e `especialidade_anterior` nos schemas `SolicitacaoCreate` e `SolicitacaoUpdate`.
  - `src/controllers/solicitacao_controller.py`: validação de permissão para alteração de especialidade (`ADMIN`, `GESTAO_LEC` ou usuário com perfil em ambas as especialidades) e ajuste na validação de duplicidade considerando `procedimento_alvo_id`.
  - `src/providers/implementations/solicitacao_sqlite_provider.py`: persistência e retorno de `procedimento_alvo_id` e `especialidade_anterior`, registro de mudança de especialidade em eventos de `ALTERACAO` e atualização da especialidade na tabela `pacientes` quando a edição é aprovada.
- **Frontend**:
  - `frontend/src/views/InteracoesLec.vue`: reconstrução de procedimentos por instância (sem colapsar duplicados), exibição de Swalis, Médico Responsável e Data de Inserção no seletor de procedimentos, habilitação condicional do dropdown de Especialidade na aba `EDITAR` restrito aos perfis do usuário, e exibição visual de `especialidade_anterior ➔ especialidade`.
  - `frontend/src/views/Pacientes.vue` e `frontend/src/views/Historico.vue`: correspondência exata por `procedimento_alvo_id` (ou fallback unitário `findIndex` + `splice` sem remover todas as cópias) e suporte a `especialidade_anterior` na reconstrução da fila e linha do tempo.
