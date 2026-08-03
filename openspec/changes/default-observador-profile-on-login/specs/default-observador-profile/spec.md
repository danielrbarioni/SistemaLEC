# Default OBSERVADOR Profile Spec

## Requirements

### Requirement: Default Profile Assignment on Login
- SHALL assign the `OBSERVADOR` profile as the default active profile for any user logging in who does not have an explicit profile record assigned in the `usuarios` table.
- SHALL clear or override any stale `perfilAtivoId` in `localStorage` upon login or logout if the logged-in user is an `OBSERVADOR` or has no custom profile.
- SHALL NOT default to `ADMIN` profile under any circumstances for non-admin or unregistered users.
- SHALL restrict read-only capabilities for users with the `OBSERVADOR` active profile across all menus (Interações LEC, Perfis, Pacientes, Histórico).
