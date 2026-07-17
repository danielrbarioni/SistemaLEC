## Context

Currently, profiles can only be created by `ADMIN` or `GESTAO_LEC` roles. However, there are no endpoints or UI elements to edit or delete existing profiles. We need to introduce endpoints for editing/deleting profiles and protect them with hierarchical permissions.

## Goals / Non-Goals

**Goals:**
- Implement `PUT /api/perfis/{id}` to edit profiles.
- Implement `DELETE /api/perfis/{id}` to delete profiles.
- Add hierarchical role checks on the backend for both operations.
- Update `frontend/src/views/Perfis.vue` to allow authorized users to edit and delete profiles in the UI.

**Non-Goals:**
- Modifying the SQLite schema of the `Profile` model (the current structure has `id`, `nome`, `tipo`, `cor`, `especialidade`).

## Decisions

### 1. Endpoint Authorization Logic
We will implement the following permission rules in the backend:
- **ADMIN**: Can edit or delete any profile.
- **GESTAO_LEC**: Can only edit or delete profiles where `tipo == "ESPECIALIDADE"`.
- **ESPECIALIDADE**: Denied for all edit/delete profile operations.

*Alternative considered:* Relying purely on frontend hiding. Rejected because backend-enforced API security is critical.

### 2. Deletion Guard (Integrity Check)
When deleting a profile, we must verify if there are any local users associated with it.
- If users are associated, the deletion MUST be blocked, returning HTTP 400 Bad Request with: `"Não é possível excluir um perfil associado a usuários."`.

### 3. Frontend Actions in Perfis.vue
- Display edit and delete icons/buttons next to each profile in the "Perfis Disponíveis" card.
- Apply conditional visibility:
  - If role is `ADMIN`, show edit/delete for all profiles (except maybe self-protection or just keep it simple).
  - If role is `GESTAO_LEC`, show edit/delete only for profiles of type `ESPECIALIDADE`.
  - If role is `ESPECIALIDADE`, hide edit/delete actions completely.
- Use a modal or inline form to support editing a profile. Since the profile creation form only has the "Especialidade" name, profile editing will let users update the specialty name (which updates `nome` and `especialidade` accordingly).

## Risks / Trade-offs

- **[Risk]**: Deleting a profile while users are still assigned would break database references.
  - **Mitigation**: Add a DB query check before deletion and return an explicit validation error.
