## Context

O perfil OBSERVADOR foi introduzido para garantir um ambiente seguro de visualização para usuários que não possuem perfil formal de edição. Para aprimorar a experiência do usuário e a clareza da interface, cada menu principal deve ajustar quais componentes renderiza.

## Goals / Non-Goals

**Goals:**
- Menu Comunicação LEC: Ocultar o card/formulário de envio de novas solicitações se o perfil for `OBSERVADOR`, exibindo apenas a tabela de "Acompanhamento das Solicitações" com filtros operacionais.
- Menu Navegação LEC: Manter abas de especialidade e filtros visíveis, mas omitir/bloquear solicitações de APA.
- Menu Pacientes: Manter a listagem e filtros de pacientes totalmente disponíveis em modo de consulta.
- Menu Histórico: Manter a tabela e os filtros de histórico totalmente disponíveis em modo de consulta.
- Menu Perfis: Exibir a lista de perfis e tabela de usuários, mas ocultar formulários de criação/edição de usuários para o perfil `OBSERVADOR`.

**Non-Goals:**
- Modificar o fluxo de permissões de escrita dos perfis ADMIN, GESTÃO LEC ou ESPECIALIDADE.

## Decisions

### Decisão 1: Renderização Condicional no Frontend via `perfisStore.perfilAtivo`
- Utilizar `v-if="perfisStore.perfilAtivo.tipo !== 'OBSERVADOR'"` nos formulários de criação/edição e botões mutativos nas views `InteracoesLec.vue`, `NavegacaoLec.vue` e `Perfis.vue`.

## Risks / Trade-offs

- **[Risco] Ocultar seções desnecessárias afetar a navegação de usuários ADMIN** → *Mitigação:* As condicionais se aplicam exclusivamente quando `perfilAtivo.tipo === 'OBSERVADOR'`. Ao alternar para ADMIN, todas as ferramentas de criação/edição reaparecem imediatamente.
