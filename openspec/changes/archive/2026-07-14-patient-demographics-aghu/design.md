## Context

A inclusão da data de nascimento e nome da mãe visa aumentar a segurança do paciente na inclusão das listas, reduzindo o risco de homônimos ou erros de identificação.

## Goals / Non-Goals

**Goals:**
- Adicionar campos de Data de Nascimento e Nome da Mãe no formulário.
- Mapear a resposta da API do backend.

**Non-Goals:**
- Armazenar esses campos como colunas persistidas separadas no SQLite se não houver necessidade, exibindo apenas dinamicamente (ou adicionando na tabela SQLite se necessário para listagens). *Nota: Eles já são salvos opcionalmente na tabela Paciente no SQLite.*

## Decisions

- Exibir os campos desabilitados na UI, embaixo dos campos Prontuário e Nome Completo.
