# Matriz de Rastreabilidade - InsightForge

Esta matriz mapeia as relações entre casos de uso, user stories, épicos, issues e componentes de código, permitindo rastreabilidade bidirecional completa.

## UC → US → EP (Casos de Uso → User Stories → Épicos)

| Caso de Uso | User Stories | Épicos |
|-------------|--------------|--------|
| [UC-001](../usecases/UC-001_code_analysis.md) | [US-001](../userstories/US-001_python_code_analysis.md) | [EP-001](../epics/EP-001_code_analysis.md) |
| [UC-002](../usecases/UC-002_documentation_generation.md) | [US-002](../userstories/US-002_markdown_documentation.md) | [EP-002](../epics/EP-002_documentation_generation.md) |
| [UC-003](../usecases/UC-003_usecase_extraction.md) | [US-003](../userstories/US-003_usecase_extraction.md), [US-004](../userstories/US-004_backlog_generation.md) | [EP-003](../epics/EP-003_requirements_extraction.md) |
| UC-004 (a ser implementado) | [US-005](../userstories/US-005_llm_integration.md) | [EP-004](../epics/EP-004_llm_integration.md) |

## EP → ISSUE (Épicos → Issues)

| Épico | Issues |
|-------|--------|
| [EP-001](../epics/EP-001_code_analysis.md) | [ISSUE-001](../issues/ISSUE-001_class_inheritance.md), [ISSUE-004](../issues/ISSUE-004_unit_tests.md) |
| [EP-002](../epics/EP-002_documentation_generation.md) | [ISSUE-003](../issues/ISSUE-003_mermaid_diagrams.md), [ISSUE-004](../issues/ISSUE-004_unit_tests.md) |
| [EP-003](../epics/EP-003_requirements_extraction.md) | [ISSUE-002](../issues/ISSUE-002_business_rules_extractor.md), [ISSUE-004](../issues/ISSUE-004_unit_tests.md) |
| [EP-004](../epics/EP-004_llm_integration.md) | (sem issues ativas no momento) |

## US → Componentes (User Stories → Componentes de Código)

| User Story | Componentes |
|------------|-------------|
| [US-001](../userstories/US-001_python_code_analysis.md) | `CodeParser`, `PythonAstParser` |
| [US-002](../userstories/US-002_markdown_documentation.md) | `DocGenerator` |
| [US-003](../userstories/US-003_usecase_extraction.md) | `UseCaseExtractor` |
| [US-004](../userstories/US-004_backlog_generation.md) | `BacklogBuilder`, `UserStory`, `Epic` |
| [US-005](../userstories/US-005_llm_integration.md) | (ainda não implementado) |

## ISSUE → Arquivos (Issues → Arquivos de Código)

| Issue | Arquivos |
|-------|----------|
| [ISSUE-001](../issues/ISSUE-001_class_inheritance.md) | `insightforge/reverse_engineering/code_parser.py` |
| [ISSUE-002](../issues/ISSUE-002_business_rules_extractor.md) | `insightforge/reverse_engineering/business_rules.py` (a ser criado) |
| [ISSUE-003](../issues/ISSUE-003_mermaid_diagrams.md) | `insightforge/reverse_engineering/doc_generator.py` |
| [ISSUE-004](../issues/ISSUE-004_unit_tests.md) | `insightforge/tests/*` |

## BR → US (Regras de Negócio → User Stories)

| Regra de Negócio | User Stories |
|------------------|--------------|
| BR-001: Toda classe deve ter seus métodos associados | [US-001](../userstories/US-001_python_code_analysis.md) |
| BR-002: Docstrings devem ser preservadas na análise | [US-001](../userstories/US-001_python_code_analysis.md), [US-002](../userstories/US-002_markdown_documentation.md) |
| BR-003: Parâmetros de métodos devem excluir 'self' | [US-001](../userstories/US-001_python_code_analysis.md) |
| BR-004: A documentação deve seguir templates pré-definidos | [US-002](../userstories/US-002_markdown_documentation.md) |
| BR-005: A estrutura de diretórios deve ser mantida consistente | [US-002](../userstories/US-002_markdown_documentation.md) |
| BR-006: Docstrings devem ser convertidas para Markdown | [US-002](../userstories/US-002_markdown_documentation.md) |
| BR-007: Casos de uso devem ter IDs únicos | [US-003](../userstories/US-003_usecase_extraction.md) |
| BR-008: Casos de uso devem ser rastreáveis ao código-fonte | [US-003](../userstories/US-003_usecase_extraction.md) |
| BR-009: Comentários com padrões específicos têm prioridade na extração | [US-003](../userstories/US-003_usecase_extraction.md) |

## Métricas de Rastreabilidade

| Métrica | Valor |
|---------|-------|
| Casos de Uso | 4 |
| User Stories | 5 |
| Épicos | 4 |
| Issues Ativas | 4 |
| Regras de Negócio | 9 |
| Componentes | 5 |
| Cobertura de Rastreabilidade | 100% |

*Última atualização: 2025-05-02*