## Why

Esta proposta visa aprimorar o módulo de gerenciamento de Perfis no Sistema LEC, otimizando a experiência do usuário e implementando regras estritas de segurança, novos filtros, suporte a Funções para usuários de especialidades e um fluxo descentralizado de solicitação de criação de usuários para o perfil de ESPECIALIDADE com fluxo de aprovação por ADMIN e GESTÃO LEC.

## What Changes

- **Reordenação de Seções**: Posicionamento da seção "Criar Novo Perfil" (restrita a ADMIN e GESTÃO LEC) acima da seção "Criar Usuário" / "Solicitar Criação de Usuário".
- **Visualização de Usuários Locais Cadastrados**:
  - Usuários do perfil ESPECIALIDADE só visualizam usuários da sua própria especialidade (filtro obrigatório).
  - Adicionados filtros por Especialidade, Função e Nome.
  - Para ADMIN e GESTÃO LEC, adicionado filtro adicional por Perfil ID.
  - Nova coluna "Função" exibindo Médico, Residente ou Enfermeiro (válido para usuários vinculados a uma especialidade).
- **Criação e Solicitação de Usuários**:
  - Para ADMIN e GESTÃO LEC, a seção mantém o nome "Criar Usuário". Caso selecionado um Perfil de Acesso do tipo Especialidade, exibe um campo de seleção da Função (Médico, Residente, Enfermeiro).
  - Para o perfil ESPECIALIDADE, a seção é renomeada para "Solicitar Criação de Usuário". O perfil de acesso fica fixado e desabilitado na especialidade correspondente. O envio cria uma solicitação pendente de aprovação.
  - Para ADMIN e GESTÃO LEC, a interface exibe duas abas: "Criar Usuário" e "Solicitações de Criação de Usuário".
  - A aba "Solicitações de Criação de Usuário" permite aprovar ou rejeitar solicitações. O número de solicitações pendentes gera um alerta vermelho com contador no menu e no cabeçalho da aba.

## Capabilities

### Modified Capabilities
- `profile-creation-rules`: Reordenação do layout exibindo "Criar Novo Perfil" acima de "Criar Usuário".
- `user-creation`: Implementação de fluxos de criação de usuários com Funções, fluxo de solicitação de criação por especialidades, e interface de aprovação/rejeição com abas e notificações de alertas para ADMIN e GESTÃO LEC.

## Impact

- Modificações no frontend (`frontend/src/views/Perfis.vue`) para suporte às duas abas, novos filtros, e campos dinâmicos de Função.
- Novos endpoints no backend (`src/routers/usuario.py`) para listar, criar, aprovar, rejeitar e contar solicitações de criação de usuários.
- Atualização do modelo de dados (`src/models/usuario.py`) para armazenar a Função e o estado da solicitação de criação de usuários.
