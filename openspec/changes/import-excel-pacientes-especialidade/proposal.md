# Proposal: Importação de Planilha Excel de Pacientes por Especialidade (Gestão LEC)

## Why

Atualmente, o processo de inicialização e migração de filas de pacientes por especialidade depende de intervenção manual direta no código ou no banco de dados. Para dar autonomia completa à equipe de **Gestão LEC**, é necessário permitir que os próprios gestores importem planilhas Excel (`.xlsx`/`.xls`) contendo as filas de pacientes pré-existentes diretamente pela interface do sistema (no menu Pacientes).

## What Changes

- **Backend (FastAPI)**:
  - Criar o endpoint `POST /api/pacientes/importar-excel` para processamento de planilhas Excel (via `pandas` / `openpyxl`).
  - Restringir o acesso do endpoint exclusivamente para usuários com perfil **Gestão LEC**.
  - Mapear as colunas da planilha:
    - **A (`id_fila`)**: Identificador único da fila do procedimento.
    - **B (`Prontuário`)**: Prontuário do paciente (busca/criação do paciente e vinculação ao AGHU).
    - **C (`id_procedimento`)**: Código do procedimento no AGHU (vincula ao nome/código do procedimento).
    - **D (`medico_responsavel`)**: Usuário EBSERH do médico responsável. Se o médico não possuir cadastro como usuário dessa especialidade, cria automaticamente o registro de `User` com `username = medico_responsavel` e `nome_completo = None` (usando o username como fallback enquanto o nome não for preenchido).
    - **E (`sin_oncologico`)**, **F (`uti`)**, **H (`sin_rt`)**: Desconsiderar nesta versão.
    - **G (`id_motivo_status`)**: Identificador do motivo/status.
    - **I (`id_especialidade`)**: Código da especialidade no AGHU.
    - **J (`swalis`)**: Pontuação de prioridade SWALIS.
    - **K (`sin_judicializado`)**: Flag de processo judicializado.
    - **L (`dth_indicação`)**: Data e hora da indicação cirúrgica.
  - Criar/atualizar automaticamente os registros de `Paciente`, `Solicitacao` e cadastros de médicos pendentes.

- **Frontend (Vue 3 / TypeScript)**:
  - Adicionar botão **"Importar Planilha de Pacientes"** na tela do menu **Pacientes** (visível somente para o perfil **Gestão LEC**).
  - Criar modal interativo para upload do arquivo `.xlsx`/`.xls`, exibição de progresso e relatório detalhado do resultado da importação (quantidade de solicitações criadas, pacientes associados e novos médicos cadastrados).

## Capabilities

### New Capabilities
- `importacao-planilha-pacientes-gestao-lec`: Capacidade da equipe de Gestão LEC importar planilhas Excel pré-existentes de filas de pacientes por especialidade, incluindo autocadastro de médicos responsáveis não registrados.

### Modified Capabilities
- `pacientes-view`: Exibição de botão e modal de importação condicionados ao perfil `Gestão LEC`.

## Impact

- **Backend**: Novos módulos/serviços de parsing de Excel e criação em lote de solicitações e usuários médicos.
- **Banco de Dados**: População das tabelas `pacientes`, `solicitacoes` e criação de `users` com `nome_completo` nulo (utilizando `username` como fallback).
- **Frontend**: Componente modal de upload em `PacientesView.vue`.
