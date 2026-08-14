# Proposal: Filtros de Judicialização e Swalis no Menu Pacientes e Fluxo de Solicitação de Exclusão de Usuários

## Why
1. **Filtros no Menu Pacientes**: Atualmente, o menu **Pacientes** permite filtrar por Prontuário/Nome, Especialidade, Procedimento, Médico Responsável e Pacientes com Múltiplos Procedimentos. No entanto, as equipes operacionais e de gestão necessitam filtrar pacientes diretamente por **Judicialização** (Sim / Não) e por prioridade de classificação **Swalis** (A1, A2, B, C, D) para priorizar casos urgentes e judicializados na fila cirúrgica.
2. **Solicitação de Exclusão no Menu Perfis**: Atualmente, usuários dos perfis `EPO GENERALISTA` e `ESPECIALIDADE` conseguem criar e solicitar edição de usuários vinculados à sua especialidade, mas a exclusão de usuários era restrita ou realizada diretamente. Para garantir maior governança e controle de segurança, usuários com perfil `EPO GENERALISTA` e `ESPECIALIDADE` não devem conseguir excluir diretamente nenhum usuário. Em vez disso, ao clicar no botão **Excluir**, o sistema deve registar uma **Solicitação de Exclusão de Usuário**, exigindo a revisão e aprovação/rejeição por um usuário com perfil `ADMIN` ou `GESTÃO LEC`.

## What
1. **Menu Pacientes (`frontend/src/views/Pacientes.vue`)**:
   - Adicionar o filtro **Judicialização** (opções: `Todas`, `Sim`, `Não`).
   - Adicionar o filtro **Swalis** (opções: `Todas`, `A1 - Prioridade máxima`, `A2 - Prioridade alta`, `B - Prioridade média`, `C - Prioridade baixa`, `D - Prioridade mínima`, `Sem Swalis / Não informado`).
   - Atualizar a computação reativa de `pacientesProcessados` e `procedimentosFlat` para aplicar os novos filtros de Judicialização e Swalis de forma combinada com os filtros existentes.

2. **Menu Perfis & Backend (`frontend/src/views/Perfis.vue`, `src/routers/usuario.py`)**:
   - Atualizar o modelo de solicitações no backend (`UserCreationRequest`) e nos schemas Pydantic para aceitar o tipo `EXCLUSAO`.
   - Modificar o fluxo de exclusão no frontend: quando o perfil ativo for `EPO_GENERALISTA` ou `ESPECIALIDADE`, o clique no botão **Excluir** na lista de usuários enviará uma requisição `POST /api/usuarios/solicitacoes` com `tipo: 'EXCLUSAO'` e `user_id: user.id`.
   - No backend, validar que o solicitante possui permissão sobre a especialidade/perfil do usuário cuja exclusão está sendo solicitada.
   - Na aba **Solicitações** do menu Perfis (visível para `ADMIN` e `GESTÃO LEC`), exibir as solicitações do tipo `EXCLUSAO` com badge de destaque em vermelho (`Exclusão`).
   - Ao aprovar uma solicitação de exclusão (`POST /api/usuarios/solicitacoes/{id}/aprovar`), o backend efetuará a exclusão real do usuário no banco de dados SQLite (`User`) e atualizará o status da solicitação para `APROVADO`.
   - Ao rejeitar uma solicitação de exclusão (`POST /api/usuarios/solicitacoes/{id}/rejeitar`), a solicitação será marcada como `REJEITADO` mantendo o usuário inalterado.

## Impact
- **Frontend**: `frontend/src/views/Pacientes.vue`, `frontend/src/views/Perfis.vue`
- **Backend**: `src/models/user_creation_request.py`, `src/routers/usuario.py`
