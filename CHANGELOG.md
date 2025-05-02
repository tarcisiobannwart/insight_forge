# Changelog - InsightForge

Todas as mudanças significativas neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.1.0-alpha] - 2025-05-02

### Adicionado

- Estrutura inicial do projeto
- CLI básica com parâmetro `--project`
- Parser para código Python usando AST
- Extração de classes, métodos e funções
- Geração de documentação Markdown básica
- Templates para documentação de referência
- Extrator inicial de casos de uso
- Gerador básico de backlog (user stories e épicos)
- Estrutura para status de execução (mcp_status.json)

### Planejado para Próxima Versão

- Detecção de relações entre classes (herança, composição)
- Geração de diagramas usando Mermaid
- Extrator de regras de negócio
- Suporte a arquivos de configuração
- Testes unitários e de integração
- Documentação de usuário mais completa

## [Backlog] - Recursos Futuros

### Análise de Código

- Suporte para JavaScript/TypeScript
- Suporte para PHP
- Detecção de APIs REST
- Análise de arquivos de configuração (JSON, YAML)
- Análise incremental baseada em git diff

### Geração de Documentação

- Templates personalizáveis
- Diagramas de classe e sequência
- Exportação para outros formatos (HTML, PDF)
- Melhor navegabilidade entre documentos
- Tabelas de rastreabilidade

### Integração

- Cliente Ollama para processamento local
- Embeddings para pesquisa semântica
- Interface de perguntas e respostas
- Integração com Jira/Trello
- Leitor de documentos PDF/DOCX
- Conector para Confluence