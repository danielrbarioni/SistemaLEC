# Proposal: Exibição da Data/Hora de Inserção e Reordenação Multi-Critério no Menu Pacientes

## Summary
Adicionar a exibição da **data e hora de inserção na LEC** para cada procedimento cirúrgico cadastrado na visualização do menu **Pacientes** (tanto como coluna na tabela principal quanto no modal de detalhes individuais do paciente). Além disso, reestruturar a ordenação padrão de procedimentos no menu Pacientes seguindo 3 critérios estritos:
1. **Prioridade Swalis**: do mais crítico para o menos crítico (`A1` > `A2` > `B` > `C` > `D` > `Sem Swalis / Não informado`).
2. **Data/Hora de Inserção na LEC**: do mais antigo para o mais recente (ordem cronológica de entrada na fila).
3. **Ordem Alfabética**: desempate em ordem alfabética do Nome do Paciente / Procedimento.

## Why
- **Visibilidade de Tempo de Espera**: A informação de quando o paciente foi inserido na fila da LEC já existe no banco de dados (`data_criacao` da solicitação de inclusão / importação de planilha), mas não estava visível diretamente na tabela do menu Pacientes. Essa informação é essencial para os operadores avaliarem a antiguidade do paciente na fila cirúrgica.
- **Hierarquização Clínica e Cronológica de Prioridades**: A ordenação anterior era puramente alfabética por nome de paciente. A ordenação clínica correta deve priorizar pacientes com classificação Swalis mais urgente e, em caso de igualdade de gravidade, priorizar quem aguarda há mais tempo na fila (data de inserção mais antiga), mantendo o critério alfabético apenas como desempate final.

## Key Changes
1. **Mapeamento e Preservação da Data/Hora de Inserção do Procedimento**:
   - Para procedimentos importados via planilha Excel: utiliza a data/hora registrada na importação (coluna "Data de inserção" / `dth_indicacao`, persistida em `Solicitacao.data_criacao`).
   - Para procedimentos incluídos manualmente pelo sistema LEC: utiliza a data e hora do registro da solicitação de inclusão (`Solicitacao.data_criacao`).
   - Garante que a data de inserção original seja preservada mesmo se o procedimento passar por edições posteriores (`EDITAR` ou `STANDBY`).

2. **Exibição na Tabela Principal de Pacientes**:
   - Adiciona a coluna **"Data de Inserção"** na tabela compacta do menu Pacientes (`Pacientes.vue`).
   - Formatação consistente: `DD/MM/AAAA HH:mm` (ex.: `15/05/2024 14:30`).

3. **Exibição no Modal de Detalhes do Paciente**:
   - No quadro/janela de cada procedimento vinculado do paciente, exibir o campo **"Data de Inserção"** junto aos detalhes de Judicialização, Swalis e Médico Responsável.

4. **Reordenação Multi-Critério dos Procedimentos (`procedimentosFlat`)**:
   - **Critério 1 - Swalis**: `A1` (rank 1) > `A2` (rank 2) > `B` (rank 3) > `C` (rank 4) > `D` (rank 5) > `Sem Swalis / Não informado / '—'` (rank 6).
   - **Critério 2 - Data/Hora de Inserção**: ordenação cronológica crescente (datas mais antigas aparecem primeiro no topo da lista).
   - **Critério 3 - Ordem Alfabética**: `localeCompare('pt-BR')` por nome do paciente / procedimento como desempate final.

## Impact & Scope
- **Frontend**:
  - `frontend/src/views/Pacientes.vue`: ajuste no mapa `todosPacientesMap`, adição da coluna na tabela `procedimentosFlat`, novo item no modal de detalhes e nova lógica de ordenação em múltiplos níveis no computed `procedimentosFlat` e na lista de procedimentos do paciente.
- **Backend / Database**:
  - Nenhuma alteração estrutural de banco de dados necessária, pois a informação já é persistida no modelo `Solicitacao.data_criacao` e no histórico de solicitações.
