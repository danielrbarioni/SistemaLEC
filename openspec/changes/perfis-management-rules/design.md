## Context

O gerenciamento de perfis e a criação de usuários locais no Sistema LEC necessitam de regras de segurança aprimoradas, flexibilidade na atribuição de funções (médico, residente, enfermeiro) para usuários de especialidades, e um fluxo de solicitação e aprovação para criação de usuários.

## Goals / Non-Goals

**Goals:**
- Implementar a reordenação visual colocando "Criar Novo Perfil" acima de "Criar Usuário" / "Solicitar Criação de Usuário".
- Adicionar coluna "Função" e suporte a filtros de Especialidade, Função, Nome (e Perfil ID para ADMIN/GESTÃO LEC) na tabela de Usuários Cadastrados.
- Permitir que usuários com perfil de ESPECIALIDADE visualizem apenas usuários de sua própria especialidade (filtro obrigatório).
- Criar fluxo de solicitações pendentes de criação de usuário para perfis de ESPECIALIDADE, e abas para aprovação/rejeição destas solicitações por ADMIN e GESTÃO LEC.
- Gerar alertas visuais (badges com contadores) baseados nas solicitações pendentes no menu e nas abas de Perfis.

**Non-Goals:**
- Não serão alteradas outras tabelas além de `usuarios` e a nova tabela/modelo para solicitações de criação de usuário.
- Não haverá alteração nos perfis base (ADMIN, GESTÃO LEC) a não ser os novos filtros e fluxos de aprovação descritos.

## Decisions

### 1. Modelo de Dados e Banco de Dados (SQLite)
Adicionar o campo `funcao` (nullable String, valores: "Médico", "Residente", "Enfermeiro") ao modelo `User`.
Criar uma nova tabela/modelo `UserCreationRequest` (`solicitacoes_criacao_usuario`):
- `id` (Integer, PK)
- `username` (String, obrigatório)
- `nome` (String, obrigatório)
- `perfil_id` (String, obrigatório)
- `funcao` (String, opcional)
- `status` (String, padrão: "PENDENTE", valores: "PENDENTE", "APROVADO", "REJEITADO")
- `especialidade` (String, opcional)
- `created_at` (DateTime)

*Alternativa considerada*: Salvar as solicitações direto na tabela `usuarios` com status `INATIVO`.
*Motivo da decisão*: Manter uma tabela dedicada de solicitações evita misturar usuários não aprovados ou rejeitados na tabela principal de usuários ativos e simplifica consultas de auditoria/aprovação.

### 2. Rotas do Backend (`src/routers/usuario.py`)
Novos endpoints:
- `GET /api/usuarios/solicitacoes` (Apenas ADMIN/GESTÃO LEC): Lista solicitações pendentes.
- `GET /api/usuarios/solicitacoes/count` (Todos os autenticados): Retorna a contagem de solicitações pendentes.
- `POST /api/usuarios/solicitacoes` (Autenticado): Cria uma solicitação pendente de usuário.
- `POST /api/usuarios/solicitacoes/{id}/aprovar` (Apenas ADMIN/GESTÃO LEC): Aprova uma solicitação e cria o usuário.
- `POST /api/usuarios/solicitacoes/{id}/rejeitar` (Apenas ADMIN/GESTÃO LEC): Rejeita uma solicitação.

### 3. Frontend (`frontend/src/views/Perfis.vue`)
- Reordenar seções: Seção de criação de Perfil fica no topo.
- Adicionar abas dinâmicas ("Criar Usuário" e "Solicitações de Criação de Usuário") se o perfil logado for ADMIN ou GESTÃO LEC.
- Campo de "Função" (select com Médico, Residente, Enfermeiro) condicionado a seleção de perfil Especialidade no formulário de criação/solicitação.
- Adicionar filtros e novas colunas na tabela de Usuários Cadastrados.
- Chamar endpoint de contagem de solicitações pendentes em intervalos para atualizar o badge do menu e da aba.

## Risks / Trade-offs

- **[Risco]** Sobrecarga de chamadas periódicas para contar solicitações pendentes.
- **[Mitigação]** Fazer a contagem apenas quando a tela for carregada ou de forma otimizada com debounce em ações específicas, sem polling curto excessivo.
