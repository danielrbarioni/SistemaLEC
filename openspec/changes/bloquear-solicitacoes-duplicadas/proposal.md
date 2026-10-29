# Proposal

## Why

Atualmente, o sistema possui validações parciais para solicitações duplicadas que ainda permitem brechas (como ausência de bloqueio imediato no frontend para inclusão, edição e standby, comparação literal sensível a formato/ID do procedimento, e ausência de verificação direta na tabela `pacientes` ou ao editar solicitações pendentes). É necessário garantir — tanto no frontend quanto no backend — que nenhuma solicitação redundante ou conflitante seja registrada com mensagem de erro clara para a mesma dupla `paciente + procedimento`.

## What Changes

- **Bloqueio em Solicitação de Inclusão (`INSERIR`)**: Impedir o envio (exibindo mensagem de erro clara no frontend e retornando HTTP 400 no backend) quando a dupla `paciente + procedimento` (comparada de forma normalizada pelo nome base do procedimento) já existir ativamente no banco de dados (`Pacientes` / fila ativa reconstruída) **ou** quando já existir uma solicitação de inclusão (`INSERIR`) com status `PENDENTE` para a mesma dupla `paciente + procedimento`.
- **Bloqueio em Solicitação de Edição (`EDITAR`)**: Impedir o envio (com mensagem de erro no frontend e HTTP 400 no backend) para um `paciente + procedimento` que já possua uma solicitação de edição (`EDITAR`) com status `PENDENTE` (e também impedir que a edição altere o procedimento para outro que já exista para o mesmo paciente ou tenha inclusão pendente).
- **Bloqueio em Solicitação de Standby (`STANDBY` / `CANCELAR_STANDBY`)**: Impedir o envio (com mensagem de erro no frontend e HTTP 400 no backend) para um `paciente + procedimento` que já possua uma solicitação de standby pendente.
- **Bloqueio em Solicitação de Exclusão (`EXCLUIR`)**: Impedir o envio (com mensagem de erro no frontend e HTTP 400 no backend) para um `paciente + procedimento` que já possua uma solicitação de exclusão (`EXCLUIR`) com status `PENDENTE`.
- **Validação consistente também ao atualizar solicitação pendente (`PUT /api/solicitacoes/{id}`)**: Aplicar as mesmas regras de unicidade de `paciente + procedimento` ao salvar alterações em uma solicitação pendente existente (ignorando o próprio ID em edição).

## Capabilities

### New Capabilities
- `solicitacao-duplicidade-validacao`: Validação e bloqueio com mensagem de erro de solicitações duplicadas para a mesma dupla `paciente + procedimento` em Inclusão (contra banco de dados `Pacientes` e solicitações `INSERIR` pendentes), Edição (contra solicitações `EDITAR` pendentes), Standby (contra solicitações `STANDBY` pendentes) e Exclusão (contra solicitações `EXCLUIR` pendentes).

### Modified Capabilities
<!-- Nenhuma capability existente possui requisitos de validação de duplicidade de solicitações. -->

## Impact

- **Backend**:
  - `src/helpers/string_helper.py`: Função utilitária para normalizar nomes de procedimentos cirúrgicos (extraindo o nome base sem prefixo/sufixo de ID e sem acentos/caixa) para comparação exata da dupla `paciente + procedimento`.
  - `src/controllers/solicitacao_controller.py`: Reforço das validações em `criar_solicitacao` e `editar_solicitacao` consultando tanto as solicitações (`listar_solicitacoes`) quanto os pacientes cadastrados (`paciente_provider.listar_pacientes()`) para bloquear duplicidades de `paciente + procedimento` em `INSERIR`, `EDITAR`, `STANDBY` e `EXCLUIR`.
- **Frontend**:
  - `frontend/src/views/InteracoesLec.vue`: Validação preventiva imediata em `enviarSolicitacao` com exibição de mensagem de erro (`toast.error`) para os 4 casos (`INSERIR`, `EDITAR`, `STANDBY` e `EXCLUIR`) usando a comparação normalizada da dupla `paciente + procedimento`.

