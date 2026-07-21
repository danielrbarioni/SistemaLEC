## Context

O menu Histórico precisa de ajustes de interface e regras de exibição para esclarecer o tipo de evento (Solicitação vs. Resposta), renomear o título principal para "Histórico de Solicitações/Respostas" e exibir o usuário no formato Ebserh (`nome.sobrenome`).

## Goals / Non-Goals

**Goals:**
- Renomear o título principal em `Historico.vue` para **"Histórico de Solicitações/Respostas"**.
- Exibir na 6ª coluna ("Solicitação ou Resposta") o tipo de evento e a justificativa/resposta.
- Garantir que o nome de usuário exibido na 8ª coluna utilize o formato de usuário Ebserh (`nome.sobrenome` / `username`).

**Non-Goals:**
- Alterar esquemas estruturais do banco de dados além dos tratamentos de exibição e registro de auditoria.

## Decisions

1. **Título Principal**:
   - Alterar de `<h1>Histórico de Solicitações</h1>` para `<h1>Histórico de Solicitações/Respostas</h1>`.

2. **Coluna Solicitação ou Resposta**:
   - Adicionar o badge com a identificação do tipo de ação na célula: "Solicitação" para envios e "Resposta" para avaliações/decisões.

3. **Formatação do Usuário Executor**:
   - Exibir `solic.username` ou `solic.usuario` garantindo prioridade ao nome de usuário Ebserh (`nome.sobrenome`).
