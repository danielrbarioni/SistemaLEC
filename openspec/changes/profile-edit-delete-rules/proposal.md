## Why

Implement structured, permission-based restrictions for modifying and deleting user profiles. This ensures that less privileged roles cannot escalate their permissions or disrupt the system's profile hierarchy.

## What Changes

- Implement authorization checks on profile modification and deletion endpoints:
  - **ADMIN** has full privileges to edit or delete any profile type (`ADMIN`, `GESTAO_LEC`, `ESPECIALIDADE`).
  - **GESTÃO LEC** has privileges to edit or delete only `ESPECIALIDADE` profiles.
  - **ESPECIALIDADE** cannot edit or delete any profiles.
- Expose profile edit and delete actions on the frontend according to user permissions.

## Capabilities

### New Capabilities
<!-- Capabilities being introduced. Replace <name> with kebab-case identifier (e.g., user-auth, data-export, api-rate-limiting). Each creates specs/<name>/spec.md -->

### Modified Capabilities
<!-- Existing capabilities whose REQUIREMENTS are changing (not just implementation).
     Only list here if spec-level behavior changes. Each needs a delta spec file.
     Use existing spec names from openspec/specs/. Leave empty if no requirement changes. -->
- `profile-creation-rules`: Add rules for profile edit and delete operations.

## Impact

- **Backend API**: Modifications in `src/routers/perfil.py` to add PUT and DELETE endpoints with hierarchical permission checks.
- **Frontend UI**: Modifications in `frontend/src/views/Perfis.vue` to show edit/delete actions for profiles depending on active user profile.
