# historico-exportacao-excel Specification

## Purpose
Permite que os usuários exportem registros consolidados do histórico de ações do Sistema LEC em formato Excel (.xlsx), aplicando seleção de intervalo temporal e filtros vigentes com metadados de auditoria.

## Requirements

### Requirement: Botão de Exportação e Modal de Intervalo de Datas
O sistema SHALL disponibilizar o botão "Exportar Histórico" no canto superior direito da tabela de histórico (abaixo do bloco de filtros) exclusivamente para usuários com perfil ADMIN ou GESTÃO LEC. Para usuários de outros perfis (como Especialidades ou Observador), o botão NÃO SHALL ser exibido. Ao clicar no botão, o sistema SHALL exibir um modal de confirmação para definição do intervalo de datas da exportação (`Data de` e `Data até`).

#### Scenario: Visualização do botão por perfil autorizado
- **WHEN** o usuário autenticado possui perfil ativo ADMIN ou GESTÃO LEC
- **THEN** o botão "Exportar Histórico" é exibido no cabeçalho da tabela

#### Scenario: Ocultação do botão para outros perfis
- **WHEN** o usuário autenticado possui perfil de Especialidade ou Observador
- **THEN** o botão "Exportar Histórico" não é exibido

#### Scenario: Abertura do modal de exportação com intervalo padrão
- **WHEN** o usuário clica no botão "Exportar Histórico" e nenhum filtro de data prévio estiver preenchido
- **THEN** o modal abre exibindo `Data de` preenchida com a data do registro mais antigo carregado no histórico e `Data até` preenchida com o dia atual

#### Scenario: Abertura do modal herdando filtros de data ativos
- **WHEN** o usuário tiver previamente preenchido `Data Início` e/ou `Data Fim` no painel de filtros e clicar em "Exportar Histórico"
- **THEN** o modal abre exibindo essas respectivas datas já preenchidas nos campos de intervalo, permitindo edição antes da exportação

### Requirement: Aplicação de Filtros Ativos na Exportação
A rotina de exportação SHALL considerar todos os filtros ativos configurados na tela (Prontuário/Paciente, Procedimento, Especialidade, Ação, Tipo de Evento, Status, Perfil Executor e Usuário Executor), combinados com o intervalo de datas (`Data de` até `Data até`) confirmado no modal.

#### Scenario: Exportação com filtros combinados
- **WHEN** o usuário seleciona filtros específicos (ex.: especialidade, status ou usuário) e confirma a exportação
- **THEN** apenas os registros que atendem cumulativamente a esses filtros e ao intervalo de datas são incluídos na planilha gerada

### Requirement: Estrutura Padronizada de Colunas e Tratamento de NA
A planilha gerada SHALL conter exatamente 11 colunas na seguinte ordem:
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

Para qualquer campo que não se aplique à natureza do evento registrado (por exemplo, `PROCEDIMENTO` ou `PRONTUÁRIO` em ações de criação ou exclusão de perfis e usuários), o sistema SHALL preencher o valor com a sigla `NA`.

#### Scenario: Exportação de ação clínica com todos os campos aplicáveis
- **WHEN** o registro exportado for uma solicitação de procedimento
- **THEN** os campos de prontuário, paciente, especialidade e procedimento são preenchidos com seus valores reais

#### Scenario: Exportação de ação administrativa sem procedimento ou paciente
- **WHEN** o registro exportado for uma ação administrativa (como criação de usuário ou perfil)
- **THEN** os campos não aplicáveis (como PRONTUÁRIO, PACIENTE, ESPECIALIDADE e PROCEDIMENTO) são preenchidos exatamente como `NA`

### Requirement: Cabeçalho com Metadados da Extração
O arquivo Excel gerado SHALL conter, acima da tabela de dados, um bloco de metadados informando:
1. A data e hora em que a exportação foi realizada;
2. O intervalo de datas considerado (`Data de` até `Data até`);
3. O resumo dos demais filtros aplicados (ou indicação de que nenhum outro filtro foi selecionado).

#### Scenario: Geração do arquivo com cabeçalho institucional
- **WHEN** o usuário confirma a exportação
- **THEN** as primeiras linhas da planilha exibem a data/hora de exportação, o intervalo de datas e os filtros aplicados, seguidos pela linha de cabeçalho das 11 colunas e as linhas de dados correspondentes
