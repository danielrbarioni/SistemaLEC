## 1. Backend: Origem Pacientes e Edição de Categorização

- [x] 1.1 Atualizar `src/helpers/excel_import_helper.py` para gravar `origem_menu="Pacientes"`, `tipo="INSERIR"` e `evento_tipo="IMPORTACAO"`.
- [x] 1.2 Registrar evento no Histórico em `src/routers/categorizacao_profissional.py` no endpoint `atualizar_categorizacao` (`tipo="EDITAR_CATEGORIZACAO"`).
- [x] 1.3 Garantir preenchimento de `especialidade` em todos os registros de auditoria em `perfil.py`, `usuario.py` e `categorizacao_profissional.py`.
- [x] 1.4 Criar script de população retroativa dos eventos no histórico para perfis, usuários e categorizações existentes no SQLite.

## 2. Frontend: Badges de Importação, Edição de Categorização e Filtros de Especialidade

- [x] 2.1 Atualizar `Historico.vue` para exibir o tipo de evento "Importação" (badge verde claro) e incluir no filtro `filtroEventoTipo`.
- [x] 2.2 Adicionar estilo e opção de "Edição de Categorização" (badge marrom claro com texto azul) no `Historico.vue`.
- [x] 2.3 Mapear origem "Pacientes" para incluir retroativamente registros com "Importação Planilha" no `Historico.vue`.
- [x] 2.4 Ajustar renderização da coluna "Especialidade / Procedimento" para exibir especialidade limpa sem exigir procedimento cirúrgico.

## 3. Validação e Deploy

- [x] 3.1 Compilar o frontend com `npm run build` e executar script de sincronização e carga retroativa na VM.
- [x] 3.2 Verificar na VM o funcionamento do Histórico com os novos filtros e eventos.
