## Context
No menu `Histórico` (`frontend/src/views/Historico.vue`):
1. O seletor `#filtroAcaoTipo` ainda possui a opção `<option value="SOLICITAR_APA">Solicitação APA</option>`, que foi descontinuada.
2. O grupo `<optgroup label="Menu Usuários">` lista `Criação de Perfil` (`CRIAR_PERFIL`) e `Exclusão de Perfil` (`EXCLUIR_PERFIL`), mas não possui `Edição de Perfil` (`EDITAR_PERFIL`).
3. Na tabela do Histórico (`getTipoBadgeClass`), os badges do menu Usuários seguem uma convenção visual clara por entidade e operação:
   - **Perfis (fundo lilás `bg-purple-100 border border-purple-300`)**:
     - Criação (`CRIAR_PERFIL`): `text-purple-800`
     - Edição (`EDITAR_PERFIL`): `text-blue-800` (mesmo fundo lilás, com letra azul, consistente com `EDITAR_USUARIO` e `EDITAR_CATEGORIZACAO` que também usam `text-blue-800`)
     - Exclusão (`EXCLUIR_PERFIL`): `text-red-700`
4. No backend (`src/routers/perfil.py`), `create_perfil` registra `CRIAR_PERFIL` e `delete_perfil` registra `EXCLUIR_PERFIL`, mas `update_perfil` ainda não registrava `EDITAR_PERFIL` via `registrar_evento_historico`.

## Goals / Non-Goals

**Goals:**
- Retirar `Solicitação APA` do filtro `Ação` em `Historico.vue`.
- Incluir `Edição de Perfil` (`EDITAR_PERFIL`) no filtro `Ação`, em `formatarTipo`, em `getTipoBadgeClass` (com `bg-purple-100 text-blue-800 border border-purple-300`) e na função de ordenação de itens sem data em `Historico.vue`.
- Registrar `EDITAR_PERFIL` via `registrar_evento_historico` em `update_perfil` (`src/routers/perfil.py`).

**Non-Goals:**
- Alterar outras ações ou filtros do menu Histórico.

## Decisions

### 1. Estilização e Formatação em `frontend/src/views/Historico.vue`
- **Filtro `#filtroAcaoTipo`**:
  - Remover `<option value="SOLICITAR_APA">Solicitação APA</option>`.
  - Adicionar `<option value="EDITAR_PERFIL">Edição de Perfil</option>` logo após `<option value="CRIAR_PERFIL">Criação de Perfil</option>`.
- **`formatarTipo`**:
  - Adicionar `case 'EDITAR_PERFIL': return 'Edição de Perfil';`.
- **`getTipoBadgeClass`**:
  - Adicionar `case 'EDITAR_PERFIL': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-blue-800 border border-purple-300';`.

### 2. Registro de Auditoria `EDITAR_PERFIL` em `src/routers/perfil.py`
- Em `update_perfil`, após atualizar o perfil e propagar o novo nome da especialidade, chamar `registrar_evento_historico`:
  - `tipo="EDITAR_PERFIL"`
  - `origem_menu="Usuários"`
  - `evento_tipo="EXECUCAO"`
  - `status="CONCLUIDO"`
  - `especialidade=existing.especialidade or "—"`
  - `procedimento="—"`
  - `detalhes`: se o nome/especialidade mudou (`old_nome != existing.nome`), registrar `f'Perfil "{existing.nome}" editado (anterior: "{old_nome}")'`; caso contrário, `f'Perfil "{existing.nome}" editado'`.
  - Nota: o formato `Perfil "<nome>" editado...` é automaticamente reconhecido por `obterAlvoAcaoPerfis` em `Historico.vue` (`/perfil\s+"([^"]+)"/i`), exibindo o nome do perfil abaixo do badge `Execução` na coluna Tipo de Evento.

