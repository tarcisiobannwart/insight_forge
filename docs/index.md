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

## Documentação

A documentação está organizada nas seguintes seções principais:

### [Documentação Técnica](technical/README.md)
- [Arquitetura do Sistema](technical/architecture/system_architecture.md)
- [Implementação](technical/implementation/LLM_Integration_implementation.md)
- [API de Referência](technical/api/index.md)
- [Diagramas](technical/diagrams/index.md)
- [Integrações](technical/integration/llm_api_integration.md)

### [Documentação de Negócio](business/README.md)
- [Casos de Uso](business/usecases/UC-001_code_analysis.md)
- [Issues](business/issues/ISSUE-001_class_inheritance.md)
- [Rastreabilidade](business/traceability/traceability_matrix.md)

### [Documentação de Gerenciamento](management/README.md)
- [Planejamento de Sprint](management/planning/sprint_planning.md)
- [Roadmap](management/planning/roadmap.md)
- [Épicos](management/epics/EP-001_code_analysis.md)
- [Histórias de Usuário](management/userstories/US-001_python_code_analysis.md)

### [Manuais](manuals/user_guide.md)
- [Guia do Usuário](manuals/user_guide.md)
- [Configuração](manuals/configuration.md)
- [Templates](manuals/templates/overview.md)
- [LLM Features](manuals/llm_features.md)

## Estrutura do Projeto

O projeto é organizado nos seguintes módulos:

- **parsers**: Analisadores de código para diferentes linguagens
- **reverse_engineering**: Ferramentas para engenharia reversa de código
- **llm**: Integração com modelos de linguagem
- **exporters**: Exportadores para diferentes formatos de documentação

## Como Contribuir

Para contribuir com o projeto, consulte o [Guia de Contribuição](guidelines/contributing.md).