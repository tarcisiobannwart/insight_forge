# Customizando Templates no InsightForge

Este guia explica como personalizar os templates do sistema de documentação do InsightForge para atender às suas necessidades específicas.

## Introdução

O sistema de templates do InsightForge permite personalizar completamente a aparência e o conteúdo da documentação gerada. Você pode modificar desde pequenos detalhes até a estrutura completa dos documentos gerados.

## Métodos de Customização

### 1. Fornecendo um Diretório de Templates Personalizados

O método mais simples para personalizar templates é fornecer um diretório contendo seus templates customizados:

```python
from insightforge.reverse_engineering.doc_generator import DocGenerator

# Inicializar o DocGenerator com templates personalizados
doc_generator = DocGenerator(
    output_dir="/caminho/para/saida",
    custom_templates_dir="/caminho/para/meus_templates"
)

# Gerar documentação com os templates personalizados
doc_generator.generate(parsed_data)
```

### 2. Customização Programática

Você também pode criar ou atualizar templates programaticamente:

```python
# Criar ou atualizar um template personalizado
doc_generator.customize_template(
    "class.md.j2",
    "# Classe Personalizada: {{ class.name }}\n\n{{ class.docstring }}"
)
```

## Herança de Templates

Uma técnica poderosa é estender os templates padrão e substituir apenas partes específicas:

```jinja
{% extends "class.md.j2" %}

{% block class_header %}
# Classe Personalizada: {{ class.name }} (v{{ version }})
{% endblock %}

{% block class_footer %}
---
Última modificação: {% now 'utc', '%Y-%m-%d' %}
{% endblock %}
```

### Blocos Disponíveis por Template

#### Template de Classe (`class.md.j2`)

| Bloco | Descrição |
|-------|-----------|
| `class_header` | Cabeçalho da documentação da classe |
| `class_description` | Seção de descrição da classe |
| `class_source` | Informações sobre o arquivo fonte |
| `class_inheritance` | Seção de herança da classe |
| `class_methods` | Lista de métodos da classe |
| `class_attributes` | Lista de atributos da classe |
| `class_footer` | Rodapé da documentação da classe |

#### Template de Função (`function.md.j2`)

| Bloco | Descrição |
|-------|-----------|
| `function_header` | Cabeçalho da documentação da função |
| `function_description` | Seção de descrição da função |
| `function_source` | Informações sobre o arquivo fonte |
| `function_parameters` | Lista de parâmetros da função |
| `function_returns` | Informações sobre o retorno da função |
| `function_footer` | Rodapé da documentação da função |

#### Template de Regra de Negócio (`businessrule.md.j2`)

| Bloco | Descrição |
|-------|-----------|
| `rule_header` | Cabeçalho da documentação da regra |
| `rule_description` | Descrição da regra de negócio |
| `rule_metadata` | Metadados da regra (tipo, severidade, etc.) |
| `rule_implementation` | Informações sobre a implementação |
| `rule_related` | Regras de negócio relacionadas |

## Criando Templates Completamente Novos

Você pode criar templates completamente novos para adicionar tipos de documentação:

1. Crie um novo arquivo `.md.j2` no diretório de templates
2. Implemente a lógica para renderizar o template na classe `TemplateManager`

Por exemplo, para criar um template para diagramas:

```jinja
{# diagram.md.j2#}
# Diagrama: {{ diagram.name }}

{% if diagram.description %}
{{ diagram.description }}
{% endif %}

```mermaid
{{ diagram.content }}
```
```

## Estrutura do Diretório de Templates Personalizados

Para sobrescrever apenas templates específicos, crie um diretório com a mesma estrutura do diretório de templates padrão:

```
meus_templates/
├── class.md.j2             # Template personalizado para classes
└── partials/               # Componentes personalizados
    └── method.md.j2        # Template personalizado para métodos
```

Apenas os arquivos fornecidos serão substituídos; para os demais, serão usados os templates padrão.

## Exemplos de Customização

### Exemplo 1: Adicionar Badges de Status

```jinja
{% extends "class.md.j2" %}

{% block class_header %}
# Classe: {{ class.name }}

{% if class.status == "deprecated" %}
![Deprecated](https://img.shields.io/badge/Status-Deprecated-red)
{% elif class.status == "experimental" %}
![Experimental](https://img.shields.io/badge/Status-Experimental-yellow)
{% elif class.status == "stable" %}
![Stable](https://img.shields.io/badge/Status-Stable-green)
{% endif %}
{% endblock %}
```

### Exemplo 2: Formato Alternativo para Métodos

```jinja
{% extends "partials/method.md.j2" %}

{# Template personalizado que mostra assinatura de método em formato de código #}
### Método: {{ method.name }}

```python
def {{ method.name }}({% for param in method.parameters %}{{ param }}{% if not loop.last %}, {% endif %}{% endfor %}):
    """
    {{ method.docstring|indent(4) }}
    """
    ...
```

{% if method.return_type %}
**Retorna**: {{ method.return_type }}
{% endif %}
```

### Exemplo 3: Adicionando Links para o GitHub

```jinja
{% extends "class.md.j2" %}

{% block class_source %}
## Fonte

- **Arquivo**: [`{{ class.file_path }}`](https://github.com/meu-usuario/meu-repo/blob/main/{{ class.file_path }})
- **Linha**: [{{ class.line_number }}](https://github.com/meu-usuario/meu-repo/blob/main/{{ class.file_path }}#L{{ class.line_number }})
{% endblock %}
```

## Solução de Problemas

### Template Não Encontrado

Se você receber um erro indicando que um template não foi encontrado:

1. Verifique se o arquivo existe no local correto
2. Confirme que o nome do arquivo corresponde exatamente ao esperado
3. Verifique se você está passando o diretório correto para `custom_templates_dir`

### Erro de Variável Indefinida

Se você receber um erro sobre uma variável indefinida:

1. Verifique os dados fornecidos para renderização do template
2. Use verificação condicional com `{% if variavel %}` para evitar erros
3. Forneça valores padrão com `{{ variavel|default('valor padrão') }}`

### Formatação Incorreta

Se a saída não estiver formatada como esperado:

1. Verifique a sintaxe Markdown no template
2. Use `trim_blocks` e `lstrip_blocks` para controlar espaçamento
3. Adicione linhas em branco com `\n\n` quando necessário