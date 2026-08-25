## Why

No formulário de interações da tela "Comunicação LEC" (`InteracoesLec.vue`):
1. A seleção do médico responsável renderiza nomes duplicados no dropdown/datalist (em preto com fonte maior e repetido em cinza com fonte menor).
2. A lista de procedimentos da fila de espera para cada especialidade cirúrgica precisa ser sincronizada diretamente com os procedimentos cadastrados no AGHU para o código da especialidade selecionada (com mapeamento completo dos códigos de especialidades do AGHU identificados nas planilhas e banco de dados).

## What Changes

- **Correção da Duplicidade Visual do Médico Responsável**: Ajustar a tag `<datalist>` para utilizar `<option :value="med" />` sem repetir o texto interno, eliminando o comportamento do navegador de renderizar rótulo duplo (preto + cinza).
- **Mapeamento e Integração de Procedimentos por Especialidade AGHU**:
  - Mapear os códigos de especialidade do AGHU (`seq`) para cada uma das especialidades do Sistema LEC (ex.: Plástica: 1884, Ortopedia: 386 e subespecialidades, Geral: 33, Oncológica: 1847, Urologia: 556, Hemodinâmica: 1270, Vascular: 37, Aparelho Digestivo: 727, Radiologia Intervencionista: 2444, Pediátrica: 1888, Otorrinolaringologia: 392, Ginecologia: 1236/1728, Oftalmologia: 366, Neurocirurgia: 291, Torácica: 1886, Proctologia: 1450, Bucomaxilofacial: 1461, Cabeça e Pescoço: 1242, Cardíaca: 2262, Dermatologia: 1602/1426, Bariátrica: 1652, Mastologia: 1745/284).
  - Puxar procedimentos cirúrgicos ativos via endpoint `/api/especialidades/{id_especialidade}/procedimentos` sob demanda ao selecionar a especialidade na tela de Comunicação LEC e Pacientes, garantindo exibição de nome + ID do procedimento.

## Capabilities

### New Capabilities
- `comunicacao-lec-procedimentos-aghu`: Busca dinâmica e preenchimento de procedimentos cirúrgicos do AGHU associados ao código da especialidade selecionada na tela Comunicação LEC.
- `comunicacao-lec-medico-responsavel-datalist`: Autocomplete limpo e deduplicado do médico responsável sem duplicidade visual no datalist.

### Modified Capabilities
<!-- Nenhuma especificação anterior teve seus requisitos alterados -->

## Impact

- Frontend: `frontend/src/views/InteracoesLec.vue`, `frontend/src/views/Pacientes.vue`, mapeamento centralizado de códigos de especialidade AGHU.
- Backend: Endpoint `/api/especialidades/{id_especialidade}/procedimentos` e queries SQL do AGHU.
