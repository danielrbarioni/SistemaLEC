## Why

Atualmente, quando um usuário registra uma solicitação de procedimento (de Inclusão, Edição ou Standby), não existe funcionalidade para retificar ou atualizar os dados dessa solicitação enquanto ela aguarda análise (status `PENDENTE`). Se houver necessidade de ajustar o procedimento, prioridade Swalis, médico responsável, tempo de standby ou justificativa, o usuário não tem um mecanismo direto de edição.

Esta mudança permite que os perfis que possuem permissão de solicitação possam editar solicitações pendentes diretamente na tabela de Acompanhamento das Solicitações, atualizando os dados da solicitação sem alterar sua posição na fila cronológica e registrando a trilha de auditoria completa no Histórico.

## What Changes

- **Ação de Edição na Tabela de Acompanhamento**: Na tabela de solicitações pendentes de `InteracoesLec.vue`, disponibilizar o botão de "Editar" na coluna de Ações para os tipos `INSERIR`, `EDITAR` e `STANDBY`. O tipo `EXCLUIR` permanece não editável (apenas cancelável).
- **Modo de Edição no Formulário**: Ao acionar "Editar", o formulário superior é preenchido com os dados da solicitação selecionada, a aba correta é ativada e um banner informativo indica o modo de edição com botões para "Salvar Alterações" e "Cancelar Edição".
- **Preservação da Fila e Sobrescrita dos Dados**: Ao salvar as alterações, os dados da solicitação ativa são atualizados na base mantendo o horário original de criação (`data_criacao`), garantindo que a ordenação e a posição da solicitação na fila de espera permaneçam inalteradas.
- **Rastreabilidade no Histórico**: É gerado um novo registro de evento de alteração (`evento_tipo: ALTERACAO`) com o timestamp e usuário executor da edição. O menu Histórico (`Historico.vue`) passa a exibir ambas as ações em ordem cronológica: a solicitação original e as alterações subsequentes.
- **Endpoint Backend de Edição**: Criação da rota `PUT /api/solicitacoes/{id_solicitacao}` com validações de perfil, status pendente e regras de negócio.
- **Garantia de Não Alteração no Banco da VM**: Implementação estritamente na camada de código e lógica da aplicação, sem alterar a estrutura das tabelas existentes.

## Capabilities

### New Capabilities
- `edicao-solicitacao-pendente`: Edição de solicitações pendentes de Inclusão, Edição e Standby com atualização de dados na fila preservando timestamp de criação e geração de evento de auditoria no Histórico.

## Impact

- **Backend**: `src/routers/solicitacao.py`, `src/controllers/solicitacao_controller.py`, `src/providers/interfaces/solicitacao_provider_interface.py`, `src/providers/implementations/solicitacao_sqlite_provider.py`, `src/providers/implementations/solicitacao_csv_provider.py`.
- **Frontend**: `frontend/src/views/InteracoesLec.vue`, `frontend/src/views/Historico.vue`.
- **APIs**: Novo endpoint `PUT /api/solicitacoes/{id_solicitacao}`.
