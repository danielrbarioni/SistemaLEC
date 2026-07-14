## Context

A tela de Pacientes renderiza a agregação dos dados de pacientes com o histórico de suas solicitações aprovadas para reconstruir seu status atual. O cadastro básico inicial de pacientes obtido do AGHU não contém informações de especialidade e procedimento (pois são dados puramente do prontuário/registro civil). Portanto, injetar um procedimento vazio na inicialização do mapa é um bug herdado do design baseado em arquivos CSV estáticos.

## Goals

- Remover o procedimento em branco inicializado no frontend.
- Garantir que a lista de procedimentos seja populada estritamente pelas solicitações aprovadas.
