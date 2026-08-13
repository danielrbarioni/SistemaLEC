# Design: Restringir Criação de Usuários para o Perfil NENHUM

## Architecture Overview
Ajuste nas permissões de criação de usuário no frontend (Vue 3) e backend (FastAPI), garantindo que o perfil `NENHUM` não consiga emitir solicitações de criação e que o perfil `NENHUM` não seja oferecido nem aceito como alvo para novos cadastros de usuários.

## Design Details

### 1. Frontend (`Perfis.vue`)
- Ocultar o card/seção de criação e solicitação de usuário quando o perfil ativo do usuário logado for `NENHUM` ou `OBSERVADOR`.
- Filtrar a lista de perfis nos dropdowns/selects do formulário de criação de usuário para excluir a opção `NENHUM` / `OBSERVADOR`.

### 2. Backend (`src/routers/usuario.py`)
- Em `create_usuario` e `create_solicitacao`:
  - Verificar a role do usuário solicitante (`creator_role`). Se for `NENHUM` ou `OBSERVADOR`, lançar HTTP 403 Forbidden.
  - Verificar o perfil alvo (`target_profile.tipo` ou `user_in.perfil_id`). Se for `NENHUM` ou `OBSERVADOR`, lançar HTTP 400 Bad Request com a mensagem de que não é permitido criar ou solicitar usuários com perfil NENHUM.
