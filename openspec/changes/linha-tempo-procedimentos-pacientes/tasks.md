# Tasks

## 1. Frontend - Agregação da Linha do Tempo por Procedimento
- [x] 1.1 Em `frontend/src/views/Pacientes.vue`, implementar algoritmo de consolidação histórica em `todosPacientesMap` que correlaciona cada procedimento aos seus eventos correspondentes (inclusão, importação, edições, standby e respostas da Gestão LEC), ordenando-os cronologicamente e gerando o array `timeline`.
- [x] 1.2 Em `frontend/src/views/Pacientes.vue`, criar funções auxiliares para formatação dos tipos de ação, ícones, cores de marcadores e tratamento amigável das justificativas e detalhes de cada evento.

## 2. Frontend - Componente Visual da Linha do Tempo no Modal
- [x] 2.1 Em `frontend/src/views/Pacientes.vue`, implementar a renderização visual da linha do tempo vertical dentro do card de cada procedimento no modal de detalhes, contendo data/hora, badge da ação, usuário/perfil executor e a justificativa em destaque.
- [x] 2.2 Adicionar botões de expandir/recolher a linha do tempo nos cards de procedimentos para garantir uma leitura ergonômica mesmo em pacientes com muitos eventos.

## 3. Validação e Testes
- [x] 3.1 Validar a exibição da linha do tempo para procedimentos criados por importação de planilha, garantindo que a data e os detalhes de importação apareçam corretamente no evento inicial.
- [x] 3.2 Validar a exibição da linha do tempo para procedimentos que sofreram ações de edição, standby e respostas da Gestão LEC, verificando a preservação das justificativas e a ordenação temporal.
