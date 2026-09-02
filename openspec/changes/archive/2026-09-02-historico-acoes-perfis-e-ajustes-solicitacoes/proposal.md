## Why

Atualmente, o menu Histórico registra principalmente eventos relacionados a procedimentos cirúrgicos originados em interações gerais, exibindo a origem genérica "Sistema LEC" em vez de "Solicitações LEC". Além disso, ações administrativas críticas realizadas no menu Perfis (criação e exclusão de perfis, solicitações e respostas de criação/exclusão de usuários, e criação/exclusão de categorizações de profissionais) não estão registradas no histórico unificado de auditoria, e as nomenclaturas de ações de procedimentos precisam ser mais precisas e descritivas ("inclusão de procedimento", "edição de procedimento", etc.).

## What Changes

- **Correção da Origem de Menu**: Atualizar a identificação de origem de "Sistema LEC" para "Solicitações LEC" nos registros novos e nos filtros de visualização do Histórico.
- **Rastreabilidade de Ações do Menu Perfis no Histórico**:
  - **Criação de Perfil**: Ação "criação de perfil" (tag lilás), tipo de evento "execução", exibindo o perfil criado na descrição/detalhes.
  - **Exclusão de Perfil**: Ação "exclusão de perfil" (tag lilás com texto vermelho), tipo de evento "execução", exibindo o perfil excluído na descrição/detalhes.
  - **Solicitação de Criação de Usuário**: Ação "criação de usuário" (tag laranja claro), tipo de evento "solicitação", exibindo o usuário solicitado na descrição.
  - **Solicitação de Exclusão de Usuário**: Ação "exclusão de usuário" (tag laranja claro com texto vermelho), tipo de evento "solicitação", exibindo o usuário com exclusão solicitada na descrição.
  - **Resposta de Criação de Usuário**: Ação "criação de usuário" (tag laranja claro), tipo de evento "resposta", detalhando aprovação ou rejeição na descrição.
  - **Resposta de Exclusão de Usuário**: Ação "exclusão de usuário" (tag laranja claro com texto vermelho), tipo de evento "resposta", detalhando aprovação ou rejeição na descrição.
  - **Criação de Categorização Profissional**: Ação "criação de categorização" (tag marrom claro), tipo de evento "execução", indicando o profissional + especialidade na descrição.
  - **Exclusão de Categorização Profissional**: Ação "exclusão de categorização" (tag marrom claro com texto vermelho), tipo de evento "execução", indicando o profissional + especialidade na descrição.
- **Padronização das Nomenclaturas de Ações de Procedimentos**:
  - "Inclusão" → "Inclusão de Procedimento" (mantendo a cor verde).
  - "Edição" → "Edição de Procedimento" (mantendo a cor azul).
  - "Standby" → "Standby de Procedimento" (mantendo a cor amarela).
  - "Exclusão" → "Exclusão de Procedimento" (mantendo a cor vermelha).
- **Filtros e Visualização no Histórico**:
  - Atualização dos seletores de "Origem / Menu", "Ação" e "Tipo de Evento" na tela `Historico.vue` para suportar as novas ações, filtros e estilizações visuais.

## Capabilities

### New Capabilities
- `historico-acoes-perfis`: Registro e exibição no Histórico das ações de criação/exclusão de perfis, solicitações/respostas de usuários e criação/exclusão de categorizações com respectivas cores e tipos de evento.
- `historico-nomenclaturas-solicitacoes`: Padronização da origem de menu para "Solicitações LEC" e sufixação das ações de procedimentos ("inclusão de procedimento", "edição de procedimento", etc.).

### Modified Capabilities

## Impact

- **Backend**: Inclusão de registros de eventos/histórico nas rotas `perfil.py`, `usuario.py`, `categorizacao_profissional.py` e `solicitacao.py`.
- **Frontend**: Componente `Historico.vue` (filtros, badges de ação, tipos de evento, estilização por cor), `InteracoesLec.vue` e `Perfis.vue`.
- **Banco de Dados / Modelos**: Tabela `solicitacoes` / estrutura de eventos de histórico para acomodar os novos tipos de ação e origem "Perfis" e "Solicitações LEC".
