## 1. Backend: Registro de Eventos e Auditoria

- [x] 1.1 Atualizar a origem padrão de procedimentos de "Sistema LEC" para "Solicitações LEC" em `src/routers/solicitacao.py` e providers.
- [x] 1.2 Implementar helper de gravação de eventos de histórico em `src/routers/perfil.py` para criação e exclusão de perfis.
- [x] 1.3 Registrar eventos no histórico em `src/routers/usuario.py` para solicitações de criação/exclusão de usuários e respostas de aprovação/rejeição.
- [x] 1.4 Registrar eventos no histórico em `src/routers/categorizacao_profissional.py` para criação e exclusão de categorizações.

## 2. Frontend: Nomenclaturas, Cores e Filtros no Histórico

- [x] 2.1 Atualizar `Historico.vue` para exibir a origem "Solicitações LEC" e ajustar o filtro de menu para corresponder a "Solicitações LEC", "Perfis" e "Pacientes".
- [x] 2.2 Renomear ações de procedimentos em `Historico.vue`: "Inclusão de Procedimento" (verde), "Edição de Procedimento" (azul), "Standby de Procedimento" (amarelo) e "Exclusão de Procedimento" (vermelho).
- [x] 2.3 Implementar formatação e badges das novas ações do menu Perfis:
  - "Criação de Perfil" (lilás) e "Exclusão de Perfil" (lilás com texto vermelho) - tipo "Execução".
  - "Criação de Usuário" (laranja claro) e "Exclusão de Usuário" (laranja claro com texto vermelho) - tipos "Solicitação" ou "Resposta".
  - "Criação de Categorização" (marrom claro) e "Exclusão de Categorização" (marrom claro com texto vermelho) - tipo "Execução".
- [x] 2.4 Atualizar dropdowns de filtros de "Ação" e "Tipo de Evento" em `Historico.vue` para incluir todas as novas opções e tipos.

## 3. Validação e Deploy

- [x] 3.1 Validar compilação do frontend com `npm run build` e execução dos endpoints locais.
- [x] 3.2 Realizar deploy para a VM preservando o banco de dados e validar os eventos gerados.
