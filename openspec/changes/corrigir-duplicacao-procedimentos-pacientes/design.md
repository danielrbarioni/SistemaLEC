## Context

Ao aprovar uma solicitação, o `SolicitacaoSqliteProvider.atualizar_status_solicitacao` atualiza o registro da solicitação original para `status = 'APROVADO'` e insere um segundo registro na tabela `solicitacoes` representando a resposta (`evento_tipo = 'RESPOSTA'`), também com `status = 'APROVADO'`.

No menu **Pacientes** (`frontend/src/views/Pacientes.vue`), a propriedade computada `pacientesProcessados` lê a lista de solicitações do backend, filtra por `status === 'APROVADO'` e aplica a inclusão/edição/exclusão/standby na lista de procedimentos do paciente. Como a resposta também possuía `status === 'APROVADO'`, ela era processada uma segunda vez, duplicando o procedimento.

No backend (`src/controllers/solicitacao_controller.py`), a função `criar_solicitacao` reconstrói os procedimentos ativos do paciente consultando solicitações aprovadas sem filtrar `evento_tipo != "RESPOSTA"`.

No menu **Histórico** (`frontend/src/views/Historico.vue`), a lista exibe tanto `SOLICITACAO` quanto `RESPOSTA` separadamente, o que é o comportamento esperado.

## Goals / Non-Goals

**Goals:**
- Filtrar `s.evento_tipo !== 'RESPOSTA'` (ou `s.is_resposta !== true`) no processamento de `pacientesProcessados` no `Pacientes.vue`.
- Filtrar `s.get("evento_tipo") != "RESPOSTA"` na reconstrução de procedimentos em `solicitacao_controller.py`.
- Manter o comportamento intacto no menu Histórico (`Historico.vue`), onde a exibição de ambas as linhas é desejada.

**Non-Goals:**
- Modificar o schema da tabela de solicitações ou a forma como as respostas são armazenadas no SQLite.
- Alterar o comportamento da exibição no menu Histórico.

## Decisions

- **Decisão:** Filtrar registros de resposta (`evento_tipo === 'RESPOSTA'`) na agregação de procedimentos do paciente no frontend e backend.
  - *Razão:* Mantém o histórico completo e auditável com 2 entradas (solicitação e resposta) na tabela de histórico, enquanto garante que cada ação de negócio seja aplicada apenas uma vez na lista de procedimentos do paciente.
  - *Alternativa considerada:* Não criar uma nova linha para a resposta e apenas atualizar a solicitação original. Rejeitada porque desfaz a funcionalidade de histórico de respostas recentemente implementada e solicitada pelo negócio.

## Risks / Trade-offs

- **[Risco]** Registros antigos gravados antes de introduzir `evento_tipo` podem ter `evento_tipo` como `null` ou `undefined`.
  - *Mitigação:* Usar checagem defensiva `s.evento_tipo !== 'RESPOSTA'`, de modo que registros nulos/antigos (que são solicitações originais) continuem sendo processados normalmente.
