## Why

Atualmente, ao rejeitar uma solicitação na Gestão LEC, a ação ocorre diretamente sem registrar o motivo/justificativa clínica da rejeição para a equipe assistencial. Além disso, na aba **Histórico Concluído (Aprovadas/Rejeitadas)** de **Comunicação LEC**, o registro de resposta aparecia repetido como uma linha separada, e o modal de descrição exibia apenas os dados parciais. Por fim, as tabelas do menu Comunicação LEC demandavam rolagem horizontal excessiva, necessitando de um layout mais compacto, responsivo e com suporte a barra de rolagem superior quando necessário.

## What Changes

- **Modal de Justificativa de Rejeição**: Adicionar modal obrigatório solicitando o motivo/justificativa ao clicar em "Rejeitar" uma solicitação (inclusão, edição, standby ou exclusão), persistindo esse motivo no backend e associando-o à resposta da solicitação.
- **Histórico Concluído com Linha Única**: Na aba *Histórico Concluído* do menu *Comunicação LEC > Acompanhamento das Solicitações*, agrupar a solicitação e sua respectiva resposta em uma linha única por solicitação concluída (ao contrário do menu *Histórico Geral*, que mantém o registro auditável completo com linhas separadas).
- **Modal de Detalhes Completo**: No modal da coluna *Descrição / Ver Descrição*, exibir de forma clara e estruturada:
  - **Dados da Solicitação**: Data e hora da criação, usuário/perfil solicitante, especialidade, procedimento, prontuário, paciente, judicialização, Swalis, médico responsável e justificativa original.
  - **Dados da Resposta**: Data e hora da ação/resposta, status (Aprovado/Rejeitado/Cancelado), usuário/perfil que respondeu e justificativa detalhada em caso de rejeição (ou observações da gestão).
- **Layout Compacto e Ajuste de Visualização das Tabelas**:
  - Ajustar colunas, espaçamentos e fontes de todas as tabelas do menu Comunicação LEC (Nova Solicitação e Acompanhamento) para que se adaptem à tela sem necessidade de scroll horizontal em resoluções padrão.
  - Adicionar suporte a scroll horizontal sincronizado no topo da tabela (barra de rolagem superior) em tabelas que apresentarem overflow horizontal, evitando que o usuário precise rolar a página até o rodapé para navegar para os lados.

## Capabilities

### Modified Capabilities
- `comunicacao-lec-fluxo-e-layout`: Implementação do fluxo de rejeição com justificativa obrigatória, unificação de linhas no Histórico Concluído com modal detalhado de solicitação/resposta e otimização visual/scroll das tabelas de Comunicação LEC.

## Impact

- `frontend/src/views/InteracoesLec.vue` (Comunicação LEC)
- `src/routers/solicitacao.py`
- `src/controllers/solicitacao_controller.py`
- `src/providers/implementations/solicitacao_sqlite_provider.py`
- `src/models/solicitacao.py` (garantir campos de justificativa de resposta se aplicável)
