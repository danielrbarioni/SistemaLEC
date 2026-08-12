# Tasks: Importação de Planilha Excel de Pacientes por Especialidade (Gestão LEC)

- [x] 1. Backend - Endpoint e Helper de Importação Excel <!-- id: 1 -->
  - [x] 1.1 Criar helper/parser em `src/helpers/excel_import_helper.py` para processar colunas A-L (`id_fila`, `Prontuário`, `id_procedimento`, `medico_responsavel`, `id_motivo_status`, `id_especialidade`, `swalis`, `sin_judicializado`, `dth_indicação`).
  - [x] 1.2 Implementar autocadastro de médico com `username = medico_responsavel`, `nome_completo = None` e associação com a especialidade importada quando o usuário não existir.
  - [x] 1.3 Criar endpoint `POST /api/pacientes/importar-excel` em `src/routers/paciente.py` com validação de permissão para perfil **Gestão LEC**.

- [x] 2. Frontend - Interface de Upload no Menu Pacientes <!-- id: 2 -->
  - [x] 2.1 Adicionar botão `"Importar Planilha"` em `frontend/src/views/PacientesView.vue`, condicionado ao perfil **Gestão LEC**.
  - [x] 2.2 Criar componente modal `frontend/src/components/ImportarPlanilhaPacientesModal.vue` para seleção de arquivo `.xlsx`, envio multipart e exibição de relatório do resultado.
  - [x] 2.3 Adicionar chamada de serviço na camada de API frontend (`frontend/src/services/pacienteService.ts`).

- [x] 3. Validação e Testes <!-- id: 3 -->
  - [x] 3.1 Testar upload de planilha de teste com médicos já existentes e novos médicos.
  - [x] 3.2 Verificar se o fallback de `username` (quando `nome_completo` está nulo) é exibido corretamente no menu Pacientes e Comunicação LEC.
  - [x] 3.3 Validar a restrição de acesso garantindo que apenas o perfil **Gestão LEC** visualize e execute a importação.
