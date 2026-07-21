## Context

O Histórico do Sistema LEC precisa abranger não apenas os envios das solicitações, mas o ciclo de vida auditável completo das ações, incluindo aprovações/rejeições e a identificação do menu/módulo em que foram originadas (ex: "Sistema LEC" ou "Navegação").
Além disso, no formulário de Interações LEC, a lista de especialidades deve derivar diretamente do cadastro centralizado no menu Perfis (`/api/perfis`), em vez de manter strings hardcoded em componentes Vue.

## Goals / Non-Goals

**Goals:**
- Adicionar a coluna **"Origem / Menu"** no Histórico, imediatamente após "Data / Hora".
- Registrar a propriedade `origem_menu` (ex: "Sistema LEC", "Navegação") nas solicitações e respostas.
- Exibir eventos de solicitação e eventos de resposta/decisão de administradores/gestores no Histórico.
- Obter a lista de especialidades em `InteracoesLec.vue` através da store de perfis (`usePerfisStore().especialidadesAtivas` / `/api/perfis`), fallbackando para especialidades existentes nos perfis caso necessário.

**Non-Goals:**
- Alterar o esquema de tabelas principais além do acréscimo de metadados de origem de solicitação e exibição formatada.

## Decisions

1. **Atributo `origem_menu`**:
   - Salvar a string `origem_menu` (ex: `'Sistema LEC'`, `'Navegação'`) no payload de criação/atualização de solicitações e respostas.
   - Na renderização da tabela do Histórico (`Historico.vue`), incluir a coluna `<th>Origem / Menu</th>` logo após `<th>Data / Hora</th>`.

2. **Integração Dinâmica de Especialidades**:
   - Importar `usePerfisStore` em `InteracoesLec.vue` e `Historico.vue`.
   - Utilizar uma propriedade computada `especialidadesDisponiveis` derivada de `perfisStore.perfis.map(p => p.especialidade)` (filtrando nulos/duplicados) para alimentar os seletores de especialidade.

## Risks / Trade-offs

- **[Risk]** Registros legados no Histórico sem `origem_menu`.
  - *Mitigation*: Fallback para `'Sistema LEC'` quando a propriedade estiver ausente em solicitações antigas.
