# Design: Filtros de Judicialização e Swalis no Menu Pacientes e Fluxo de Solicitação de Exclusão de Usuários

## Architecture Overview

A proposta abrange duas melhorias independentes e complementares na aplicação:

### 1. Filtros Adicionais no Menu Pacientes
No componente `frontend/src/views/Pacientes.vue`, adicionaremos dois novos controles de seleção no grid de filtros do cabeçalho da página:
- `filtroJudicializado`: reativo (string: `""`, `"Sim"`, `"Não"`).
- `filtroSwalis`: reativo (string: `""`, `"A1"`, `"A2"`, `"B"`, `"C"`, `"D"`, `"NENHUM"`).

Na propriedade computada `pacientesProcessados`, ao iterar sobre cada procedimento do paciente:
```typescript
if (filtroJudicializado.value) {
  procs = procs.filter((p: any) => (p.judicializado || 'Não') === filtroJudicializado.value);
}

if (filtroSwalis.value) {
  procs = procs.filter((p: any) => {
    const sw = (p.Swalis || p.swalis || p.swallis || '—').trim();
    if (filtroSwalis.value === 'NENHUM') {
      return sw === '—' || sw === '' || sw === 'Não informado';
    }
    return sw === filtroSwalis.value;
  });
}
```

### 2. Solicitação de Exclusão de Usuário (Perfis `EPO_GENERALISTA` e `ESPECIALIDADE`)

#### Backend (`src/routers/usuario.py`)
1. **Schema & Model**:
   - `UserCreationRequestCreate`: garantir suporte a `tipo: Optional[str] = "CRIACAO"` (valores esperados: `"CRIACAO"`, `"EDICAO"`, `"EXCLUSAO"`).
2. **Criação da Solicitação (`POST /api/usuarios/solicitacoes`)**:
   - Quando `req_in.tipo == "EXCLUSAO"`:
     - Validar a existência do usuário alvo (`req_in.user_id`).
     - Para perfil `ESPECIALIDADE`, validar se a especialidade do usuário a ser excluído é idêntica à especialidade do criador.
     - Para perfil `EPO_GENERALISTA`, validar permissão sobre usuários de especialidade.
     - Registrar a solicitação na tabela `solicitacoes_criacao_usuario` com `tipo = "EXCLUSAO"`, `user_id = req_in.user_id`, `status = "PENDENTE"`, `username = user.username`, `nome = user.nome`, `perfil_id = user.perfil_id`, `especialidade = user.especialidade`, `funcao = user.funcao`.
3. **Aprovação da Solicitação (`POST /api/usuarios/solicitacoes/{id}/aprovar`)**:
   - Se `request_obj.tipo == "EXCLUSAO"`:
     - Buscar o usuário alvo (`User` onde `User.id == request_obj.user_id`).
     - Se o usuário existir, exclui-lo com `await db.delete(target_user)`.
     - Atualizar o status da solicitação para `"APROVADO"`.
     - Retornar mensagem ou objeto do usuário excluído.
4. **Rejeição da Solicitação (`POST /api/usuarios/solicitacoes/{id}/rejeitar`)**:
   - Atualizar o status da solicitação para `"REJEITADO"`, mantendo o usuário cadastrado intacto.

#### Frontend (`frontend/src/views/Perfis.vue`)
1. **Permissões de Exclusão**:
   - `podeExcluirUsuario(user)`: Retornará `true` para `ADMIN`, `GESTAO_LEC`, `EPO_GENERALISTA` e `ESPECIALIDADE` (se dentro de sua respectiva especialidade).
2. **Ação do Botão Excluir**:
   - Se o perfil ativo for `EPO_GENERALISTA` ou `ESPECIALIDADE`:
     - Ao clicar no botão **Excluir** e confirmar no diálogo ("Confirma a solicitação de exclusão deste usuário?"), invocar `api.post('/api/usuarios/solicitacoes', { user_id: user.id, username: user.username, nome: user.nome, perfil_id: user.perfil_id, tipo: 'EXCLUSAO' })`.
     - Exibir mensagem via toast: `"Solicitação de exclusão de usuário enviada com sucesso!"`.
   - Se o perfil ativo for `ADMIN` ou `GESTAO_LEC`:
     - Mantém a exclusão direta chamando `api.delete('/api/usuarios/${id}')`.
3. **Aba Solicitações Pendentes**:
   - Renderizar o badge do tipo da solicitação:
     - Se `tipo === 'EXCLUSAO'`: exibir etiqueta vermelha `Exclusão`.
     - Se `tipo === 'EDICAO'`: exibir etiqueta roxa `Edição`.
     - Se `tipo === 'CRIACAO'`: exibir etiqueta azul `Criação`.
