## Context

No menu Histórico (`Historico.vue`), a ordem das colunas no `<thead` e `<tbody` estava em desalinhamento, fazendo com que a informação de "Especialidade / Procedimento" caísse dentro do cabeçalho "Detalhes / Justificativa", deslocando o restante das células.

## Goals / Non-Goals

**Goals:**
- Ajustar rigorosamente o HTML de `frontend/src/views/Historico.vue` para que a tabela exiba exatamente as 8 colunas especificadas na ordem correta:
  1. `Data/Hora` (`solic.data_criacao`)
  2. `Origem/Menu` (`solic.origem_menu`)
  3. `Prontuário/Paciente` (`solic.codigo_paciente` e `solic.nome_paciente`)
  4. `Especialidade/Procedimento` (`solic.especialidade` e `solic.procedimento`)
  5. `Ação/Tipo` (`solic.tipo`)
  6. `Solicitação ou Resposta` (`solic.detalhes`)
  7. `Status` (`solic.status`)
  8. `Perfil executor/Usuário Executor` (`solic.perfil_executor` e `solic.usuario`)

**Non-Goals:**
- Alterações no backend ou no modelo de persistência de banco de dados.

## Decisions

1. **Estrutura da Tabela no Frontend**:
   - Ajustar o bloco `<thead>` com os 8 cabeçalhos exatos.
   - Ajustar o bloco `<tbody>` alinhando os 8 elementos `<td>` para corresponderem exatamente a cada um dos cabeçalhos definidos.

## Risks / Trade-offs

Nenhum risco relevante. Trata-se de uma reorganização direta de leiaute no template Vue.
