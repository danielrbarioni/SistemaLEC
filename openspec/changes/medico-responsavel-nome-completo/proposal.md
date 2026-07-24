## Why

No menu Pacientes e nas abas de Comunicação LEC (Solicitar Edição, etc.), o médico responsável em solicitações legadas ou sincronizadas aparece identificado pelo login de usuário Ebserh (ex.: `joao.silva`). Quando o usuário tenta alterar o médico responsável, a lista de seleção apresenta nomes completos (ex.: `João Santos da Silva`). Isso permite selecionar equivocadamente o mesmo médico sob a representação de nome completo em vez de login, gerando inconsistências visuais e duplicidades conceituais onde um paciente é exibido com login e outro com nome completo.

O objetivo é padronizar a exibição e o armazenamento para que, em todas as telas (menu Pacientes, cartões, modais e abas do menu Comunicação LEC), o médico responsável seja sempre exibido pelo seu nome completo em vez do login Ebserh.

## What Changes

- Padronizar o retorno dos dados de paciente/solicitação e o preenchimento de opções de seleção para garantir que o campo `medicoResponsavel` exiba sempre o nome completo do médico.
- No backend/serviço de busca e sincronização (AGHU / banco local), realizar o mapeamento do login Ebserh para o nome completo correspondente do perfil/usuário.
- No frontend, assegurar que a formatação e as opções de filtro/edição de médico responsável utilizem o nome completo de forma consistente.

## Capabilities

### Modified Capabilities
- `medico-responsavel-specialty-filter`: Atualizar os requisitos para garantir que o médico responsável seja consistentemente exibido e selecionado pelo seu nome completo em toda a plataforma.

## Impact

- Frontend: `NavegacaoLec.vue`, `InteracoesLec.vue`, `HistoricoLec.vue` e stores de perfis/solicitações.
- Backend: Endpoints de pacientes, solicitações e integração AGHU (`src/routers/solicitacao.py`, `src/routers/paciente.py`, `src/providers/`).
