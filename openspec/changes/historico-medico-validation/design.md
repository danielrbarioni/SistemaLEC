## Context

No Sistema LEC, a auditoria e o acompanhamento histórico exigem precisão quanto ao Usuário Ebserh que executou cada ação. Além disso, no lançamento e edição de solicitações (Interações LEC), é necessário garantir que o Médico Responsável selecionado esteja devidamente cadastrado no sistema com o perfil vinculado à especialidade cirúrgica da solicitação.

## Goals / Non-Goals

**Goals:**
- Garantir que o campo `usuario` armazenado e exibido no menu Histórico reflita exatamente o nome/username cadastrado do Usuário Ebserh executor.
- No formulário de Interações LEC (inclusão/edição), filtrar e validar o campo Médico Responsável contra a lista de usuários cadastrados no banco/sistema que possuem perfil associado à especialidade selecionada.
- Exibir alerta/notificação de erro caso um nome inválido/fora da lista de médicos da especialidade seja submetido.

**Non-Goals:**
- Alterar o fluxo de autenticação do Active Directory / LDAP.
- Modificar permissões de acesso aos outros módulos além da validação do formulário.

## Decisions

1. **Obtenção e exibição do Usuário Executor**:
   - O frontend repassa `usuario: authStore.user?.givenName?.[0] || authStore.user?.username` no payload.
   - O backend prioriza o `displayName` ou `username` do token de autenticação caso o payload venha sem o campo.
   - O provider SQLite/CSV não faz fallback para `perfil_executor`, evitando duplicidade de rótulos.

2. **Validação do Médico Responsável no Frontend & Backend**:
   - Carregar/buscar a lista de usuários cadastrados através da API (`GET /api/users`).
   - Filtrar os médicos cadastrados cuja especialidade cadastrada coincida com a especialidade da solicitação (ou permitir escolha via datalist/select).
   - Adicionar validação no método de submit de `InteracoesLec.vue` verificando se `medico_responsavel` bate com um dos médicos cadastrados para a especialidade ativa. Se não, emitir `toast.error("O Médico Responsável selecionado não possui cadastro para a especialidade X.")`.

## Risks / Trade-offs

- **[Risk]** Dados antigos no banco de solicitações sem `usuario` preenchido.
  - *Mitigation*: O frontend continuará exibindo `—` para registros antigos sem usuário em vez de mascarar dados com o perfil executor.
- **[Risk]** Nenhum médico cadastrado para uma determinada especialidade no ambiente de testes.
  - *Mitigation*: Garantir fallback/mensagens informativas e verificar usuários de teste com perfil de especialidade cadastrados.
