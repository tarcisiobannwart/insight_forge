# InsightForge - Visão Geral Técnica

## Arquitetura

O InsightForge é construído usando uma arquitetura modular baseada em componentes, onde cada módulo tem uma responsabilidade específica no processo de engenharia reversa. A ferramenta segue o padrão Multi-Component Process (MCP), que coordena a execução dos diferentes módulos.

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Code Analysis │────▶│  Doc Generator│────▶│ UC Extractor  │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Doc Repository│     │ Backlog Builder│    │ LLM Integration│
└───────────────┘     └───────────────┘     └───────────────┘
```

## Fluxo de Processamento

1. **Entrada**: Caminho do projeto a ser analisado (--project)
2. **Análise de Código**: Extração de classes, métodos, funções e suas relações
3. **Geração de Documentação**: Criação de arquivos Markdown estruturados
4. **Extração de Casos de Uso**: Identificação de funcionalidades a partir do código
5. **Construção de Backlog**: Geração de user stories e épicos
6. **Integração com LLM**: Alimentação de modelos de linguagem com o conhecimento extraído

## Componentes Principais

### 1. Code Parser

O `CodeParser` é responsável por analisar o código-fonte e extrair informações estruturais. Suporta Python, PHP e JavaScript/TypeScript, utilizando analisadores específicos para cada linguagem.

**Recursos atuais:**
- Identificação de classes, interfaces, traits, métodos e funções
- Extração de docstrings, PHPDoc, JSDoc e TSDoc
- Detecção de herança e implementação de interfaces
- Suporte para features específicas de cada linguagem
- Armazenamento de informações de localização (arquivo, linha)

**Suporte a linguagens:**
- **Python**: Análise via módulo AST (Abstract Syntax Tree)
- **PHP**: Análise via biblioteca phply (opcional)
- **JavaScript/TypeScript**: Análise via Node.js e @babel/parser (opcional)

### 2. Documentation Generator

O `DocGenerator` transforma os dados estruturais do código em documentação Markdown legível e navegável.

**Recursos atuais:**
- Geração de documentação para classes e funções
- Criação de visão geral do projeto
- Organização em diretórios estruturados

**Limitações atuais:**
- Templates fixos com pouca personalização
- Sem suporte para diagramas
- Sem integração com sistemas de documentação existentes

### 3. Use Case Extractor

O `UseCaseExtractor` identifica casos de uso descritos no código, principalmente via docstrings e comentários.

**Recursos atuais:**
- Identificação de padrões de caso de uso em docstrings
- Associação de casos de uso a componentes do código
- Geração de IDs únicos para casos de uso

**Limitações atuais:**
- Depende fortemente da qualidade dos comentários
- Heurísticas limitadas para inferência de casos de uso
- Sem análise de fluxo para detecção de cenários alternativos

### 4. Backlog Builder

O `BacklogBuilder` gera user stories e épicos a partir dos casos de uso e estrutura do código.

**Recursos atuais:**
- Conversão de casos de uso em user stories
- Geração de estrutura "Como um X, eu quero Y, para que Z"
- Agrupamento básico em épicos

**Limitações atuais:**
- Critérios de aceitação genéricos
- Sem estimativa automática de story points
- Agrupamento simples sem análise de domínio

### 5. LLM Integration (Planejado)

A integração com modelos de linguagem permitirá consultas em linguagem natural sobre o projeto.

**Recursos planejados:**
- Integração com Ollama para processamento local
- Embeddings para pesquisa semântica
- Resposta a perguntas sobre o projeto

## Stack Tecnológica

- **Linguagem Principal**: Python 3.10+
- **Análise de Código**: 
  - Python: ast (biblioteca padrão)
  - PHP: phply (opcional)
  - JavaScript/TypeScript: Node.js e @babel/parser (opcional)
- **Manipulação de Arquivos**: pathlib, glob
- **Interface CLI**: argparse, rich
- **Formatação**: markdown, pyyaml
- **Configuração**: jsonschema para validação
- **Validação de Tipo**: mypy
- **Testes**: pytest

## Exemplo de Uso

```bash
# Análise básica de um projeto
python main.py --project /caminho/do/seu/projeto

# Saída da documentação
/caminho/do/seu/projeto/docs/
  ├── overview/
  ├── classes/
  ├── functions/
  ├── usecases/
  └── userstories/
```