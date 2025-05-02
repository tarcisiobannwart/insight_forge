---
layout: default
title: InsightForge - Documentação
---

# InsightForge - Documentação

InsightForge é uma ferramenta para análise e documentação automática de código-fonte. Ele extrai informações e gera documentação estruturada com diagramas.

## Recursos Principais

- Análise de código de múltiplas linguagens (Python, PHP, JavaScript/TypeScript)
- Geração automática de diagramas (classes, módulos, sequências)
- Integração com LLMs para explicações inteligentes de código
- Detecção automática de relacionamentos entre classes
- Exportação para diversos formatos, incluindo GitHub Pages

## Começando

Para usar o InsightForge, siga estas etapas:

```bash
# Instalar o InsightForge
pip install insightforge

# Analisar um projeto
insightforge analyze --project ./meu-projeto --output-dir ./documentacao
```

## Estrutura do Projeto

O projeto é organizado nos seguintes módulos:

- **parsers**: Analisadores de código para diferentes linguagens
- **reverse_engineering**: Ferramentas para engenharia reversa de código
- **llm**: Integração com modelos de linguagem
- **exporters**: Exportadores para diferentes formatos de documentação

## Mais Informações

- [Guia de Arquitetura](architecture.md)
- [Diagramas](diagrams/index.md)
- [API de Referência](api/index.md)
- [Como Contribuir](contributing.md)