## Context

Atualmente, na autenticação Active Directory (AD), se um usuário Ebserh faz login e não possui uma entrada vinculada na tabela `usuarios` do banco de dados (que define seu perfil formal entre ADMIN, GESTÃO LEC ou ESPECIALIDADE), a aplicação atribui como fallback o perfil de maior privilégio (`ADMIN`). Isso permite que novos usuários navegantes ou não mapeados tenham acesso ilimitado à gestão do sistema.

## Goals / Non-Goals

**Goals:**
- Alterar o fallback de autenticação para que usuários sem perfil explícito recebam o perfil `OBSERVADOR`.
- Garantir que o perfil `OBSERVADOR` consiga visualizar painéis, listas e detalhes no frontend, mas seja impedido no backend de realizar operações de alteração ou exclusão de dados.
- Ocultar ou desabilitar ações de criação/edição/aprovação no frontend quando o perfil ativo for `OBSERVADOR`.

**Non-Goals:**
- Criar novos fluxos de aprovação de cadastro de usuário nesta mudança.
- Alterar as permissões vigentes dos perfis existentes (`ADMIN`, `GESTÃO LEC`, `ESPECIALIDADE`).

## Decisions

### Decisão 1: Fallback do Token JWT no Backend (`src/auth/auth.py`)
- **Decisão:** Na função de autenticação/emissão de token, se a busca pelo usuário na tabela `usuarios` retornar nulo ou sem perfil atribuído, incluir `"perfil": "OBSERVADOR"` nas *claims* do JWT em vez de `"ADMIN"`.
- **Alternativa considerada:** Negar o login e retornar 403 Forbidden. *Rejeitado porque o usuário Ebserh válido deve conseguir consultar informações no sistema em modo leitura.*

### Decisão 2: Proteção de Rotas com Middleware/Dependency no FastAPI
- **Decisão:** Aplicar validação de perfil nas rotas de escrita/mutação (endpoints de POST, PUT, DELETE em solicitações, pacientes e perfis), permitindo acesso somente aos perfis `ADMIN`, `GESTÃO LEC` ou `ESPECIALIDADE` conforme o caso. O perfil `OBSERVADOR` receberá `403 Forbidden`.
- **Alternativa considerada:** Validar apenas no Frontend. *Rejeitado pois vulnerabilidades na API poderiam ser exploradas diretamente via requisições HTTP.*

### Decisão 3: Tratamento de Interface no Frontend (Vue 3 / Pinia)
- **Decisão:** Atualizar a store `perfis.ts` e `auth.ts` para reconhecer `OBSERVADOR`. As views (`NavegacaoLec.vue`, `Admin.vue`, etc.) utilizarão verificação `isObservador` para ocultar botões como "Criar Solicitação", "Aprovar", "Rejeitar", "Editar Perfil".

## Risks / Trade-offs

- **[Risco] Usuários administrativos atuais sem cadastro na tabela `usuarios` perderem acesso a funções de escrita** → *Mitigação:* Garantir que a tabela `usuarios` contenha os cadastros prévios dos administradores antes do deploy e permitir que um ADMIN cadastre formalmente os usuários.
