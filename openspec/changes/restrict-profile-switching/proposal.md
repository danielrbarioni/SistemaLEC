## Why

Currently, any authenticated user can change their active profile via the profile selector UI or the "Ativar Perfil" button on the Perfis page, overriding their assigned profile. Restricting profile switching to ADMIN users ensures that non-ADMIN users remain bound strictly to their assigned profile permissions and responsibilities.

## What Changes

- **Profile Switcher UI Restriction**: Hide or disable profile switching controls (in the header dropdown and on the Perfis view) for non-ADMIN users.
- **Enforce Assigned Profile for Non-ADMIN Users**: Non-ADMIN users will automatically be locked to the profile corresponding to their registered user profile (or default assigned profile), disabling manual switching.
- **ADMIN Unrestricted Switching**: Maintain full ability for ADMIN users to activate and switch between any profile for testing, debugging, and management purposes.

## Capabilities

### New Capabilities
- `restrict-profile-switching`: Restricts active profile selection so that only ADMIN users can switch profiles, while non-ADMIN users are restricted to their registered profile.

### Modified Capabilities
<!-- None -->

## Impact

- **Frontend**:
  - `frontend/src/layouts/DefaultLayout.vue`: Restrict header profile selector visibility to `authStore.isAdmin`.
  - `frontend/src/views/Perfis.vue`: Hide or disable "Ativar Perfil" buttons for non-ADMIN users and ensure `perfilAtivoId` aligns with the user's assigned profile.
  - `frontend/src/stores/perfis.ts`: Add logic/helpers to restrict `setPerfilAtivo` or resolve default profile based on the logged-in user's assigned profile.
