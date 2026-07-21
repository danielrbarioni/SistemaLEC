## Why

A tabela do menu **Histórico** encontrava-se desregulada: o conteúdo da coluna "Especialidade / Procedimento" estava sendo exibido sob o cabeçalho "Detalhes / Justificativa", e os demais dados das colunas subsequentes estavam desalinhados.
Esta mudança reordena os cabeçalhos e os valores das células da tabela do Histórico para garantir alinhamento visual perfeito e auditoria completa das solicitações e respostas.

## What Changes

- **Frontend (`Historico.vue`)**:
  - Reordenar as colunas da tabela de solicitações exatamente para a seguinte sequência (8 colunas):
    1. **Data/Hora** (`data_criacao`)
    2. **Origem/Menu** (`origem_menu`)
    3. **Prontuário/Paciente** (`codigo_paciente` e `nome_paciente`)
    4. **Especialidade/Procedimento** (`especialidade` e `procedimento`)
    5. **Ação/Tipo** (`tipo`)
    6. **Solicitação ou Resposta** (`detalhes`)
    7. **Status** (`status`)
    8. **Perfil executor/Usuário Executor** (`perfil_executor` e `usuario`)

## Capabilities

### New Capabilities
- `historico-colunas-reordenadas`: Estruturação e ordenação correta das 8 colunas da tabela no menu Histórico.

### Modified Capabilities
(Nenhuma)

## Impact

- **Frontend**: `frontend/src/views/Historico.vue`.
