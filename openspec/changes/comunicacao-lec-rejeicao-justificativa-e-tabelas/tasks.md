## 1. Backend - Suporte a justificativa na atualização de status

- [x] 1.1 Atualizar o modelo e router em `src/routers/solicitacao.py` e `src/controllers/solicitacao_controller.py` para aceitar `justificativa` no corpo da requisição de atualização de status.
- [x] 1.2 Atualizar `src/providers/implementations/solicitacao_sqlite_provider.py` para registrar a justificativa de rejeição no campo de detalhes da resposta e no histórico.

## 2. Frontend - Modal de Justificativa de Rejeição

- [x] 2.1 Em `InteracoesLec.vue`, criar o modal de confirmação de rejeição com campo de texto obrigatório para a justificativa.
- [x] 2.2 Conectar o botão "Rejeitar" para abrir o modal e enviar a justificativa ao backend ao confirmar.

## 3. Frontend - Histórico Concluído com Linha Única e Modal de Descrição Completo

- [x] 3.1 Em `InteracoesLec.vue`, ajustar a filtragem da sub-aba *Histórico Concluído* para consolidar a solicitação e sua respectiva resposta em uma linha única por solicitação.
- [x] 3.2 Reformular o modal disparado por *📄 Ver Descrição* para exibir detalhadamente os dados da solicitação (Data/Hora, solicitante, justificativa original) e os dados da resposta (Data/Hora, quem respondeu, status e justificativa da rejeição).

## 4. Frontend - Otimização de Layout e Rolagem das Tabelas

- [x] 4.1 Compactar colunas, espaçamentos e tipografia das tabelas em `InteracoesLec.vue` para visualização completa em tela sem scroll horizontal forçado.
- [x] 4.2 Adicionar barra de rolagem horizontal superior sincronizada para tabelas que apresentarem overflow horizontal.

## 5. Validação e Deploy

- [x] 5.1 Realizar build do frontend (`npm run build`) e validar integridade do código backend.
- [x] 5.2 Testar o fluxo completo: criação de solicitação, aprovação, rejeição com justificativa, visualização no Histórico Concluído e visualização no Histórico Geral.
