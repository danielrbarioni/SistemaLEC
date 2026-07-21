## Context

Currently, the active profile (`perfilAtivoId`) in Vue 3 Pinia store `usePerfisStore` can be freely modified by any user using the profile dropdown in the top header (`DefaultLayout.vue`) or the "Ativar Perfil" button in `Perfis.vue`. Non-admin users are supposed to operate under their assigned profile.

## Goals / Non-Goals

**Goals:**
- Only allow ADMIN users to change active profile.
- Restrict non-ADMIN users to their assigned profile by hiding profile switcher controls (header dropdown and "Ativar Perfil" button on Perfis page) and ensuring `setPerfilAtivo` only allows changes when the user is an ADMIN.
- Automatically set non-ADMIN users' active profile to their assigned profile matching their username/AD user when loading perfis or authenticating.

**Non-Goals:**
- Changing backend authentication endpoints or LDAP group sync mechanism.

## Decisions

1. **Frontend Permission Check (`canSwitchProfile`)**:
   - In `useAuthStore`, `isAdmin` checks if the logged-in user has the admin group. In `usePerfisStore`, or in components, we check `authStore.isAdmin` (or if `perfilAtivo.tipo === 'ADMIN'`).
   - If a user is not an ADMIN (`!authStore.isAdmin`), `canSwitchProfile` returns false.

2. **Header Dropdown (`DefaultLayout.vue`)**:
   - Wrap the top header profile dropdown in `v-if="authStore.isAdmin"`. If not an ADMIN, show a static badge displaying the active profile name instead of a select dropdown.

3. **Perfis Page (`Perfis.vue`)**:
   - Wrap the "Ativar Perfil" button with `v-if="authStore.isAdmin"`.

4. **Auto-Binding Active Profile**:
   - When `fetchPerfis()` is called or upon auth load, if the logged in user is not an ADMIN, locate the user record corresponding to `authStore.user.username` and set `perfilAtivoId` to that user's `perfil_id`.

## Risks / Trade-offs

- **[Risk]** Non-ADMIN user has no registered profile in the database.
  → **Mitigation**: Fallback to standard default profile assignment and notify or log warning.
