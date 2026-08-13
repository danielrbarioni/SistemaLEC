# Design: Restringir Perfil 'OBSERVADOR' (Renomeado para 'NENHUM') e Registrar Solicitações no Histórico

## Architecture Overview
O Sistema LEC possui frontend em Vue 3 + Vite e backend FastAPI. Esta mudança afeta as definições de permissão/rotas, controle de navegação visual, middlewares/guards de rota e o serviço de auditoria/histórico.

## Design Details

### 1. Renomeação de OBSERVADOR para NENHUM
- Atualizar as constantes de perfil no sistema (ex.: em seeders/constantes de perfil ou tabela de perfis) trocando o nome `OBSERVADOR` por `NENHUM`.
- Atualizar scripts de inicialização de perfil padrão para registrar `NENHUM`.

### 2. Restrição de Menus e Guardas de Rota para Perfil 'NENHUM'
- **Frontend Menu Navigation**:
  - Na navegação do Vue (componente de Sidebar / Navbar), verificar o perfil ativo.
  - Para o perfil `NENHUM`, apenas a opção de menu **Perfis** deve ser visível e selecionável.
  - Ocultar/desabilitar: Comunicação LEC, Navegação, Pacientes e Histórico.
- **Navigation Guard / Interceptação**:
  - No Vue Router (e nos endpoints da API quando aplicável), se um usuário com perfil `NENHUM` tentar navegar via URL ou requisição para rotas proibidas (Comunicação LEC, Navegação, Pacientes, Histórico), a ação deve ser bloqueada.
  - Exibir um alerta/toast com a mensagem exata:
    `Solicite criação de usuário e associação a um perfil, no menu Perfis`

### 3. Registro no Histórico (Auditoria)
- Nos controllers/serviços responsáveis pela criação e aprovação de solicitações de usuário e solicitações de perfil:
  - Adicionar chamadas para o repositório/serviço de Histórico.
  - Registrar eventos com ações como: `CRIAÇÃO_SOLICITAÇÃO_USUÁRIO`, `APROVAÇÃO_SOLICITAÇÃO_USUÁRIO`, `CRIAÇÃO_SOLICITAÇÃO_PERFIL`, `APROVAÇÃO_SOLICITAÇÃO_PERFIL`.
  - Garantir que o módulo de Histórico persista estes eventos no banco de dados.

### 4. Preservação dos Dados da VM e Localhost
- As alterações de banco de dados devem ser aplicadas através de queries idempotentes ou migrations seguras sem realizar `drop database`, `truncate` ou recreação destrutiva de tabelas de pacientes/atendimentos.
