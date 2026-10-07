# Proposal

## Why
Atualmente, no menu Pacientes, os usuários visualizam os dados cadastrais e o estado atual de cada procedimento vinculado ao paciente, mas não conseguem acompanhar o histórico detalhado dos acontecimentos daquele procedimento específico (como a data exata de inclusão, justificativas de solicitações de alteração, motivos de entrada ou saída de standby e histórico de aprovações). As equipes das especialidades cirúrgicas e da Gestão LEC precisam rastrear a evolução cronológica completa de cada procedimento diretamente na visualização do paciente, sem precisar buscar manualmente eventos dispersos no menu de Histórico geral.

## What Changes
- Adicionar uma seção interativa de "Linha do Tempo de Ações" (Timeline) dentro do card de cada procedimento no modal de detalhes do paciente em `Pacientes.vue`.
- Integrar e exibir em ordem cronológica todas as ações e eventos vinculados àquele procedimento:
  - Evento inicial de inclusão/inserção (com data de inclusão na fila e justificativa/origem, contemplando também procedimentos importados via planilha Excel ou legados);
  - Solicitações e aprovações de edição/alteração de dados com respectivas justificativas e campos alterados;
  - Eventos de Standby e cancelamento de Standby com prazos e justificativas clínicas;
  - Decisões da Gestão LEC (aprovações e rejeições) com suas respectivas justificativas registradas;
- Manter total integridade do banco de dados, sem qualquer alteração destrutiva ou refatoração no schema existente, agregando as informações em tempo de execução a partir dos registros de solicitações e base de pacientes.

## Capabilities

### New Capabilities
- `pacientes-linha-tempo-procedimento`: Apresentação cronológica (linha do tempo) de ações, datas, responsáveis e justificativas registradas para cada procedimento cirúrgico do paciente no menu Pacientes.

### Modified Capabilities
<!-- Nenhuma especificação existente teve seus requisitos alterados. -->

## Impact
- **Frontend**: Componente `frontend/src/views/Pacientes.vue` (agregação de histórico por procedimento em `todosPacientesMap`, adição do componente/bloco visual de linha do tempo expansível/visível no card do procedimento).
- **Backend / APIs**: Nenhuma alteração estrutural necessária nos endpoints existentes (`/api/pacientes`, `/api/solicitacoes`), aproveitando a carga unificada de dados já disponível no frontend.
