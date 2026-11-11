## 1. Frontend: Filtro e Badge no Menu Histórico (`frontend/src/views/Historico.vue`)

- [x] 1.1 Remover a opção `<option value="SOLICITAR_APA">Solicitação APA</option>` do filtro `Ação` (`#filtroAcaoTipo`) em `frontend/src/views/Historico.vue`.
- [x] 1.2 Incluir a opção `<option value="EDITAR_PERFIL">Edição de Perfil</option>` no `<optgroup label="Menu Usuários">` do filtro `Ação` em `frontend/src/views/Historico.vue`.
- [x] 1.3 Adicionar `case 'EDITAR_PERFIL': return 'Edição de Perfil'` em `formatarTipo` e `case 'EDITAR_PERFIL': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-blue-800 border border-purple-300'` em `getTipoBadgeClass` (além de incluir `EDITAR_PERFIL` em `getPriority`).

## 2. Backend: Registro de Auditoria de Edição de Perfil (`src/routers/perfil.py`)

- [x] 2.1 Adicionar chamada a `registrar_evento_historico` com `tipo="EDITAR_PERFIL"` em `update_perfil` (`src/routers/perfil.py`) ao salvar a edição de um perfil.

## 3. Validação

- [x] 3.1 Validar o build do frontend (`npm run build`) e testar o registro de `EDITAR_PERFIL`.

