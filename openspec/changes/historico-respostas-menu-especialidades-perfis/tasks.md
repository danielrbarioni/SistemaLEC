## 1. Atualizações no Menu Histórico

- [x] 1.1 Em `frontend/src/views/Historico.vue`, adicionar a coluna "Origem / Menu" logo após a coluna "Data / Hora".
- [x] 1.2 Atualizar o backend e o frontend para registrar e exibir no Histórico os eventos de resposta/decisão efetuados por ADMIN ou GESTÃO LEC (ex: aprovação e rejeição).
- [x] 1.3 Incluir a propriedade `origem_menu` (ex: "Sistema LEC", "Navegação") nas solicitações e respostas.

## 2. Especialidades Dinâmicas a partir do Menu Perfis

- [x] 2.1 Em `frontend/src/views/InteracoesLec.vue`, carregar as especialidades dinamicamente através do `perfisStore` / `/api/perfis`, removendo o array fixo hardcoded.
- [x] 2.2 Atualizar os filtros e seletores de especialidade no Sistema LEC para utilizar a lista dinâmica de especialidades dos perfis cadastrados.
- [x] 2.3 Verificar o correto funcionamento e compilação do projeto.
