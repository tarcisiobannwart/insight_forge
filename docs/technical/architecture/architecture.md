---
layout: default
title: Arquitetura do InsightForge
---

# Arquitetura do InsightForge

O InsightForge é construído usando uma arquitetura baseada em componentes que permite a análise e geração de documentação flexível para diferentes linguagens e formatos.

## Visão Geral da Arquitetura

A arquitetura do InsightForge é organizada nos seguintes componentes principais:

```
insightforge/
├── config/                  # Gerenciamento de configuração
├── reverse_engineering/     # Componentes de engenharia reversa
│   ├── code_parser.py       # Parser de código base
│   ├── php_parser.py        # Parser específico para PHP
│   ├── javascript_parser.py # Parser específico para JS/TS
│   ├── relationship_detector.py  # Detector de relacionamentos
│   ├── flow_analyzer.py     # Analisador de fluxo de método
│   ├── diagram_generator.py # Gerador de diagramas
│   ├── doc_generator.py     # Gerador de documentação
│   └── template_system.py   # Sistema de templates
├── llm/                     # Integração com modelos de linguagem
│   ├── base.py              # Classes base para integração LLM
│   ├── ollama.py            # Integração com Ollama
│   ├── embeddings.py        # Sistema de embeddings
│   └── query.py             # Motor de consulta em linguagem natural
├── exporters/               # Exportadores de documentação
│   ├── github_exporter.py   # Exportador para GitHub Pages
│   └── github_integration.py # Integração com GitHub
└── main.py                  # Ponto de entrada da CLI
```

## Fluxo de Processamento

1. **Análise de Código**: Os parsers específicos de linguagem analisam o código-fonte para construir um modelo de dados abstrato.
2. **Detecção de Relacionamentos**: O detector de relacionamentos identifica conexões entre classes e componentes.
3. **Análise de Fluxo**: O analisador de fluxo rastreia chamadas de método para gerar diagramas de sequência.
4. **Geração de Diagramas**: O gerador de diagramas cria representações visuais usando sintaxe Mermaid.
5. **Geração de Documentação**: O gerador de documentação usa o sistema de templates para produzir documentação estruturada.
6. **Exportação**: Os exportadores convertem a documentação para formatos específicos, como GitHub Pages.

## Componentes Principais

### Code Parser

O `CodeParser` é a classe base para todos os parsers de linguagem específicos. Ele coordena a análise de um projeto inteiro, delegando o parsing de arquivos individuais para parsers específicos de linguagem.

### Relationship Detector

O `RelationshipDetector` analisa o código para detectar automaticamente relações como herança, composição, agregação e associação entre classes.

### Flow Analyzer

O `FlowAnalyzer` rastreia chamadas de método para reconstruir fluxos de execução, que são usados para gerar diagramas de sequência.

### Diagram Generator

O `DiagramGenerator` cria diagramas em sintaxe Mermaid, incluindo diagramas de classe, módulo e sequência.

### Doc Generator

O `DocGenerator` usa um sistema de templates baseado em Jinja2 para criar documentação completa a partir do código analisado.

### LLM Integration

O módulo `llm` fornece integração com modelos de linguagem grandes (LLMs) para gerar explicações inteligentes de código e responder a consultas em linguagem natural sobre o código-fonte.

### GitHub Exporter

O `GitHubExporter` transforma a documentação gerada para um formato compatível com GitHub Pages e fornece ferramentas para publicação automática.