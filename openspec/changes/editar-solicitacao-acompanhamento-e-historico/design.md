## Context

No módulo de Solicitações LEC (`InteracoesLec.vue`), os usuários registram solicitações de Inclusão, Edição, Standby e Exclusão. Quando uma solicitação está no estado `PENDENTE`, pode ser necessário corrigir dados digitados (como procedimento, prioridade Swalis, médico responsável, tempo de standby ou justificativa).

Atualmente, não existia uma opção para editar solicitações já criadas. O usuário solicitou que:
1. Seja possível editar solicitações pendentes dos tipos `INSERIR`, `EDITAR` e `STANDBY`.
2. A solicitação de `EXCLUIR` não possa ser editada (apenas cancelada).
3. A edição seja permitida para todos os perfis com permissão de solicitação (Médico, Residente, Administrador, Gestão LEC).
4. Ao clicar no botão de edição na tabela de acompanhamento, o formulário no topo da página seja preenchido e entre em modo de edição.
5. Os dados atualizados fiquem "por cima" da solicitação original na fila, preservando a data/hora original de criação (`data_criacao`) para não alterar a ordem cronológica da fila.
6. No menu Histórico (`Historico.vue`), ambas as ações fiquem registradas: a solicitação original (com seu horário e usuário criador) e a alteração (com seu horário de edição e usuário editor).

## Goals / Non-Goals

**Goals:**
- Implementar endpoint `PUT /api/solicitacoes/{id_solicitacao}` para edição de solicitações pendentes.
- Bloquear edição de solicitações com status diferente de `PENDENTE` ou do tipo `EXCLUIR`.
- Atualizar a linha da solicitação original mantendo inalterado o timestamp `data_criacao`.
- Inserir um registro com `evento_tipo = 'ALTERACAO'` para manter rastreabilidade cronológica completa no Histórico.
- Adicionar botão "Editar" na coluna Ações da tabela de acompanhamento de solicitações pendentes (`InteracoesLec.vue`).
- Criar modo de edição visual no Card de Nova Solicitação com opções para salvar alterações ou cancelar a edição.
- Exibir eventos de alteração com badge visualmente diferenciado no menu Histórico (`Historico.vue`).
- Nenhuma alteração estrutural no banco de dados da VM.

**Non-Goals:**
- Não permitir edição de solicitações já concluídas (`APROVADO`, `REJEITADO`, `CANCELADO`).
- Não permitir edição de solicitações de exclusão (`EXCLUIR`).

## Decisions

1. **Atualização In-Place e Registro de Histórico no Backend**:
   - `solicitacao_controller.editar_solicitacao`:
     - Localiza a solicitação pelo `id_solicitacao`.
     - Verifica se `status == 'PENDENTE'` e `tipo != 'EXCLUIR'`.
     - Atualiza os campos (`especialidade`, `procedimento`, `judicializado`, `swallis`, `medico_responsavel`, `detalhes`, `tempo_standby`, `procedimento_anterior`) sem alterar `data_criacao`.
     - Insere um novo registro com `evento_tipo = 'ALTERACAO'`, timestamp atual `data_criacao = datetime.now()`, usuário executor e resumo das alterações na descrição para o histórico.
2. **Filtragem no Frontend**:
   - `InteracoesLec.vue`: Na listagem de acompanhamento, filtrar `evento_tipo != 'ALTERACAO'` para não duplicar linhas, exibindo a solicitação original já com seus dados atualizados.
   - `Historico.vue`: Exibir todos os eventos (`SOLICITACAO`, `ALTERACAO`, `RESPOSTA`) com filtros e badges correspondentes.
3. **Fluxo de Edição no Frontend (`InteracoesLec.vue`)**:
   - Variáveis reativas: `modoEdicaoSolicitacao = ref(false)` e `solicitacaoEmEdicaoId = ref<string | null>(null)`.
   - Função `iniciarEdicaoSolicitacao(solic)`: Ativa a aba correta, preenche o `form`, ativa `modoEdicaoSolicitacao` e rola suavemente até o formulário.
   - Função `cancelarEdicaoSolicitacao()`: Limpa o formulário e sai do modo de edição.

## Risks / Trade-offs

- **[Risk]** Usuário editar a solicitação e o frontend criar uma nova solicitação em vez de atualizar.
  → **Mitigation**: `enviarSolicitacao` verifica se `modoEdicaoSolicitacao` está ativo; se estiver, direciona para `PUT /api/solicitacoes/{id}` em vez de `POST`.
