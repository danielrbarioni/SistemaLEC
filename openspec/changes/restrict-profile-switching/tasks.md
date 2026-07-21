## 1. Pinia Store Logic Updates

- [x] 1.1 Update `usePerfisStore` in `frontend/src/stores/perfis.ts` to automatically bind non-ADMIN users to their registered profile upon loading or fetching perfis.
- [x] 1.2 Add permission guard in `setPerfilAtivo` so profile activation can only be manually invoked if the user is an ADMIN.

## 2. UI Profile Switcher Restrictions

- [x] 2.1 Update top header in `frontend/src/layouts/DefaultLayout.vue` to hide the profile `<select>` dropdown for non-ADMIN users, rendering a static profile badge instead.
- [x] 2.2 Update `frontend/src/views/Perfis.vue` to hide the "Ativar Perfil" button for non-ADMIN users.

## 3. Verification & Testing

- [x] 3.1 Verify profile view and switching behavior when logged in as ADMIN vs non-ADMIN.
