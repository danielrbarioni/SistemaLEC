# Tasks

## 1. Modelo de Configuração e Backend da Navegação (AGHU Read-Only + SQLite Local)

- [x] 1.1 Criar o modelo e migração da tabela `navegacao_config` no SQLite local (`src/models/navegacao_config.py`, `src/helpers/database_migration_helper.py` e `src/main.py`) com seed automático das siglas de grades EPO (`EPO, EPG, POO, OEP, POT, POF`), Consultas Pré-Op (`RIS, PPC, RCI, OHR, PPO`), APA (`ANE, TAN`) e dos 8 Grupos de Exames Pré-Operatórios (*Laboratório*, *Raio X*, *Espirometria*, *Ecocardiograma Transtorácico*, *Cintilografia Miocárdica*, *Ressonância Magnética (todas)*, *Holter 24h* e *Teste de Esteira*), verificando a criação da tabela sem erros
- [x] 1.2 Implementar os endpoints de configuração e busca ao vivo no catálogo do AGHU em `src/routers/navegacao.py` (`GET /api/navegacao/config`, `PUT /api/navegacao/config`, `GET /api/navegacao/aghu/grades`, `GET /api/navegacao/aghu/exames`) e registrar o roteador em `src/main.py`
- [x] 1.3 Implementar o endpoint de consulta consolidada dos 5 painéis da jornada cirúrgica (`GET /api/navegacao/paineis`) em `src/routers/navegacao.py`, utilizando queries `DISTINCT ON` no PostgreSQL do AGHU (com recorte temporal e cache TTL + opção de forçar atualização `refresh=true`) para retornar as Tabelas `1`, `2.1`, `2.2` (enriquecida com os grupos de exames e consultas pré-operatórias mais recentes), `3.1` e `3.2`

## 2. Interface dos Painéis da Jornada Cirúrgica e Configuração no Frontend (`NavegacaoLec.vue`)

- [x] 2.1 Remover o modal bloqueante de "Funcionalidade em desenvolvimento" em `frontend/src/views/NavegacaoLec.vue` (mantendo a rota e o menu lateral restritos ao perfil `ADMIN`) e implementar a barra superior com **Busca Global por Prontuário/Paciente** (que exibe em qual(is) das 5 tabelas o paciente se encontra com atalho direto), seletor de janela temporal e botão **"Atualizar dados do AGHU"**
- [x] 2.2 Implementar em `frontend/src/views/NavegacaoLec.vue` as abas e tabelas das 5 etapas da jornada cirúrgica (**Tabela 1** — EPO Agendada, **Tabela 2.1** — EPO Faltosa, **Tabela 2.2** — EPO Realizada com exibição em **cards** dos exames pré-op e consultas pré-op solicitados por paciente, **Tabela 3.1** — APA Não Realizada, **Tabela 3.2** — APA Realizada), com todas as colunas, cards de status/data, filtros automáticos, filtros modificáveis (prontuário, grades, intervalo de datas, exame/parecer solicitado e status), paginação e ordenação especificados
- [x] 2.3 Implementar em `frontend/src/views/NavegacaoLec.vue` o modal **"Configurar Grades e Exames do Circuito Cirúrgico"**, permitindo visualizar, pesquisar ao vivo no AGHU e adicionar/remover siglas de grades (EPO, Pré-Op, APA) e siglas de exames em cada grupo pré-operatório

## 3. Verificação, Build e Deploy

- [x] 3.1 Compilar o frontend (`npm run build`) verificando zero erros de TypeScript (`vue-tsc`) e Vite
- [x] 3.2 Implantar as alterações do backend e frontend na VM de produção (`10.34.0.202`), validar a resposta real de `/api/navegacao/paineis` conectada ao PostgreSQL do AGHU e reiniciar o serviço `sistemalec.service`
