## Why

Quando uma solicitação (de inclusão, edição, standby ou exclusão) é aprovada pela Gestão LEC, o sistema registra a resposta gerando uma nova linha de histórico com `evento_tipo = "RESPOSTA"` e `status = "APROVADO"`, além de atualizar a solicitação original para `status = "APROVADO"`.
No menu **Pacientes** (e na validação do backend), ao reconstruir os procedimentos de um paciente a partir das solicitações aprovadas, o sistema contabilizava ambas as linhas (`evento_tipo = "SOLICITACAO"` e `evento_tipo = "RESPOSTA"`), fazendo com que procedimentos com solicitação aprovada fossem incluídos duplicados no perfil do paciente.

## What Changes

- Filtragem na montagem do mapa de procedimentos de pacientes no frontend (`Pacientes.vue`) para desconsiderar eventos do tipo `RESPOSTA` (`evento_tipo === "RESPOSTA"`), garantindo que apenas a solicitação original seja processada.
- Ajuste no backend (`solicitacao_controller.py`) para ignorar registros de `RESPOSTA` na reconstrução de procedimentos ativos durante validações de criação de nova solicitação.
- Preservação da exibição dupla de Solicitação e Resposta no menu **Histórico** (`Historico.vue`), conforme comportamento esperado pelo negócio.

## Capabilities

### Modified Capabilities
- `gestao-pacientes-e-historico`: Ajuste da regra de agregação de procedimentos aprovados por solicitação no menu Pacientes e no controller de solicitações sem afetar a exibição do Histórico.

## Impact

- `frontend/src/views/Pacientes.vue`
- `src/controllers/solicitacao_controller.py`
