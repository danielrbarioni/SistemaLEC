# Proposal: Exportar Histórico para Excel

## Why

A equipe de Gestão LEC e os usuários das especialidades precisam extrair relatórios auditáveis e consolidados dos registros históricos do sistema para fins de conferência clínica, prestação de contas, análises administrativas e cruzamento de dados externos. Atualmente, os dados do menu Histórico só podem ser visualizados na interface web, sem a possibilidade de exportação estruturada em planilha Excel (`.xlsx`).

Disponibilizar a exportação com seleção de intervalo temporal e aderência a todos os filtros ativos permitirá extrações precisas e imediatas diretamente pelo usuário.

## What Changes

- **Botão 'Exportar Histórico' no menu Histórico**: Adicionar um botão no canto superior direito da tabela de histórico (logo abaixo do bloco de filtros).
- **Modal de Intervalo de Exportação**:
  - Ao clicar no botão, abrir modal solicitando o intervalo de datas (`Data de` e `Data até`).
  - **Valores padrão**: `Data de` preenchido com a data da ação mais antiga registrada no histórico carregado; `Data até` preenchido com o dia atual.
  - **Aproveitamento de filtros prévios**: Se o usuário já tiver preenchido `Data Início` e/ou `Data Fim` no painel de filtros antes de abrir o modal, esses valores serão pré-carregados no modal (permanecendo editáveis pelo usuário).
- **Filtragem Dinâmica na Exportação**:
  - A exportação respeitará rigorosamente todos os filtros ativos na tela (Prontuário/Paciente, Procedimento, Especialidade, Ação, Tipo de Evento, Status, Perfil Executor, Usuário Executor) combinados com o intervalo de datas confirmado.
- **Estrutura das Colunas da Planilha Excel**:
  1. `DATA/HORA`
  2. `ORIGEM/MENU`
  3. `PRONTUÁRIO`
  4. `PACIENTE`
  5. `ESPECIALIDADE`
  6. `PROCEDIMENTO`
  7. `AÇÃO`
  8. `TIPO DE EVENTO`
  9. `STATUS`
  10. `PERFIL EXECUTOR`
  11. `USUÁRIO EXECUTOR`
  - Para campos que não se aplicam à ação registrada (por exemplo, `PROCEDIMENTO` ou `PRONTUÁRIO` em ações de criação de usuário ou perfil), preencher explicitamente como `NA`.
- **Metadados / Cabeçalho Institucional acima da Tabela**:
  - Nas primeiras linhas da planilha (antes do cabeçalho da tabela de dados), exibir:
    - Data/Hora em que a exportação foi realizada.
    - Intervalo de datas selecionado na exportação.
    - Demais filtros ativos aplicados (ou indicação de "Nenhum outro filtro aplicado").
- **Geração de Arquivo Excel (.xlsx)**:
  - Adição de biblioteca de manipulação de planilhas Excel no frontend (`xlsx` / SheetJS) para gerar e baixar instantaneamente o arquivo formatado no navegador sem sobrecarregar o backend.

## Capabilities

### New Capabilities
- `historico-exportacao-excel`: Capacidade de exportar registros do histórico de ações para arquivo Excel (.xlsx), incluindo modal de parametrização de período, aplicação de filtros ativos, metadados de cabeçalho e preenchimento de `NA` para campos não aplicáveis.

### Modified Capabilities
<!-- Nenhuma especificação de capacidade existente teve suas regras alteradas; trata-se de extensão funcional do menu Histórico. -->

## Impact

- **Frontend**:
  - `frontend/src/views/Historico.vue`: Inclusão do botão de exportação, modal de confirmação de intervalo de datas, função de montagem e download do arquivo Excel.
  - `frontend/package.json`: Adição da biblioteca `xlsx` para geração do arquivo `.xlsx`.
- **Backend / Banco de Dados**:
  - Sem alterações estruturais no banco de dados. Os dados consumidos vêm das listagens já providas pela API (`/api/solicitacoes` e rotas do histórico).
