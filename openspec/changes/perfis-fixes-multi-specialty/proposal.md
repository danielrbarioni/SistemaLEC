## Why

Durante a utilização real do sistema pelos usuários, foram identificados 3 pontos críticos de usabilidade e integridade no Menu Perfis:
1. A tabela de "Usuários Locais Cadastrados" passou a apresentar barra de rolagem horizontal desnecessária, prejudicando a visualização de colunas fundamentais.
2. Médicos que atuam em mais de uma especialidade não conseguiam ser cadastrados com o mesmo login em especialidades distintas devido a uma restrição global de unicidade por `username`, além de não haver mecanismo para que esses usuários alternem seu perfil ativo (da mesma forma que administradores fazem).
3. Usuários foram bloqueados ao tentar cadastrar novas especialidades devido a colisões de chave primária (`id`) decorrentes de edições anteriores de nomes de especialidades e ausência de verificação de existência do `id` do perfil.

Esta mudança resolve essas dores estruturais para permitir a operação plena dos profissionais com múltiplas especialidades e garantir uma experiência de navegação limpa e estável no gerenciamento de acessos.

## What Changes

- **Layout e Responsividade da Tabela de Usuários**:
  - Reestruturação do layout da tela de Perfis para que a tabela de "Usuários Locais Cadastrados" ocupe a largura ideal e exiba todas as suas colunas (Nome / Username, Perfil ID, Especialidade, Função, Ações) sem barra de rolagem lateral horizontal.
- **Suporte a Usuários Multi-Especialidade e Alternância de Perfil**:
  - Atualização do modelo e tabela `usuarios` no SQLite para que a restrição de unicidade seja composta `(username, perfil_id)`, permitindo que um mesmo profissional seja cadastrado em mais de uma especialidade/perfil.
  - Atualização dos endpoints de criação, edição e solicitações de usuários para validar duplicidade apenas no par `(username, perfil_id)`.
  - Atualização da autenticação e login (`auth.py`) para coletar todos os perfis associados ao `username` logado e permitir a seleção do perfil inicial ou alternância dinâmica.
  - Disponibilização do recurso de alternância de perfil (seletor de perfil ativo no topo da tela e no menu Perfis) para qualquer usuário que possua mais de 1 perfil cadastrado (ou perfil ADMIN).
- **Criação e Gestão Resiliente de Perfis / Especialidades**:
  - Correção no endpoint `POST /api/perfis` para verificar e tratar colisões no identificador primário (`id`), além do nome da especialidade.
  - Sanitização robusta e geração segura de IDs únicos (slug normalizado sem acentos ou com sufixo quando necessário).
  - Retorno de mensagens de erro claras e amigáveis no frontend caso ocorram inconsistências.

## Capabilities

### New Capabilities
- `multi-specialty-users`: Permite o vínculo de um mesmo login a múltiplos perfis/especialidades e a alternância de perfil ativo no cabeçalho e menu Perfis.
- `perfis-table-layout`: Otimiza a visualização e largura da tabela de usuários cadastrados, eliminando a rolagem horizontal indesejada.
- `profile-creation-resilience`: Garante integridade, sanitização e unicidade na criação e edição de perfis de especialidades sem falhas de colisão de chave primária.

### Modified Capabilities
- `user-creation`: Atualiza os requisitos de criação/edição/solicitação de usuários para validar a unicidade por `(username, perfil_id)` ao invés de `username` isolado.
- `profile-creation-rules`: Atualiza os requisitos de validação e geração de ID de perfis para prevenir colisões decorrentes de edições prévias.

## Impact

- **Backend**:
  - `src/models/user.py`: Alteração da restrição única para `UniqueConstraint('username', 'perfil_id')`.
  - `src/routers/usuario.py`: Ajuste das validações de duplicidade em `/api/usuarios` (POST, PUT e `/solicitacoes`).
  - `src/routers/perfil.py`: Ajuste da geração de `id` e validações em `/api/perfis` (POST e PUT).
  - `src/auth/auth.py`: Retorno da lista de perfis disponíveis do usuário no login e suporte à seleção/alternância de perfil.
  - Migração de banco de dados para atualizar tabela `usuarios` mantendo 100% dos dados existentes.
- **Frontend**:
  - `frontend/src/views/Perfis.vue`: Reorganização de layout para visualização ampla e sem scroll lateral; habilitação do botão "Ativar Perfil" para usuários com múltiplos vínculos.
  - `frontend/src/stores/auth.ts` e `frontend/src/stores/perfis.ts`: Gerenciamento de múltiplos perfis do usuário logado e persistência do perfil selecionado.
  - `frontend/src/components/Header.vue` / `frontend/src/components/Sidebar.vue`: Exibição do seletor de perfil ativo quando o usuário possuir mais de 1 perfil vinculado.
