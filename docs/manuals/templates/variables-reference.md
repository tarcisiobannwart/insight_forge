# Referência de Variáveis para Templates

Este documento fornece uma referência completa de todas as variáveis disponíveis em cada tipo de template do sistema de documentação do InsightForge.

## Contexto Geral

Variáveis disponíveis em todos os templates:

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `project_name` | string | Nome do projeto (quando fornecido) |
| `project_description` | string | Descrição do projeto (quando fornecida) |

## Templates de Classe (`class.md.j2`)

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `class.name` | string | Nome da classe |
| `class.docstring` | string | Documentação da classe (pode estar em formato Markdown) |
| `class.file_path` | string | Caminho do arquivo onde a classe é definida |
| `class.line_number` | int | Número da linha onde a classe é definida |
| `class.base_classes` | lista | Lista de classes base (herança) |
| `class.methods` | lista | Lista de objetos de método (veja abaixo) |
| `class.attributes` | lista | Lista de objetos de atributo (veja abaixo) |
| `class.module` | string | Nome do módulo onde a classe é definida |

### Objetos de Método

Cada item em `class.methods` contém:

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `method.name` | string | Nome do método |
| `method.docstring` | string | Documentação do método |
| `method.line_number` | int | Número da linha onde o método é definido |
| `method.parameters` | lista | Lista de nomes dos parâmetros |
| `method.parameter_types` | dict | Dicionário de tipos de parâmetros (`{param_name: tipo}`) |
| `method.parameter_docs` | dict | Dicionário de documentação dos parâmetros (`{param_name: doc}`) |
| `method.return_type` | string | Tipo de retorno do método |
| `method.is_static` | bool | `True` se o método for estático |
| `method.is_class_method` | bool | `True` se for um método de classe |
| `method.is_abstract` | bool | `True` se for um método abstrato |
| `method.decorators` | lista | Lista de decoradores aplicados ao método |

### Objetos de Atributo

Cada item em `class.attributes` contém:

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `attr.name` | string | Nome do atributo |
| `attr.type` | string | Tipo do atributo (se disponível) |
| `attr.docstring` | string | Documentação do atributo (se disponível) |
| `attr.default_value` | string | Valor padrão (se disponível) |
| `attr.is_property` | bool | `True` se for uma property |
| `attr.is_class_var` | bool | `True` se for uma variável de classe |

## Templates de Função (`function.md.j2`)

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `function.name` | string | Nome da função |
| `function.docstring` | string | Documentação da função |
| `function.file_path` | string | Caminho do arquivo onde a função é definida |
| `function.line_number` | int | Número da linha onde a função é definida |
| `function.parameters` | lista | Lista de nomes de parâmetros |
| `function.parameter_types` | dict | Dicionário de tipos de parâmetros (`{param_name: tipo}`) |
| `function.parameter_docs` | dict | Dicionário de documentação dos parâmetros (`{param_name: doc}`) |
| `function.return_type` | string | Tipo de retorno da função |
| `function.module` | string | Nome do módulo onde a função é definida |
| `function.decorators` | lista | Lista de decoradores aplicados à função |

## Templates de Regra de Negócio (`businessrule.md.j2`)

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `rule.id` | string | ID da regra de negócio (ex: BR-001) |
| `rule.name` | string | Nome da regra |
| `rule.description` | string | Descrição detalhada da regra |
| `rule.file_path` | string | Caminho do arquivo onde a regra é encontrada |
| `rule.line_number` | int | Número da linha onde a regra é encontrada |
| `rule.type` | string | Tipo da regra (validação, cálculo, processo, etc.) |
| `rule.severity` | string | Severidade (crítica, alta, média, baixa) |
| `rule.source` | string | Origem da regra (código, comentário, docstring) |
| `rule.code_component` | string | Componente de código relacionado |
| `rule.related_rules` | lista | Lista de IDs de regras relacionadas |

## Templates de Caso de Uso (`usecase.md.j2`)

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `usecase.id` | string | ID do caso de uso (ex: UC-001) |
| `usecase.name` | string | Nome do caso de uso |
| `usecase.description` | string | Descrição detalhada do caso de uso |
| `usecase.actors` | lista | Lista de atores envolvidos |
| `usecase.preconditions` | lista | Lista de pré-condições |
| `usecase.main_flow` | lista | Lista de passos do fluxo principal |
| `usecase.alternate_flows` | lista | Lista de fluxos alternativos |
| `usecase.postconditions` | lista | Lista de pós-condições |
| `usecase.related_usecases` | lista | Lista de casos de uso relacionados |

### Objetos de Fluxo Alternativo

