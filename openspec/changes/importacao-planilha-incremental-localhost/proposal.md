## Why

O gestor LEC precisa realizar a importação incremental de planilhas de pacientes por especialidade (ex: nova planilha da Plástica com 2.518 procedimentos vs 2.364 existentes) diretamente através da interface web do sistema em ambiente **localhost**. 

Para isso, o sistema deve:
1. Executar todas as validações e testes estritamente em **localhost**, sem alterar o banco de dados da máquina virtual (VM).
2. Comparar a nova planilha enviada pelo gestor com as solicitações já cadastradas, acrescentando apenas os novos registros (excedentes) e atualizando os existentes, sem gerar duplicatas nem apagar histórico.
3. Disponibilizar a funcionalidade de upload e drag-and-drop no modal de importação para uso direto pelo próprio Gestor LEC.

## What Changes

- **Ambiente de Desenvolvimento & Execução**:
  - Restrição de testes e execuções para **localhost** (banco local `data/app.db` e servidor local FastAPI `127.0.0.1:8000`), sem envio para a VM.
- **Lógica de Importação Incremental (`src/helpers/excel_import_helper.py`)**:
  - Indexação inteligente por `solic_id` e chave composta `(codigo_paciente, procedimento)`.
  - Comparação linha a linha da planilha enviada com o banco local.
  - Atualização dos registros existentes e inserção exclusiva de novas solicitações (excedentes).
- **Interface Web de Importação (`ImportarPlanilhaPacientesModal.vue` e `pacienteService.ts`)**:
  - Correção dos manipuladores de eventos de drag-and-drop e prevenção de drop no nível da janela (`window`).
  - Envio correto de requisições `POST` multipart/form-data com suporte às rotas com e sem barra final.

## Capabilities

### New Capabilities
- `importacao-planilha-incremental-localhost`: Capacidade de importação de planilhas Excel pelo Gestor LEC na interface web em localhost, aplicando comparação incremental que adiciona apenas excedentes e atualiza registros correspondentes.

### Modified Capabilities
*(nenhuma regra de negócio existente foi alterada)*

## Impact

- **Frontend**: Componente `ImportarPlanilhaPacientesModal.vue` e `pacienteService.ts`.
- **Backend**: Helper `excel_import_helper.py` e roteador `src/routers/paciente.py`.
- **Banco de dados**: Atualizado somente no ambiente **localhost** (`data/app.db`).
