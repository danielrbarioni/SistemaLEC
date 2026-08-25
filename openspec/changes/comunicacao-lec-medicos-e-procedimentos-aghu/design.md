## Context

No menu Comunicação LEC (`frontend/src/views/InteracoesLec.vue`), os usuários realizam solicitações de Inclusão, Edição, Standby e Exclusão na fila cirúrgica. Dois pontos foram levantados:
1. O elemento `<datalist>` do médico responsável possui a estrutura `<option :value="med">{{ med }}</option>`, o que induz os navegadores a desenhar duas linhas para cada item (uma com o valor e outra com o texto interno).
2. O carregamento de procedimentos do AGHU atualmente estava restrito à Plástica (código 1884). Agora, precisa cobrir todas as especialidades cadastradas, mapeando seus respectivos IDs do AGHU (`seq` da tabela `agh.agh_especialidades`) e buscando procedimentos via API `/api/especialidades/{id_especialidade}/procedimentos`.

## Goals / Non-Goals

**Goals:**
- Eliminar a duplicidade visual de médicos no datalist usando a sintaxe auto-fechada `<option :value="med" />`.
- Mapear os códigos de especialidade do AGHU para todas as especialidades do Sistema LEC:
  - `PLÁSTICA`: 1884
  - `ORTOPEDIA`: 386 (e subespecialidades 1974, 1971, 1972, 1616, 1978, 1977)
  - `GERAL`: 33
  - `ONCOLÓGICA`: 1847, 2080, 1466
  - `UROLOGIA`: 556, 1420
  - `HEMODINÂMICA`: 1270
  - `VASCULAR`: 37
  - `APARELHO DIGESTIVO`: 727
  - `RADIOLOGIA INTERVENCIONISTA`: 2444
  - `PEDIÁTRICA`: 1888, 1560
  - `OTORRINOLARINGOLOGIA`: 392, 2450
  - `GINECOLOGIA GERAL`: 1236
  - `GINECOLOGIA ENDOSCÓPICA`: 1728, 1441
  - `OFTALMOLOGIA`: 366, 2052
  - `NEUROCIRURGIA`: 291
  - `TORÁCICA`: 1886
  - `PROCTOLOGIA`: 1450
  - `BUCOMAXILOFACIAL`: 1461
  - `CABEÇA E PESCOÇO`: 1242
  - `CARDÍACA`: 2262
  - `DERMATOLOGIA`: 1602, 1426
  - `BARIÁTRICA`: 1652, 2512
  - `MASTOLOGIA - ESPAÇO TRANS`: 1745, 284
- Implementar cache em memória no frontend para evitar requisições repetidas ao AGHU para a mesma especialidade durante a sessão.

**Non-Goals:**
- Alterar o schema do banco de dados local SQLite ou AGHU.
- Modificar o fluxo de aprovação/rejeição das solicitações.

## Decisions

- **Mapeamento Centralizado no Frontend**: Criar um arquivo auxiliar `frontend/src/utils/especialidadeAghuMap.ts` contendo o mapa de códigos AGHU por especialidade, permitindo reuso entre `InteracoesLec.vue`, `Pacientes.vue` e qualquer tela futura.
- **Suporte a Múltiplos IDs por Especialidade**: Algumas especialidades cirúrgicas possuem sub-códigos no AGHU (ex.: Ortopedia possui 386 e códigos específicos de Coluna, Joelho, Quadril). O helper deve buscar e agregar os procedimentos de todos os IDs associados daquela especialidade e deduplicá-los por descrição/ID.
- **Datalist Fix**: Utilizar `<option :value="med" />` sem children.

## Risks / Trade-offs

- [AGHU PostgreSQL temporariamente inacessível] → O frontend utiliza fallback automático para procedimentos da base local de solicitações e histórico de pacientes sem interromper a interface.
