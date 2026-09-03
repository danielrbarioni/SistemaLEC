## 1. Banco de Dados e Modelos (Backend)

- [x] 1.1 Adicionar a coluna `lateralidade` nos modelos SQLAlchemy `Paciente` e `Solicitacao` com valor padrão `'Indefinida'`
- [x] 1.2 Atualizar inicialização do banco SQLite (`src/main.py`) e migração para incluir coluna `lateralidade` nas tabelas `pacientes` e `solicitacoes` preenchendo registros legados com `'Indefinida'`
- [x] 1.3 Atualizar schemas Pydantic e provedores SQLite para suportar `lateralidade` em requisições de criação e edição

## 2. Correção de Edição e Categorização (Backend)

- [x] 2.1 Aprimorar a localização e correspondência do procedimento em `src/routers/solicitacao.py` por chave composta (`prontuario`, `especialidade`, `procedimento_anterior`, `medico_responsavel`) para evitar colisões em pacientes com múltiplos procedimentos
- [x] 2.2 Garantir que a rota de aprovação de edição atualize estritamente o procedimento alvo e mantenha `categorizacao` e `lateralidade` consistentes
- [x] 2.3 Validar que o endpoint de listagem de pacientes retorne `categorizacao` e `lateralidade` devidamente preenchidas

## 3. Frontend: Formulários de Edição, Inclusão e Lateralidade

- [x] 3.1 Em `InteracoesLec.vue`, garantir que `abrirModalEdicao(proc)` popule `formEdicao.categorizacao` com a categoria atualmente atribuída e `formEdicao.lateralidade` com a lateralidade do procedimento
- [x] 3.2 Corrigir o cálculo do estado anterior (`obterEstadoAnteriorProcedimento`) em `InteracoesLec.vue` para comparar apenas com o procedimento selecionado
- [x] 3.3 Adicionar campo obrigatório de Lateralidade nos formulários de Inclusão (`INSERIR`) e Edição (`EDITAR`) com as 4 opções (`lado esquerdo`, `lado direito`, `bilateral`, `não se aplica`)
- [x] 3.4 Validar o preenchimento obrigatório da lateralidade no envio de novas inclusões e edições

## 4. Frontend: Visualização e Histórico

- [x] 4.1 Exibir a informação de lateralidade nos cards de procedimentos em `InteracoesLec.vue` e `Pacientes.vue`
- [x] 4.2 Adicionar exibição de lateralidade e diffs de alteração de lateralidade no menu `Historico.vue`

## 5. Validação, Build e Deploy

- [x] 5.1 Executar validação de tipos e build do frontend (`npm run build`) e verificação do backend
- [x] 5.2 Testar no ambiente local os cenários de múltiplos procedimentos, persistência de categorização e obrigatoriedade da lateralidade
- [x] 5.3 Executar migração do banco na VM (`10.34.0.202`), sincronizar arquivos, reiniciar serviço `sistemalec` e comitar/push no GitHub
