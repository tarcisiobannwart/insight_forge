# Sistema de Templates InsightForge

## Visão Geral

O sistema de templates do InsightForge é uma implementação flexível baseada em Jinja2 que permite a personalização completa da documentação gerada. Os templates definem a estrutura e o formato dos documentos Markdown gerados para classes, funções, regras de negócio e outros componentes do projeto.

## Principais Recursos

- **Flexibilidade Total**: Qualquer aspecto da documentação gerada pode ser personalizado
- **Templates Padrão**: Um conjunto de templates bem projetados para uso imediato
- **Customização**: Os usuários podem fornecer seus próprios templates personalizados
- **Herança de Templates**: Suporte para estender templates existentes e sobrescrever apenas partes específicas
- **Validação**: Detecção e relatório de erros em templates personalizados
- **Fallback**: Uso automático de templates padrão quando os personalizados falham

## Estrutura de Diretórios

```
templates/
├── class.md.j2             # Template para classes
├── function.md.j2          # Template para funções
├── usecase.md.j2           # Template para casos de uso
├── userstory.md.j2         # Template para user stories
├── businessrule.md.j2      # Template para regras de negócio
├── overview.md.j2          # Template para visão geral
├── index.md.j2             # Template para índice principal
└── partials/               # Componentes reutilizáveis
    ├── method.md.j2        # Fragmento para métodos
    ├── parameter.md.j2     # Fragmento para parâmetros
    ├── navigation.md.j2    # Fragmento para navegação
    └── component_links.md.j2 # Fragmento para links relacionados
```

## Como Usar o Sistema de Templates

### Uso Básico

O sistema de templates é utilizado automaticamente pelo `DocGenerator` quando você gera documentação:

```python
from insightforge.reverse_engineering.doc_generator import DocGenerator

# Inicializar o DocGenerator com o diretório de saída
doc_generator = DocGenerator("/caminho/para/saida")

# Gerar documentação a partir dos dados analisados
doc_generator.generate(parsed_data, project_name="Meu Projeto", project_description="Descrição do projeto")
```

### Fornecendo Templates Personalizados

Você pode fornecer seus próprios templates personalizados:

```python
# Inicializar com um diretório de templates personalizados
doc_generator = DocGenerator(
    "/caminho/para/saida",
    custom_templates_dir="/caminho/para/meus_templates"
)
```

### Criando um Template Personalizado Programaticamente

Você também pode criar ou atualizar templates personalizados programaticamente:

```python
# Exemplo de template personalizado para documentação de classe
custom_template = """
{% block class_header %}
# Classe: {{ class.name }}
{% endblock %}

{% if class.docstring %}
## Sobre esta Classe

{{ class.docstring }}
{% endif %}

## Informações Técnicas

- **Arquivo**: `{{ class.file_path }}`
- **Linha**: {{ class.line_number }}

{% if class.methods %}
## Métodos Disponíveis

{% for method in class.methods %}
### `{{ method.name }}`
{% if method.docstring %}
{{ method.docstring }}
{% endif %}
{% endfor %}
{% endif %}
"""

# Criar ou atualizar um template personalizado
doc_generator.customize_template("class.md.j2", custom_template)
```

## Variáveis Disponíveis nos Templates

Cada tipo de template tem seu próprio conjunto de variáveis disponíveis:

### Em Templates de Classe (`class.md.j2`)

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `class.name` | string | Nome da classe |
| `class.docstring` | string | Documentação da classe |
| `class.file_path` | string | Caminho do arquivo onde a classe é definida |
| `class.line_number` | int | Número da linha onde a classe é definida |
| `class.base_classes` | lista | Lista de classes base (herança) |
| `class.methods` | lista | Lista de métodos da classe |
| `class.attributes` | lista | Lista de atributos da classe |

### Em Templates de Função (`function.md.j2`)

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `function.name` | string | Nome da função |
| `function.docstring` | string | Documentação da função |
| `function.file_path` | string | Caminho do arquivo onde a função é definida |
| `function.line_number` | int | Número da linha onde a função é definida |
| `function.parameters` | lista | Lista de nomes dos parâmetros |
| `function.parameter_types` | dict | Dicionário de tipos de parâmetros |
| `function.parameter_docs` | dict | Dicionário de documentação dos parâmetros |
| `function.return_type` | string | Tipo de retorno da função |

### Em Templates de Regra de Negócio (`businessrule.md.j2`)

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

## Filtros Jinja2 Personalizados

O sistema de templates inclui filtros personalizados para ajudar na formatação:

| Filtro | Descrição | Exemplo |
|--------|-----------|---------|
| `markdown_escape` | Escapa caracteres especiais do Markdown | `{{ text\|markdown_escape }}` |
| `pluralize` | Pluraliza uma palavra com base na contagem | `{{ count }} {{ "item"\|pluralize(count) }}` |
| `format_code` | Formata texto como bloco de código Markdown | `{{ code\|format_code("python") }}` |
| `titleize` | Converte texto para title case preservando acrônimos | `{{ "api documentation"\|titleize }}` |

## Funções Globais

O sistema também fornece funções globais disponíveis em todos os templates:

| Função | Descrição | Exemplo |
|--------|-----------|---------|
| `include_file` | Inclui o conteúdo de um arquivo | `{{ include_file("/caminho/para/arquivo.txt") }}` |

## Estendendo Templates Existentes

Você pode estender templates existentes para personalizar apenas partes específicas:

```jinja
{% extends "class.md.j2" %}

{% block class_header %}
# Classe Customizada: {{ class.name }}
{% endblock %}

{% block class_footer %}
---
Documentação gerada por InsightForge em {% now 'utc', '%Y-%m-%d %H:%M:%S UTC' %}
{% endblock %}
```

## Melhores Práticas

1. **Evite Duplicação**: Use `{% include %}` para componentes reutilizáveis e `{% extends %}` para herança
2. **Use Blocos**: Divida seus templates em blocos para facilitar a personalização
3. **Documente Variáveis**: Adicione comentários sobre as variáveis esperadas no topo do template
4. **Valide**: Teste seus templates com diferentes tipos de dados para garantir robustez
5. **Mantenha a Consistência**: Use um estilo coerente em todos os templates