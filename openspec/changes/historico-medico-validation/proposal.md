## Why

Atualmente no menu Histórico, a coluna de usuário pode cair para valores genéricos ou perfilexecutor se não configurada corretamente, precisando exibir com precisão o nome/username Ebserh cadastrado do usuário executor da ação.
Além disso, no menu Sistema LEC (Interações LEC), a inclusão ou alteração de solicitações permite a digitação livre do Médico Responsável. Para garantir a consistência e conformidade assistencial, o Médico Responsável deve ser validado contra a lista de médicos cadastrados no sistema com perfil ativo na respectiva especialidade selecionada.

## What Changes

- **Menu Histórico**:
  - Garantir que a coluna "Usuário Executor" exiba com exatidão o nome/username cadastrado do usuário Ebserh responsável pela ação (ex: `user.givenName` / `user.username` / nome no perfil), sem utilizar o nome do perfil executor como fallback indesejado.

- **Menu Sistema LEC (Interações LEC)**:
  - Ao incluir ou editar uma solicitação no formulário de Interações LEC, o campo "Médico Responsável" deve ser selecionado a partir de (ou validado contra) a lista de médicos cadastrados que possuem perfil associado à especialidade selecionada.
  - Se for digitado ou enviado um nome fora da lista de médicos autorizados/cadastrados para aquela especialidade, o sistema deve bloquear o envio e notificar um erro claro.

## Capabilities

### New Capabilities
- `historico-usuario-exibicao`: Exibição exata do nome/username do usuário Ebserh executor no menu Histórico.
- `medico-responsavel-validacao`: Validação estrita do Médico Responsável contra médicos cadastrados na especialidade no formulário do Sistema LEC.

### Modified Capabilities
(Nenhuma)

## Impact

- **Frontend**: `frontend/src/views/Historico.vue`, `frontend/src/views/InteracoesLec.vue`, `frontend/src/stores/perfis.ts`, `frontend/src/stores/auth.ts`, `frontend/src/services/api.ts`.
- **Backend**: `src/routers/solicitacao.py`, `src/controllers/solicitacao_controller.py`, `src/providers/implementations/solicitacao_sqlite_provider.py`, `src/providers/implementations/solicitacao_csv_provider.py`, `src/routers/usuario.py`.
