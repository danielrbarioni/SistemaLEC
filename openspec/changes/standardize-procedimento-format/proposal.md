# Proposal: Padronizar Formato e Eliminar Duplicidades de Procedimentos

## Summary
Padronização de todos os locais de exibição e seleção de procedimentos (filtros, formulários e listas de pacientes) para o formato único `NOME DO PROCEDIMENTO (ID XXX)`, eliminando duplicidades provenientes de formatos legados como `NOME DO PROCEDIMENTO - ID XXX` ou `NOME DO PROCEDIMENTO (XXX)`.

## Why
Atualmente, ocorrem duplicidades nas listas e filtros de procedimentos (ex.: no menu Pacientes, Comunicação LEC e Navegação LEC) devido a variações na string do nome do procedimento gravada no banco ou retornada pela integração (`- ID 966`, `(966)`, `(ID 966)`). Isso polui as opções dos filtros de busca e causa inconsistências visuais na interface.

## Key Changes
1. **Função Auxiliar de Formatação Única**:
   - Normalizar strings de procedimento para extrair o código/ID e o nome limpo do procedimento.
   - Formatar de forma estrita como `NOME DO PROCEDIMENTO (ID XXX)`.
2. **Eliminação de Duplicidades em Filtros e Listas**:
   - Aplicar a normalização e remoção de duplicatas nos selects de procedimentos das views `Pacientes.vue`, `InteracoesLec.vue` e `NavegacaoLec.vue`.
   - Garantir que essa padronização seja escalável para bases futuras de outras especialidades vindas do AGHU/PostgreSQL ou SQLite.
3. **Normalização no Backend / Provedores**:
   - Garantir que os endpoints que retornam procedimentos tratem e padronizem as descrições no padrão `NOME DO PROCEDIMENTO (ID XXX)`.

## Impact & Scope
- Vue Components: `Pacientes.vue`, `InteracoesLec.vue`, `NavegacaoLec.vue`.
- Helpers / Backend: Provedores e utilitários de procedimento.
