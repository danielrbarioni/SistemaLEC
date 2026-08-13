## Why

Atualmente, enfermeiros estão associados a perfis de especialidades específicas e possuem restrições em ações assistenciais direcionadas (como na Comunicação LEC). Existe a necessidade de um novo perfil institucional, **EPO GENERALISTA**, voltado para enfermeiros gerais. Este perfil não possui restrição ou filtro por especialidade cirúrgica específica, permitindo visualizar dados globais e interagir nos menus permitidos sem estar preso a uma única especialidade.

## User Review Required

> [!IMPORTANT]
> **Definições do Perfil EPO GENERALISTA**:
> - **Tipo de Perfil**: `EPO_GENERALISTA` (Sem especialidade padrão vinculada).
> - **Posição na Lista de Perfis**: Logo abaixo de **GESTÃO LEC** e imediatamente acima dos perfis de **ESPECIALIDADES**.
> - **Cor da Badge**: **Laranja** (`bg-orange-100 text-orange-800 border-orange-200`).
> - **Permissões Assistenciais**: Mesmas permissões de um Enfermeiro (acesso ao menu Comunicação LEC restrito para solicitações assistenciais, mas acesso livre aos demais menus).
> - **Sem Filtro por Especialidade**: Ao navegar pelos menus permitidos (ex.: Pacientes), não será aplicado nenhum filtro fixo de especialidade, permitindo consultar e atuar em todas as especialidades.

## What Changes

- **Novo Perfil EPO GENERALISTA**:
  - Tipo: `EPO_GENERALISTA`.
  - Posição na lista de perfis: Abaixo de **GESTÃO LEC** e acima das **ESPECIALIDADES**.
  - Cor visual da badge: **Laranja**.
- **Permissões do Perfil EPO GENERALISTA**:
  - Mesmas permissões de um enfermeiro de especialidade (bloqueado na Comunicação LEC para solicitações assistenciais de inclusão/alteração, mas com acesso total aos menus liberados como Pacientes, Histórico, Navegação, Perfis).
  - **Sem filtro por especialidade**: Visualização ampla de dados e procedimentos de todas as especialidades nos menus acessados.
- **Regras de Seleção e Usuários**:
  - Usuários atribuídos a esse perfil têm por padrão a função de Enfermeiro e visualizam dados gerais sem restrição de filtro de especialidade padrão.

## Capabilities

### New Capabilities
- `epo-generalista-profile`: Define as regras do novo perfil EPO GENERALISTA, posição na ordenação de perfis, cor de destaque (laranja), comportamento de enfermeiro e ausência de restrição por especialidade.

### Modified Capabilities

## Impact

- `src/models/profile.py` e `src/routers/perfil.py`: Atualização do seed/cadastro de perfis padrão e ordenação.
- `frontend/src/stores/perfis.ts`: Atualização das listas de perfis, tipo `EPO_GENERALISTA`, cor da badge (laranja) e ordenação (Abaixo de Gestão LEC, acima de Especialidades).
- `frontend/src/views/Pacientes.vue`, `NavegacaoLec.vue`, `InteracoesLec.vue`: Tratamento para `EPO_GENERALISTA` não aplicar filtro automático de especialidade ao carregar.
