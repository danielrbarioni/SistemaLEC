## Why

O fluxo de aprovação estava atualizando diretamente o registro da Solicitação original para APROVADO, gerando confusão no Histórico em relação aos badges. Além disso, a ordem dos filtros e nomenclaturas no menu Histórico de Solicitações/Respostas precisavam ser reordenadas e refinadas.

## What Changes

1. **Separação Rigorosa de Solicitação vs Resposta**:
   - A solicitação original gravada ao enviar um formulário se mantém permanentemente com `status = 'PENDENTE'` e `evento_tipo = 'SOLICITACAO'`.
   - Ao aprovar ou rejeitar uma solicitação na Gestão LEC, a API cria um novo registro independente no histórico com `status = 'APROVADO'` ou `'REJEITADO'`, `evento_tipo = 'RESPOSTA'`, `origem_menu = solic.origem_menu`, contendo a data/hora exata da decisão e o usuário executor.

2. **Reordenação e Ajustes dos Filtros (`Historico.vue`)**:
   - Ordem exata dos 9 filtros:
     1. **Data De**
     2. **Data Até**
     3. **Origem / Menu**
     4. **Prontuário / Paciente**
     5. **Especialidade** (carregada dinamicamente a partir dos perfis cadastrados do tipo `ESPECIALIDADE` no menu Perfis)
     6. **Ação** (remover o termo "Tipo" do rótulo do filtro e da tabela)
     7. **Solicitação ou Resposta**
     8. **Status**
     9. **Usuário Executor** (remover o sufixo "Ebserh")

## Capabilities

### New Capabilities
- `historico-ordem-filtros-e-preservacao-respostas`: Manutenção da solicitação como PENDENTE + inclusão da resposta como novo evento independente e reordenação dos 9 filtros no Histórico.

### Modified Capabilities
(Nenhuma)

## Impact

- **Frontend**: `frontend/src/views/Historico.vue`, `frontend/src/views/InteracoesLec.vue`.
- **Backend**: `src/providers/implementations/solicitacao_sqlite_provider.py`, `src/providers/implementations/solicitacao_csv_provider.py`.
