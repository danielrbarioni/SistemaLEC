## 1. Database and Backend Support for Multi-Specialty Users

- [x] 1.1 Update `src/models/user.py` to replace single-column `unique=True` on `username` with composite `UniqueConstraint('username', 'perfil_id')`
- [x] 1.2 Create and execute a safe migration on `data/app.db` to adjust constraints on the `usuarios` table without altering existing data
- [x] 1.3 Update `src/routers/usuario.py` endpoints (`POST /api/usuarios`, `PUT /api/usuarios/{id}`, and `/api/usuarios/solicitacoes`) to validate uniqueness based on `(username, perfil_id)` instead of `username` alone

## 2. Authentication and Multi-Profile Management

- [x] 2.1 Update `src/auth/auth.py` to query all profiles linked to the logging username and include `available_profiles` and default `active_profile` in the authentication result
- [x] 2.2 Ensure JWT token or perfil router supports activating and switching between authorized profiles for the current session

## 3. Profile Creation Resilience and ID Collision Fix

- [x] 3.1 Update `src/routers/perfil.py` (`POST /api/perfis` and `PUT /api/perfis/{id}`) to sanitize string inputs, remove accents, and generate safe unique IDs
- [x] 3.2 Implement collision checks and explicit friendly error handling in `create_perfil` to prevent SQLite Primary Key 500 exceptions

## 4. Frontend Layout and Profile Switching UI

- [x] 4.1 Reorganize the visual layout in `frontend/src/views/Perfis.vue` ensuring the "Usuários Locais Cadastrados" table displays all columns comfortably with zero horizontal scrollbar
- [x] 4.2 Update `frontend/src/stores/auth.ts` and `frontend/src/stores/perfis.ts` to manage multiple profiles per user and track the active profile
- [x] 4.3 Enable the "Ativar Perfil" action in `frontend/src/views/Perfis.vue` and in the top Header for users with multiple profiles (in addition to ADMIN)

## 5. Verification and Validation

- [x] 5.1 Verify that a single username can be registered in two or more specialties and saved correctly
- [x] 5.2 Verify that a multi-specialty user can switch active profile from the UI and that queues and forms adapt accordingly
- [x] 5.3 Verify that adding new surgical specialties works reliably even with accents or previously edited profile names
- [x] 5.4 Verify that the users table displays cleanly without lateral horizontal scrolling
