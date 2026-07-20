## 1. Database and Models

- [x] 1.1 Add `funcao` field to the `User` model in `src/models/user.py`
- [x] 1.2 Create the `UserCreationRequest` model in `src/models/user_creation_request.py`
- [x] 1.3 Add migrations for the new field and model using Alembic

## 2. Backend Routes

- [x] 2.1 Implement `GET /api/usuarios/solicitacoes` endpoint to retrieve pending user creation requests
- [x] 2.2 Implement `GET /api/usuarios/solicitacoes/count` endpoint for the badge counter
- [x] 2.3 Implement `POST /api/usuarios/solicitacoes` endpoint to create a request
- [x] 2.4 Implement `POST /api/usuarios/solicitacoes/{id}/aprovar` and `POST /api/usuarios/solicitacoes/{id}/rejeitar` endpoints for ADMIN/GESTÃO LEC approval workflow

## 3. Frontend Layout and Component Changes

- [x] 3.1 Reorder layouts in `frontend/src/views/Perfis.vue`: position "Criar Novo Perfil" above "Criar Usuário" / "Solicitar Criação de Usuário"
- [x] 3.2 Display the two tabs ("Criar Usuário" and "Solicitações de Criação de Usuário") dynamically for ADMIN and GESTÃO LEC profiles
- [x] 3.3 Add conditional "Função" (select list) in the creation form when an specialty profile is chosen or when requesting creation
- [x] 3.4 Rename form section to "Solicitar Criação de Usuário" and freeze/lock the access profile input to the current specialty for non-admin/non-gestão users
- [x] 3.5 Update the registered local users table to show the new "Função" column and include filters for Specialty, Function, Name (and Profile ID for admin/gestão users)
- [x] 3.6 Implement mandatory specialty filtering in the registered local users table for users with specialty profile

## 4. Alerts and Badges

- [x] 4.1 Update UI menu and headers to query and show the number of pending user creation requests in a red badge alert
