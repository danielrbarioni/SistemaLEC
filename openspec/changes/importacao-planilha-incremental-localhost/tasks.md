## 1. Preservação do Banco da VM e Restauração

- [x] 1.1 Restaurar banco de dados da VM (`10.34.0.202`) para o backup original de 2.364 solicitações.
- [x] 1.2 Garantir que nenhuma alteração ou script modifique o banco da VM durante os testes locais.

## 2. Comparação Incremental de Planilhas (Localhost)

- [x] 2.1 Implementar indexação por `(codigo_paciente, procedimento)` em `src/helpers/excel_import_helper.py`.
- [x] 2.2 Garantir que novas planilhas (ex: 2.518 linhas) atualizem os registros existentes e acrescentem apenas os excedentes.

## 3. Preparação do Ambiente Web para o Gestor LEC

- [x] 3.1 Corrigir captura de drag-and-drop e prevenir comportamento padrão de abertura no navegador em `ImportarPlanilhaPacientesModal.vue`.
- [x] 3.2 Garantir suporte a requisições `POST` multipart com cabeçalho explícito e tratamento de rotas em `pacienteService.ts` e `src/routers/paciente.py`.
