## 1. Frontend - Ajustar agregação de solicitações em Pacientes.vue

- [x] 1.1 Em `Pacientes.vue`, atualizar a filtragem de `approvedSolics` na propriedade `pacientesProcessados` para desconsiderar `evento_tipo === 'RESPOSTA'`.

## 2. Backend - Ajustar reconstrução de procedimentos em solicitacao_controller.py

- [x] 2.1 Em `src/controllers/solicitacao_controller.py`, atualizar a lista `approved_solics` dentro de `criar_solicitacao` para desconsiderar `s.get("evento_tipo") == "RESPOSTA"`.

## 3. Validação

- [x] 3.1 Verificar no frontend que os procedimentos de um paciente com solicitação aprovada aparecem apenas uma vez na tabela e modal do menu Pacientes.
- [x] 3.2 Verificar no frontend que o menu Histórico mantém a exibição das 2 entradas (Solicitação e Resposta) para cada ação aprovada.
