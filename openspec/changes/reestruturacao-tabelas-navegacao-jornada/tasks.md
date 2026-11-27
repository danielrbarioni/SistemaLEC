# Tasks

## 1. Backend — Reestruturação dos Painéis da Navegação em 6 Tabelas

- [x] 1.1 Atualizar `src/routers/navegacao.py` (`GET /api/navegacao/paineis`) para separar o estágio EPO em `tabela_1_1_epo_agendada` (apenas `status == "Agendado"`, hoje/data futura), `tabela_1_2_epo_nao_realizada` (`status in ("Falta do paciente", "Falta do profissional", "Agendado (Data Passada)")`) e `tabela_2_epo_realizada` (`status == "Realizado"`), verificando a sintaxe e estrutura do payload de retorno
- [x] 1.2 Atualizar `src/routers/navegacao.py` (`GET /api/navegacao/paineis`) para separar o estágio APA em `tabela_3_1_apa_agendada` (apenas `status == "Agendado"`, hoje/data futura), `tabela_3_2_apa_nao_realizada` (`status in ("Falta do paciente", "Falta do profissional", "Agendado (Data Passada)")`) e `tabela_4_apa_realizada` (`status == "Realizado"`), mantendo as ordenações (`ASC` para `1.1`, `1.2`, `2`, `3.1`, `3.2` e `DESC` para `4`)

## 2. Frontend — Atualização das 6 Abas, Nomenclaturas, Filtros e Busca Global

- [x] 2.1 Atualizar `frontend/src/views/NavegacaoLec.vue` para exibir os 6 cards de abas em 2 fileiras agrupadas nos 4 Estágios (`T1_1` = `Tabela 1.1 — Consulta EPO agendada`, `T1_2` = `Tabela 1.2 — Consulta EPO não realizada`, `T2` = `Tabela 2 — Consulta EPO realizada` sem `+ Exames/Pré-Op`, `T3_1` = `Tabela 3.1 — APA agendada`, `T3_2` = `Tabela 3.2 — APA não realizada` e `T4` = `Tabela 4 — APA realizada`) e verificar a compilação do frontend (`npm run build`)
- [x] 2.2 Atualizar os filtros modificáveis de status (`T1_2` e `T3_2`), os filtros exclusivos de exames/consultas pré-op (`T2`) e a Busca Global nas 6 tabelas em `frontend/src/views/NavegacaoLec.vue`, validando o build sem erros

## 3. Deploy e Verificação em Produção (VM)

- [x] 3.1 Implantar `src/routers/navegacao.py` e o build do frontend na VM (`10.34.0.202`), reiniciar o serviço `sistemalec.service` e verificar via API `/api/navegacao/paineis?refresh=true` a contagem e distribuição real dos pacientes nas 6 tabelas (`1.1`, `1.2`, `2`, `3.1`, `3.2` e `4`)
