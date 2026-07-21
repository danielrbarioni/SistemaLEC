## ADDED Requirements

### Requirement: Restrict profile switching to ADMIN users
The system SHALL only allow users with the `ADMIN` profile type (or system admin status) to manually switch their active profile in the UI.

#### Scenario: Non-ADMIN user attempts to switch profile
- **WHEN** a non-ADMIN user views the application header or Perfis page
- **THEN** profile switcher controls ("Ativar Perfil" and header selector) are hidden or disabled for them, and their active profile is locked to their assigned profile.

#### Scenario: ADMIN user switches profile
- **WHEN** an ADMIN user selects a profile from the header dropdown or clicks "Ativar Perfil" on the Perfis page
- **THEN** the system updates their active profile and updates view access accordingly.