Cada item em `usecase.alternate_flows` contém:

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `flow.name` | string | Nome do fluxo alternativo |
| `flow.steps` | lista | Lista de passos do fluxo alternativo |
| `flow.condition` | string | Condição que aciona o fluxo alternativo |

## Templates de User Story (`userstory.md.j2`)

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `story.id` | string | ID da user story (ex: US-001) |
| `story.name` | string | Nome da user story |
| `story.role` | string | Papel do usuário ("Como um...") |
| `story.goal` | string | Objetivo do usuário ("Eu quero...") |
| `story.benefit` | string | Benefício para o usuário ("Para que...") |
| `story.acceptance_criteria` | lista | Lista de critérios de aceitação |
| `story.related_usecases` | lista | Lista de casos de uso relacionados |
| `story.implemented_by` | lista | Lista de componentes que implementam a user story |

## Templates de Visão Geral (`overview.md.j2`)

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `classes` | lista | Lista de classes do projeto |
| `functions` | lista | Lista de funções do projeto |
| `business_rules` | lista | Lista de regras de negócio do projeto |
| `usecases` | lista | Lista de casos de uso do projeto |
| `userstories` | lista | Lista de user stories do projeto |

## Templates de Índice (`index.md.j2`)

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `project_name` | string | Nome do projeto |
| `project_description` | string | Descrição do projeto |
| `classes` | lista | Lista de classes do projeto |
| `functions` | lista | Lista de funções do projeto |
| `business_rules` | lista | Lista de regras de negócio do projeto |
| `usecases` | lista | Lista de casos de uso do projeto |
| `userstories` | lista | Lista de user stories do projeto |

## Filtros e Funções Disponíveis

### Filtros Personalizados

| Filtro | Descrição | Exemplo |
|--------|-----------|---------|
| `markdown_escape` | Escapa caracteres especiais do Markdown | `{{ text\|markdown_escape }}` |
| `pluralize` | Pluraliza uma palavra com base na contagem | `{{ count }} {{ "item"\|pluralize(count) }}` |
| `format_code` | Formata texto como bloco de código Markdown | `{{ code\|format_code("python") }}` |
| `titleize` | Converte texto para title case preservando acrônimos | `{{ "api documentation"\|titleize }}` |

### Funções Globais

| Função | Descrição | Exemplo |
|--------|-----------|---------|
| `include_file` | Inclui o conteúdo de um arquivo | `{{ include_file("/caminho/para/arquivo.txt") }}` |

### Funções Padrão do Jinja2

Todos os [filtros](https://jinja.palletsprojects.com/en/3.1.x/templates/#list-of-builtin-filters) e [funções](https://jinja.palletsprojects.com/en/3.1.x/templates/#list-of-global-functions) padrão do Jinja2 também estão disponíveis.

## Exemplos

### Exemplo: Acessando Métodos em um Template de Classe

```jinja
# Classe: {{ class.name }}

{% if class.docstring %}
{{ class.docstring }}
{% endif %}

## Métodos

{% for method in class.methods %}
### `{{ method.name }}({% for param in method.parameters %}{{ param }}{% if not loop.last %}, {% endif %}{% endfor %})`

{% if method.docstring %}
{{ method.docstring }}
{% endif %}

{% if method.is_static %}
*Este é um método estático.*
{% endif %}

{% if method.return_type %}
**Retorna**: {{ method.return_type }}
{% endif %}
{% endfor %}
```

### Exemplo: Formatação de Parâmetros de Função

```jinja
# Função: `{{ function.name }}`

{% if function.parameters %}
## Parâmetros:

{% for param in function.parameters %}
- **{{ param }}**{% if function.parameter_types and function.parameter_types[param] %} ({{ function.parameter_types[param] }}){% endif %}{% if function.parameter_docs and function.parameter_docs[param] %}: {{ function.parameter_docs[param] }}{% endif %}
{% endfor %}
{% endif %}
```

### Exemplo: Regra de Negócio com Formatação Condicional

```jinja
# {{ rule.id }} - {{ rule.name }}

{{ rule.description }}

{% if rule.severity == "critical" %}
⚠️ **Esta é uma regra crítica!**
{% endif %}

**Tipo**: {{ rule.type }}
**Severidade**: {{ rule.severity }}
**Fonte**: {{ rule.source }}
```

### Exemplo: Uso de Filtros Personalizados

```jinja
# User Story: {{ story.id }}

Como um {{ story.role|titleize }},
Eu quero {{ story.goal|markdown_escape }},
Para que {{ story.benefit|markdown_escape }}.

{% if story.acceptance_criteria %}
## Critérios de Aceitação ({{ story.acceptance_criteria|length }} {{ "item"|pluralize(story.acceptance_criteria|length) }})

{% for criteria in story.acceptance_criteria %}
- {{ criteria }}
{% endfor %}
{% endif %}
```