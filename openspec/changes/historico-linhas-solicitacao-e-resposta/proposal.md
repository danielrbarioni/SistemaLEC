## Why

Atualmente, ao responder uma solicitação (Aprovar ou Rejeitar na Gestão LEC), o sistema alterava o status da solicitação original e adicionava uma resposta, mas ocorria substituição visual/lógica incorreta da linha da solicitação.
A regra correta exige que a linha da solicitação original permaneça visível no Histórico (com seus dados de criação, usuário solicitante e o status atualizado para APROVADO ou REJEITADO) E TAMBÉM seja adicionada uma nova linha independente representando a Resposta (com a data/hora da resposta, usuário que respondeu e status APROVADO ou REJEITADO).

## What Changes

1. **Backend (`SolicitacaoSqliteProvider` e `SolicitacaoCsvProvider`)**:
   - Manter o registro da Solicitação original com seu ID, `evento_tipo = 'SOLICITACAO'`, usuário solicitante original, atualizando apenas o seu `status` para `APROVADO` ou `REJEITADO`.
   - Adicionar uma nova linha independente no banco de dados para a Resposta com `evento_tipo = 'RESPOSTA'`, `data_criacao` no momento exato da decisão, `status = APROVADO/REJEITADO`, `usuario = usuario_executor` (quem respondeu) e `detalhes` descrevendo a ação.
   - Garantir que a listagem de solicitações retorne ambas as linhas de forma independente para exibição no Histórico.

2. **Frontend (`Historico.vue`)**:
   - Exibir ambas as linhas ordenadas cronologicamente (da mais recente para a mais antiga).
   - Exibir na linha da solicitação original: Data de envio, Usuário solicitante (ex.: maria.carneiro), Solicitação, Status atualizado (APROVADO/REJEITADO).
   - Exibir na linha da resposta: Data/Hora da resposta, Usuário executor que respondeu (ex.: joao.freitas), Resposta, Status (APROVADO/REJEITADO).

## Capabilities

### New Capabilities
- `historico-preservacao-solicitation-e-resposta`: Exibição simultânea e independente da linha da solicitação (com status atualizado) e da linha da resposta no histórico.

### Modified Capabilities

## Impact

- **Backend**: `src/providers/implementations/solicitacao_sqlite_provider.py`, `src/providers/implementations/solicitacao_csv_provider.py`.
- **Frontend**: `frontend/src/views/Historico.vue`.
