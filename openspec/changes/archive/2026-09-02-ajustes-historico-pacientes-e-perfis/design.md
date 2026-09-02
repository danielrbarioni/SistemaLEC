## Context

Refinamentos no menu Histórico para tratar importações por planilha no menu Pacientes, registrar edições de categorizações de profissionais e unificar a filtragem e exibição por Especialidade para eventos administrativos.

## Goals / Non-Goals

**Goals:**
- Ajustar `excel_import_helper.py` e mapeamento retroativo para que importações do menu Pacientes apareçam com `origem_menu = 'Pacientes'`, ação `'INSERIR'` ("Inclusão de Procedimento") e `evento_tipo = 'IMPORTACAO'` (badge verde clara).
- Registrar em `src/routers/categorizacao_profissional.py` no endpoint de atualização (`PUT`) o evento `'EDITAR_CATEGORIZACAO'` com badge marrom claro e letra azul.
- Garantir que todas as ações administrativas gravem e exibam a `especialidade` preenchida e sejam contempladas nos filtros do cabeçalho de `Historico.vue`.
- Criar script de população retroativa de eventos no banco SQLite para que perfis, usuários e categorizações já existentes constem no Histórico.

**Non-Goals:**
- Alterar as regras de permissão de acesso existentes.

## Decisions

1. **Badge Tipo de Evento "Importação"**:
   - `evento_tipo === 'IMPORTACAO'`: badge com estilo `bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold`.
2. **Badge Ação "Edição de Categorização"**:
   - `tipo === 'EDITAR_CATEGORIZACAO'`: badge `bg-amber-100 text-blue-800 border border-amber-300 font-bold`.
3. **Mapeamento Retroativo no Frontend**:
   - `formatarOrigemMenu`: se for `'Importação Planilha'` ou `'Pacientes'`, padroniza para `'Pacientes'`.
   - `filtroOrigemMenu === 'Pacientes'`: corresponde a `s.origem_menu === 'Pacientes'` ou `s.origem_menu === 'Importação Planilha'`.
