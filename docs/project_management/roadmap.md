# InsightForge - Roadmap de Desenvolvimento

## Visão Geral do Roadmap

Este roadmap descreve o plano de desenvolvimento para o InsightForge, dividido em etapas incrementais com foco em entrega de valor em cada milestone.

## Milestone 1: Fundação (Status: Em andamento)

**Objetivo**: Estabelecer a estrutura básica e primeiras funcionalidades.

- ✅ Estrutura inicial do projeto
- ✅ CLI com parâmetro --project
- ✅ Parser básico para código Python
- ✅ Gerador de documentação Markdown
- ✅ Templates de documentação

## Milestone 2: Core Engine (Próximo)

**Objetivo**: Completar funcionalidades essenciais e refinar a experiência do usuário.

- ⬜ Adicionar suporte para análise de relações entre classes (herança, dependências)
- ⬜ Melhorar a detecção de docstrings e comentários
- ⬜ Implementar caching para análises repetidas
- ⬜ Adicionar comandos CLI para controle granular do processo
- ⬜ Desenvolver extrator de regras de negócio
- ⬜ Melhorar a qualidade da documentação gerada
- ⬜ Implementar testes unitários para componentes principais

## Milestone 3: Expansão de Recursos

**Objetivo**: Ampliar capacidades e suporte para outras linguagens.

- ⬜ Adicionar suporte para JavaScript/TypeScript
- ⬜ Adicionar suporte para PHP
- ⬜ Implementar análise de arquivos de configuração (JSON, YAML)
- ⬜ Adicionar detecção de APIs REST
- ⬜ Gerar documentação de APIs usando OpenAPI
- ⬜ Permitir configuração via arquivo YAML
- ⬜ Implementar análise incremental baseada em git diff

## Milestone 4: Integração com LLM

**Objetivo**: Adicionar inteligência e consultas em linguagem natural.

- ⬜ Implementar cliente Ollama para processamento local
- ⬜ Criar sistema de embeddings para pesquisa semântica
- ⬜ Desenvolver interface de perguntas e respostas
- ⬜ Integrar com Claude/outros LLMs
- ⬜ Implementar recomendações de melhorias de código
- ⬜ Adicionar geração de testes baseada no entendimento do código

## Milestone 5: Integração Externa

**Objetivo**: Conectar com sistemas externos e expandir usabilidade.

- ⬜ Implementar leitor de documentos PDF
- ⬜ Implementar leitor de documentos DOCX
- ⬜ Desenvolver integração com Confluence
- ⬜ Adicionar exportação para Jira/Trello
- ⬜ Implementar visualização web dos resultados
- ⬜ Criar plugins para IDEs populares (VSCode, JetBrains)
- ⬜ Desenvolver API REST para uso como serviço

## Tarefas Pendentes Detalhadas

### Curto Prazo (Milestone 2)

1. **Aprimorar o Code Parser**
   - Implementar detecção de herança entre classes
   - Adicionar identificação de interfaces/classes abstratas
   - Implementar análise de imports para mapear dependências
   - Adicionar detecção de constantes e variáveis globais
   - Corrigir limitações na análise AST para casos complexos

2. **Expandir o Doc Generator**
   - Adicionar suporte para templates personalizáveis
   - Implementar geração de índice de navegação
   - Adicionar links de referência bidirecional entre documentos
   - Implementar formatação avançada para parâmetros e tipos
   - Gerar diagramas simplificados (usando sintaxe mermaid)

3. **Refinar o Use Case Extractor**
   - Melhorar heurísticas para detectar casos de uso implícitos
   - Implementar análise de fluxo para identificação de cenários alternativos
   - Adicionar detecção de pré e pós-condições baseada em verificações no código
   - Implementar agrupamento de casos de uso por domínio

4. **Desenvolver Business Rules Extractor**
   - Criar extrator de regras de negócio a partir de validações no código
   - Implementar detecção de regras em blocos if/else e validações
   - Gerar documentação específica para regras de negócio
   - Mapear regras de negócio para casos de uso

5. **Implementar Sistema de Testes**
   - Desenvolver suite de testes unitários para todos os componentes
   - Adicionar testes de integração para o fluxo completo
   - Implementar mock objects para testes isolados
   - Configurar CI para execução automática de testes

### Médio Prazo (Milestone 3)

1. **Expandir Suporte para Linguagens**
   - Implementar parser para JavaScript/TypeScript
   - Adicionar suporte para análise de PHP
   - Desenvolver detecção de frameworks comuns (React, Laravel, etc.)
   - Unificar representação intermediária para multi-linguagem

2. **Implementar Análise Incremental**
   - Integrar com git para detecção de mudanças
   - Implementar caching de análises prévias
   - Adicionar modo de atualização que processa apenas arquivos modificados
   - Desenvolver sistema de mesclagem de documentação existente com nova

3. **Ampliar Capacidades de API**
   - Adicionar detecção de endpoints REST
   - Implementar geração de documentação OpenAPI
   - Desenvolver análise de contratos de API
   - Adicionar testes de integração para APIs detectadas

### Longo Prazo (Milestones 4-5)

1. **Integração LLM**
   - Desenvolver cliente Ollama para processamento local
   - Implementar sistema de embeddings para pesquisa semântica
   - Criar interface de perguntas e respostas sobre o código
   - Adicionar recomendações de melhoria baseadas em LLM

2. **Integração Externa**
   - Implementar leitores para documentos externos (PDF, DOCX)
   - Desenvolver conector para Confluence
   - Adicionar exportação para sistemas de gestão de projetos
   - Criar visualizador web para navegação na documentação