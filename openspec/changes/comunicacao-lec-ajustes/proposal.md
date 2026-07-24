## Why

Ajustar a nomenclatura do menu "Sistema LEC" para "Comunicação LEC", corrigir o carregamento automático de dados demográficos do AGHU na aba de Inclusão do módulo de comunicação, restringir acesso da função Enfermeiro e conceder permissão de criação de solicitações para o perfil GESTÃO LEC.

## What Changes

- **Renomeação de Menu**: Alterar a exibição do menu de "Sistema LEC" para "Comunicação LEC" na interface e componentes correspondentes.
- **Integração AGHU / Prontuário**: Garantir que na aba "Solicitar Inclusão" do menu Comunicação LEC os dados demográficos (nome completo, data de nascimento e nome da mãe) venham do AGHU ao digitar o prontuário.
- **Controle de Acesso (Enfermeiro)**: Restringir o acesso ao menu Comunicação LEC para perfis/usuários com função Enfermeiro (exibindo aviso de funcionalidade restrita a Médicos e Residentes).
- **Permissão GESTÃO LEC**: Conceder ao perfil GESTÃO LEC acesso completo para criar solicitações no menu Comunicação LEC (Inclusão, Edição, Standby e Exclusão), mantendo a aba de acompanhamento.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `patient-demographics-aghu`: Garantir a busca e preenchimento dos dados do AGHU na aba Solicitar Inclusão.
- `profile-creation-rules`: Atualizar regras de permissões dos perfis Enfermeiro e GESTÃO LEC no menu Comunicação LEC.

## Impact

- Frontend (componentes de navegação, formulários de solicitação LEC e rotas/guardas de permissão).
- Backend (APIs de consulta de paciente/AGHU e endpoints de solicitação LEC se houver validação por role).
