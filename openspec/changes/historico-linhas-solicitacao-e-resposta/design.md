## Context

Ao aprovar ou rejeitar uma solicitação na Gestão LEC, a API alterava a linha original da solicitação sem registrar separadamente a resposta ou substituía incorretamente as informações do usuário solicitante original.
É necessário garantir que a solicitação permaneça com suas informações originais intactas (apenas alterando seu status para APROVADO/REJEITADO) e que uma nova entrada no banco seja gerada especificamente para o evento de RESPOSTA.

## Goals / Non-Goals

**Goals:**
- Manter a linha original da solicitação visível no histórico com seu criador original (ex.: maria.carneiro) e o status atualizado (`APROVADO` / `REJEITADO`).
- Registrar uma nova linha independente para a resposta com a data/hora do evento, tipo `RESPOSTA` e o usuário executor da ação (ex.: joao.freitas).

**Non-Goals:**
- Alterar as regras de filtragem ou os 9 filtros já existentes no menu Histórico.

## Decisions

- **Decisão 1: Atualização da linha de solicitação + Inserção de nova linha de resposta**:
  - No `SolicitacaoSqliteProvider` e `SolicitacaoCsvProvider`, o método `atualizar_status_solicitacao` atualizará o status da solicitação original para `APROVADO` ou `REJEITADO` mantendo `solic.usuario` e `solic.evento_tipo = 'SOLICITACAO'`.
  - Em seguida, inserirá uma nova entidade `Solicitacao` no banco de dados com `evento_tipo = 'RESPOSTA'`, `data_criacao = data_atual`, `status = novo_status`, `usuario = usuario_executor` (da Gestão LEC).

## Risks / Trade-offs

- [Multiplicação de entradas no banco] → A inclusão de uma nova linha por resposta é intencional para auditoria completa do histórico.
