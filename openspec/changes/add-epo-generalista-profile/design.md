## Context

O Sistema LEC possui os perfis institucionais padrão **ADMIN**, **GESTÃO LEC**, **NENHUM** e múltiplos perfis do tipo **ESPECIALIDADE** (Ortopedia, Plástica, Urologia, etc.).
Foi solicitada a criação do perfil **EPO GENERALISTA**, voltado para enfermeiros gerais da EPO. Esse perfil precisa ser listado no menu Perfis logo abaixo de Gestão LEC e acima das Especialidades, possuir a cor visual laranja (`bg-orange-100 text-orange-800 border-orange-200`) e operar com as permissões de enfermeiro sem a restrição de ter os dados filtrados por uma única especialidade.

## Goals / Non-Goals

**Goals:**
- Adicionar o perfil padrão `EPO GENERALISTA` com tipo `EPO_GENERALISTA` no seed/banco de dados e no frontend.
- Definir a cor da badge do perfil como laranja.
- Garantir a ordenação exata da lista no menu Perfis: ADMIN → GESTÃO LEC → **EPO GENERALISTA** → ESPECIALIDADES → NENHUM.
- Garantir que usuários com o perfil `EPO GENERALISTA` possuam o comportamento assistencial de enfermeiro (bloqueio no menu Comunicação LEC) e possam visualizar os dados globais de todas as especialidades sem ter um filtro automático de especialidade aplicado.

**Non-Goals:**
- Não permitir que usuários `EPO GENERALISTA` criem solicitações assistenciais na Comunicação LEC.
- Não alterar a estrutura do banco de dados existente de solicitações ou usuários além da adição do perfil.

## Decisions

1. **Definir Perfil EPO GENERALISTA no Seed/Database**:
   - `id`: `EPO_GENERALISTA`
   - `nome`: `EPO GENERALISTA`
   - `tipo`: `EPO_GENERALISTA` (ou `ENFERMEIRO_GERAL`)
   - `cor`: `bg-orange-100 text-orange-800 border-orange-200`
   - `especialidade`: `None`

2. **Ordenação dos Perfis no Frontend ([perfis.ts](file:///c:/Users/daniel.barioni/.gemini/antigravity-ide/scratch/Antigravity%20IDE/Sistema%20LEC/frontend/src/stores/perfis.ts) e [Perfis.vue](file:///c:/Users/daniel.barioni/.gemini/antigravity-ide/scratch/Antigravity%20IDE/Sistema%20LEC/frontend/src/views/Perfis.vue))**:
   - Ordem fixa de exibição:
     1. ADMIN (`id: ADMIN`)
     2. Gestão LEC (`id: GESTAO_LEC`)
     3. **EPO GENERALISTA** (`id: EPO_GENERALISTA`)
     4. Perfis de Especialidades (`tipo: ESPECIALIDADE`)
     5. NENHUM (`id: NENHUM`)

3. **Verificação de Permissão de Enfermeiro ([InteracoesLec.vue](file:///c:/Users/daniel.barioni/.gemini/antigravity-ide/scratch/Antigravity%20IDE/Sistema%20LEC/frontend/src/views/InteracoesLec.vue))**:
   - Atualizar a checagem `isEnfermeiro` para incluir `perfilNome.includes('epo generalista') || perfilTipo === 'EPO_GENERALISTA'`.

4. **Filtro Automático de Especialidade ([Pacientes.vue](file:///c:/Users/daniel.barioni/.gemini/antigravity-ide/scratch/Antigravity%20IDE/Sistema%20LEC/frontend/src/views/Pacientes.vue) / [NavegacaoLec.vue](file:///c:/Users/daniel.barioni/.gemini/antigravity-ide/scratch/Antigravity%20IDE/Sistema%20LEC/frontend/src/views/NavegacaoLec.vue))**:
   - `espSelecionada` aplicará filtro fixo apenas quando `perfil.tipo === 'ESPECIALIDADE'`. Para `EPO_GENERALISTA`, `ADMIN` e `GESTAO_LEC`, o filtro de especialidade virá nulo por padrão (sem restrição).

## Risks / Trade-offs

- [Risco]: Esquecer de incluir `EPO_GENERALISTA` em algum local que valida `ESPECIALIDADE`.
  - *Mitigação*: Manter verificação estrita de `p.tipo === 'ESPECIALIDADE'` separada de `p.tipo === 'EPO_GENERALISTA'`.
