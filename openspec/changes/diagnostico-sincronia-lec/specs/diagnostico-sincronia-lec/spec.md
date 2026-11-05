# Spec Delta

## Purpose

Permite exclusivamente aos perfis Administrador e Gestão LEC gerenciar o histórico de diagnósticos de sincronia entre o Comunicação Cirúrgica e o Sistema LEC, realizar novos diagnósticos via upload de planilhas/ZIP com verificação preliminar de cobertura de especialidades e desduplicação automática, visualizar todas as divergências de fila, de especialidade e de informações (Swalis, médico responsável, lateralidade e judicialização) diretamente na tela, avaliar e corrigir manualmente informações divergentes e executar ações de sincronização no banco do Comunicação Cirúrgica com registro integral no menu Histórico (`origem_menu = "Pacientes"`).

## ADDED Requirements

### Requirement: Acesso restrito aos perfis ADMIN e GESTAO_LEC
O sistema SHALL exibir o botão `"Diagnóstico Comunicação Cirúrgica x Sistema LEC"` no cabeçalho da tela de Pacientes, ao lado de `"Importar Planilha"`, e permitir o acesso aos endpoints de diagnóstico e sincronização exclusivamente para usuários com perfil ativo `ADMIN` ou `GESTAO_LEC`.

#### Scenario: Visualização por perfil autorizado
- **WHEN** um usuário com perfil ativo `ADMIN` ou `GESTAO_LEC` acessa a tela de Pacientes
- **THEN** o botão `"Diagnóstico Comunicação Cirúrgica x Sistema LEC"` é exibido ao lado de `"Importar Planilha"`

#### Scenario: Bloqueio para perfis de especialidade
- **WHEN** um usuário com perfil ativo do tipo `ESPECIALIDADE` acessa a tela de Pacientes ou tenta chamar os endpoints `/api/pacientes/diagnostico-lec`
- **THEN** o botão não é exibido na interface e o backend rejeita qualquer chamada com `403 Forbidden`

### Requirement: Lista de diagnósticos realizados e opção de novo diagnóstico
O sistema SHALL abrir, ao clicar em `"Diagnóstico Comunicação Cirúrgica x Sistema LEC"`, a lista histórica de diagnósticos já realizados ordenada da data/hora mais recente para a mais antiga, acompanhada do botão `"Novo Diagnóstico"`.

#### Scenario: Abertura da lista de diagnósticos realizados
- **WHEN** o usuário autorizado clica em `"Diagnóstico Comunicação Cirúrgica x Sistema LEC"`
- **THEN** o modal exibe a lista de diagnósticos anteriores em ordem decrescente de data/hora e o botão `"Novo Diagnóstico"`

#### Scenario: Execução de ações por múltiplos usuários no mesmo diagnóstico armazenado
- **WHEN** diferentes usuários autorizados abrem um diagnóstico armazenado e executam ações em itens distintos
- **THEN** o sistema registra em cada item sincronizado e no menu Histórico o nome/username do usuário específico que executou aquela ação

### Requirement: Upload flexível, desduplicação e relatório preliminar de cobertura de especialidades
O sistema SHALL aceitar o envio de um ou mais arquivos `.xlsx`/`.xls` ou `.zip`, desduplicar arquivos repetidos da mesma especialidade e apresentar um painel preliminar indicando quais especialidades cadastradas no Comunicação Cirúrgica tiveram planilha importada e quais não tiveram.

#### Scenario: Envio de arquivo ZIP com planilhas duplicadas e verificação de cobertura
- **WHEN** o usuário envia um pacote `.zip` ou múltiplas planilhas `.xlsx`
- **THEN** o sistema consolida automaticamente arquivos duplicados da mesma especialidade e exibe quais especialidades do CC tiveram planilha importada, quais ficaram sem planilha e quais existem apenas no Sistema LEC

### Requirement: Classificação separada de divergência de especialidade e de divergências cadastrais/clínicas
O sistema SHALL manter em categoria separada os pacientes que estão em outra especialidade no Comunicação Cirúrgica (`EM_OUTRA_ESPECIALIDADE_NO_CC`) e classificar em categoria específica (`DIVERGENCIA_DADOS_CADASTRAIS`) os pacientes presentes em ambos os sistemas na mesma especialidade cujas informações de Swalis, médico responsável, lateralidade ou judicialização divirjam entre o Comunicação Cirúrgica e o Sistema LEC.

#### Scenario: Paciente em especialidade diferente entre CC e Sistema LEC
- **WHEN** um prontuário consta na planilha do Sistema LEC em uma especialidade (ex.: `BARIÁTRICA`) e está ativo no Comunicação Cirúrgica em outra especialidade (ex.: `GERAL`)
- **THEN** o sistema classifica o registro na aba separada `EM_OUTRA_ESPECIALIDADE_NO_CC` e disponibiliza a ação de mudança de especialidade no CC

#### Scenario: Paciente ativo em ambos os sistemas com divergência em Swalis, médico responsável, lateralidade ou judicialização
- **WHEN** um prontuário está ativo na mesma especialidade em ambos os sistemas, mas apresenta valor diferente em Swalis, médico responsável, lateralidade ou judicialização
- **THEN** o sistema classifica o registro em `DIVERGENCIA_DADOS_CADASTRAIS`, exibindo lado a lado o valor que consta no Comunicação Cirúrgica e o valor que consta no Sistema LEC para cada campo divergente

#### Scenario: Avaliação individual e correção manual de informações divergentes pelo usuário Gestão LEC
- **WHEN** o usuário visualiza um registro na aba de divergência de informações (`DIVERGENCIA_DADOS_CADASTRAIS`) e aciona a opção individual de avaliar/corrigir
- **THEN** o sistema abre a edição individual permitindo ao usuário escolher/editar manualmente os valores de Swalis, médico responsável, lateralidade e judicialização a serem gravados no Comunicação Cirúrgica (sem ação automática em lote)

### Requirement: Ações de inclusão, exclusão e edição no CC com registro obrigatório no menu Histórico
O sistema SHALL executar todas as ações decorrentes do diagnóstico (`Incluir no CC`, `Excluir do CC`, `Mudar Especialidade no CC` e `Corrigir Informações no CC`) exclusivamente no banco do Comunicação Cirúrgica e registrar cada ação no menu `Histórico` com `origem_menu = "Pacientes"`, identificando o usuário executor e detalhando a alteração.

#### Scenario: Ação Excluir do CC para pacientes que saíram do Sistema LEC
- **WHEN** o usuário seleciona um ou mais pacientes ativos apenas no CC e aciona `"Excluir do CC"`
- **THEN** o sistema registra uma solicitação `EXCLUIR` aprovada com `origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`, o usuário que executou a ação e detalhes explicando a exclusão via Diagnóstico CC x Sistema LEC, removendo o paciente da fila ativa de Pacientes

#### Scenario: Mudança de especialidade ou de informações registrada no Histórico como edição do tipo execução
- **WHEN** o usuário executa a mudança de especialidade (`EM_OUTRA_ESPECIALIDADE_NO_CC`) ou a correção manual individual de informações divergentes (`Swalis`, `Médico Responsável`, `Lateralidade` ou `Judicialização`)
- **THEN** o sistema atualiza os dados ativos do paciente no Comunicação Cirúrgica e grava no menu Histórico um registro com `tipo = "EDITAR"`, `evento_tipo = "EXECUCAO"`, `origem_menu = "Pacientes"`, `status = "APROVADO"`, o usuário que executou a ação e a descrição detalhada das mudanças no formato `Campo: valor_anterior -> valor_novo`
