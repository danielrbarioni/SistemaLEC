## ADDED Requirements

### Requirement: Justificativa obrigatória na rejeição de solicitações
O sistema DEVE exigir o preenchimento de uma justificativa antes de efetivar a rejeição de qualquer solicitação no menu Comunicação LEC (Inclusão, Edição, Standby ou Exclusão). Essa justificativa DEVE ser enviada à API e armazenada tanto no registro da resposta quanto vinculada aos detalhes da solicitação rejeitada.

#### Scenario: Gestor clica em Rejeitar solicitação
- **WHEN** o usuário com perfil GESTAO_LEC ou ADMIN clica no botão "Rejeitar" de uma solicitação pendente
- **THEN** o sistema abre um modal solicitando obrigatoriamente o motivo/justificativa da rejeição
- **WHEN** o gestor preenche a justificativa e confirma
- **THEN** o status da solicitação é alterado para `REJEITADO` e a justificativa é gravada no banco

#### Scenario: Tentativa de confirmação sem preencher justificativa
- **WHEN** o gestor tenta confirmar a rejeição sem digitar nenhuma justificativa
- **THEN** o sistema impede o envio e alerta que o campo é obrigatório

### Requirement: Exibição unificada de procedimentos na aba Histórico Concluído
Na aba *Histórico Concluído (Aprovadas/Rejeitadas)* de *Comunicação LEC*, cada procedimento concluído DEVE ser exibido em uma linha única (desconsiderando a linha de resposta isolada e consolidando os dados da solicitação e da resposta em um único registro).

#### Scenario: Visualização do Histórico Concluído em Comunicação LEC
- **WHEN** o usuário acessa a sub-aba *Histórico Concluído* em *Comunicação LEC*
- **THEN** cada solicitação aprovada ou rejeitada aparece exatamente uma vez
- **THEN** a tabela exibe a data/hora da ação e o status da conclusão

### Requirement: Modal detalhado de Descrição da Solicitação e Resposta
O modal disparado pelo botão *📄 Ver Descrição* na tabela de solicitações DEVE exibir os dados estruturados da solicitação (Data/Hora, Usuário Solicitante, Justificativa clínica) e, caso a solicitação já tenha sido respondida (concluída), DEVE exibir também os dados da resposta (Data/Hora da resposta, Usuário que respondeu, Status e Justificativa da rejeição/observação).

#### Scenario: Abertura do modal de descrição em solicitação concluída com rejeição
- **WHEN** o usuário clica em *📄 Ver Descrição* em uma solicitação rejeitada
- **THEN** o modal exibe a seção de dados da solicitação inicial e uma seção destacada de "Dados da Resposta" contendo a data/hora, usuário executor e o motivo da rejeição

### Requirement: Otimização do layout e barra de rolagem superior em tabelas
As tabelas do menu *Comunicação LEC* (formulários e acompanhamento de solicitações) DEVEM possuir visualização compacta e ajustada à tela. Quando houver necessidade de rolagem horizontal, o componente DEVE dispor de uma barra de rolagem horizontal superior sincronizada com a rolagem inferior para navegação ágil.

#### Scenario: Visualização da tabela de acompanhamento de solicitações
- **WHEN** o usuário visualiza as tabelas no menu Comunicação LEC
- **THEN** o conteúdo é distribuído de forma fluida e legível
- **THEN** caso a largura ultrapasse o contêiner, uma barra de rolagem superior sincronizada permite deslocamento horizontal sem rolar até a base da página
