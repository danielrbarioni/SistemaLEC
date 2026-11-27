# Tasks

## 1. Banco de Dados e Modelos — Persistência de Classificações e Configuração Pós-APA

- [x] 1.1 Criar o modelo `NavegacaoClassificacao` (`navegacao_classificacoes`) em `src/models/navegacao_config.py` e registrar sua migração automática em `src/helpers/database_migration_helper.py`, verificando a criação da tabela no SQLite
- [x] 1.2 Estender `DEFAULT_NAVEGACAO_CONFIG` e `NavegacaoConfigUpdate` em `src/routers/navegacao.py` com a chave `grades_pos_apa` (`Grades de Consultas Solicitadas pela APA`), garantindo retrocompatibilidade com configurações existentes no banco

## 2. Backend — Motor de Classificações, Encadeamento Temporal, Promoções e Consultas Pós-APA

- [x] 2.1 Implementar em `src/routers/navegacao.py` a lógica de cruzamento dos eventos do AGHU com `navegacao_classificacoes`, validando o encadeamento temporal (`numero_consulta_ref` e `data_consulta_ref`), a promoção `REALIZADA_SEM_REGISTRO_AGHU` (`1.2 -> 2` e `3.2 -> 4`) e o enriquecimento de `consultas_pos_apa` na `Tabela 4`
- [x] 2.2 Criar em `src/routers/navegacao.py` os endpoints `POST /api/navegacao/classificar`, `POST /api/navegacao/classificacao/ticar` e `DELETE /api/navegacao/classificacao/{id}` (desfazer), verificando a compilação Python sem erros

## 3. Frontend — Subtabelas, Alertas Vermelhos, Check de Ações, Desfazimento e Coluna Pós-APA

- [x] 3.1 Atualizar `frontend/src/views/NavegacaoLec.vue` para exibir o seletor de `Lista Principal` e `Subtabelas` nas Tabelas `1.2`, `2`, `3.2` e `4`, com badges vermelhos de alerta para ações pendentes não ticadas (nas abas das subtabelas e nos cartões superiores das tabelas)
- [x] 3.2 Adicionar em `frontend/src/views/NavegacaoLec.vue` os botões de classificação na Lista Principal, o botão/checkbox de "Ticar ação realizada" nas subtabelas com alerta, e o botão "Desfazer classificação" no card da classificação (inclusive para pacientes promovidos às Tabelas `2` e `4` via `Realizada (sem registro no AGHU)`)
- [x] 3.3 Adicionar em `frontend/src/views/NavegacaoLec.vue` a coluna `Consultas solicitadas pela APA` e seus filtros (`Situação` e `Grades`) na `Tabela 4`, além da aba `Grades de Consultas Solicitadas pela APA` no modal `⚙️ Consultas e Exames monitorados`, validando o build (`npm run build`)

## 4. Deploy e Verificação em Produção (VM)

- [x] 4.1 Implantar backend e frontend na VM (`10.34.0.202`), reiniciar `sistemalec.service` e testar o ciclo completo de classificação, alerta vermelho, ticar ação realizada, promoção `1.2 -> 2` / `3.2 -> 4`, desfazimento e coluna `Consultas solicitadas pela APA` na `Tabela 4`
