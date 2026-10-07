# Design: Exportação do Histórico para Excel

## Context

O menu Histórico em `frontend/src/views/Historico.vue` carrega os eventos consolidados de solicitações cirúrgicas, respostas da Gestão LEC, cancelamentos e ações administrativas (criação/edição/exclusão de perfis, usuários e categorizações). A tela possui um painel de filtros robusto (Data Início, Data Fim, Prontuário/Paciente, Procedimento, Perfil Executor, Especialidade, Ação, Tipo de Evento, Status e Usuário Executor).

Para permitir que os usuários extraiam relatórios em Excel (.xlsx) respeitando os filtros ativos e parametrizando o intervalo temporal, implementaremos a geração direta da planilha no frontend com formatação estruturada de metadados e preenchimento de campos não aplicáveis com `NA`.

## Goals / Non-Goals

**Goals:**
- Botão visível "Exportar Histórico" no canto superior direito da tabela do histórico (logo abaixo dos filtros).
- Modal interativo para confirmação/ajuste do intervalo de datas da exportação (`Data de` e `Data até`).
- Respeitar cumulativamente todos os filtros selecionados na interface web combinados com o intervalo confirmado.
- Formatação das 11 colunas solicitadas: `DATA/HORA`, `ORIGEM/MENU`, `PRONTUÁRIO`, `PACIENTE`, `ESPECIALIDADE`, `PROCEDIMENTO`, `AÇÃO`, `TIPO DE EVENTO`, `STATUS`, `PERFIL EXECUTOR`, `USUÁRIO EXECUTOR`.
- Exibir explicitamente `NA` para campos que não se aplicam à ação registrada.
- Inserir metadados informativos no topo da planilha (Data/hora de exportação, Intervalo de datas, Outros filtros aplicados).

**Non-Goals:**
- Criar rotinas agendadas (cron) de exportação ou envio de planilhas por e-mail.
- Alterar o esquema ou as rotas de banco de dados no backend.

## Decisions

### Decisão 1: Geração da Planilha no Cliente com `xlsx` (SheetJS)
- **Escolha**: Adicionar a biblioteca `xlsx` ao frontend para montar a pasta de trabalho (`WorkBook`), compor as linhas de metadados e dados e acionar o download do arquivo `.xlsx` diretamente no navegador.
- **Racional**: Todos os dados históricos já estão carregados e normalizados no estado reativo de `Historico.vue`. A exportação no cliente é instantânea, não consome I/O de disco nem memória no servidor, e evita tráfego redundante de API.
- **Alternativa descartada**: Criar endpoint backend em FastAPI (`openpyxl`). Exigiria reenviar todos os estados de filtro via HTTP, reconsultar a base SQLite no servidor e gerenciar streaming de downloads.

### Decisão 2: Modal de Intervalo de Datas e Herança de Filtros
- **Escolha**: Criar o estado reativo `modalExportarAberto`, `exportDataInicio` e `exportDataFim`.
- **Comportamento dos defaults**:
  - `Data de`: Se o filtro `dataInicio` na tela já estiver preenchido, herda seu valor; caso contrário, busca a data mais antiga presente na lista de registros carregados.
  - `Data até`: Se o filtro `dataFim` na tela já estiver preenchido, herda seu valor; caso contrário, define a data de hoje (`YYYY-MM-DD`).
  - O usuário pode livremente alterar esses campos no modal antes de confirmar o download.

### Decisão 3: Estrutura da Planilha com Metadados Institucionais
A planilha gerada terá a seguinte estrutura tabular:
- Linha 1: Título em destaque: `SISTEMA LEC - RELATÓRIO DO HISTÓRICO DE AÇÕES`
- Linha 2: `Data/Hora da Exportação: <DD/MM/AAAA HH:mm:ss>`
- Linha 3: `Intervalo da Exportação: <DD/MM/AAAA> até <DD/MM/AAAA>`
- Linha 4: `Filtros Aplicados: <Resumo textual dos filtros vigentes ou 'Nenhum outro filtro aplicado'>`
- Linha 5: Linha em branco separadora
- Linha 6: Cabeçalhos das 11 colunas:
  `["DATA/HORA", "ORIGEM/MENU", "PRONTUÁRIO", "PACIENTE", "ESPECIALIDADE", "PROCEDIMENTO", "AÇÃO", "TIPO DE EVENTO", "STATUS", "PERFIL EXECUTOR", "USUÁRIO EXECUTOR"]`
- Linhas 7+: Registros de dados correspondentes.

### Decisão 4: Tratamento de Campos Inaplicáveis (`NA`)
- Para ações administrativas que não possuem vínculo com paciente ou cirurgia (ex.: `CRIAR_PERFIL`, `EXCLUIR_USUARIO`, `CRIAR_CATEGORIZACAO`):
  - `PRONTUÁRIO`: `NA`
  - `PACIENTE`: `NA`
  - `ESPECIALIDADE`: `NA` (ou a especialidade vinculada se houver, caso contrário `NA`)
  - `PROCEDIMENTO`: `NA`
- Para qualquer campo de identificação ausente ou vazio na ação específica, o valor será gravado como `NA`.

## Risks / Trade-offs

- **[Volume de dados muito grande para processar no browser]** → *Mitigação:* Os dados do histórico carregados pelo sistema já são pré-filtrados e paginados pelo backend, e testes demonstram que o SheetJS processa milhares de linhas em menos de 100ms no cliente.
- **[Formatação de datas e fusos horários]** → *Mitigação:* Utilizar o mesmo utilitário padronizado de formatação já estabelecido em `formatarDataHora` e extração de strings ISO.
