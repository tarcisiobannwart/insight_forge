# TASK-DG-01: Implementar Sistema de Templates

## Descrição
Desenvolver um sistema de templates flexível para o DocGenerator, permitindo personalização da documentação gerada. Isso incluirá a migração do código atual para usar templates Jinja2, criação de templates padrão para diferentes componentes, e mecanismos para permitir que usuários customizem os templates.

## Detalhes
- **Prioridade**: Alta
- **Estimativa**: 3 dias
- **Épico**: [EP-002](../epics/EP-002_documentation_generation.md)
- **Responsável**: Não atribuído
- **Status**: Pendente

## Requisitos

### Funcionais
- O sistema deve usar templates Jinja2 para geração de documentação
- Deve haver templates padrão para classes, funções, casos de uso, etc.
- Usuários devem poder customizar templates
- O sistema deve permitir herança de templates
- As alterações em templates devem ser aplicadas a toda documentação gerada

### Técnicos
- Integrar Jinja2 como motor de templates
- Implementar carregamento de templates personalizados
- Manter compatibilidade com a estrutura de dados existente
- Garantir erro claro quando templates inválidos são usados
- Documentar variáveis disponíveis para cada template

## Subtarefas

### 1. Integrar motor de templates Jinja2
- [ ] Adicionar dependência Jinja2 ao requirements.txt
- [ ] Criar sistema de carregamento de templates
- [ ] Implementar ambiente Jinja2 configurado
- [ ] Adicionar funções auxiliares para formatação Markdown
- [ ] Criar mecanismo de cache para templates compilados

### 2. Criar templates para diferentes componentes
- [ ] Template para documentação de classes
- [ ] Template para documentação de funções
- [ ] Template para casos de uso
- [ ] Template para user stories
- [ ] Template para regras de negócio
- [ ] Template para índice e navegação

### 3. Implementar customização de templates
- [ ] Criar mecanismo para detectar templates personalizados
- [ ] Implementar herança de templates (extend/override)
- [ ] Validar templates carregados
- [ ] Adicionar variáveis de configuração para ajustar templates
- [ ] Implementar fallback para templates padrão quando customizados falham

### 4. Documentar o sistema de templates
- [ ] Criar documentação sobre variáveis disponíveis em cada template
- [ ] Documentar como customizar templates
- [ ] Adicionar exemplos de templates personalizados
- [ ] Documentar funções auxiliares disponíveis nos templates
- [ ] Criar guia de melhores práticas para templates

## Abordagem Técnica

### Estrutura de Templates
Os templates serão organizados por tipo:

```
templates/
├── class.md.j2             # Template para classes
├── function.md.j2          # Template para funções
├── usecase.md.j2           # Template para casos de uso
├── userstory.md.j2         # Template para user stories
├── businessrule.md.j2      # Template para regras de negócio
├── index.md.j2             # Template para índice
└── partials/               # Componentes reutilizáveis
    ├── method.md.j2        # Fragmento para métodos
    ├── parameter.md.j2     # Fragmento para parâmetros
    └── navigation.md.j2    # Fragmento para navegação
```

### Sistema de Carregamento
Implementaremos um carregador que procura templates nesta ordem:
1. Diretório de templates personalizado fornecido pelo usuário
2. Templates padrão do sistema

```python
class TemplateLoader:
    def __init__(self, custom_dir=None):
        self.custom_dir = custom_dir
        self.default_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = jinja2.Environment(
            loader=jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(self.custom_dir) if self.custom_dir else jinja2.DictLoader({}),
                jinja2.FileSystemLoader(self.default_dir),
            ]),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters["markdown_escape"] = self._markdown_escape
        
    def get_template(self, name):
        """Get a template by name."""
        try:
            return self.env.get_template(name)
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(f"Template '{name}' not found")
```

### Exemplo de Template
Um template para classes poderia ser:

```jinja
# Class: {{ class.name }}

{% if class.docstring %}
{{ class.docstring }}
{% endif %}

## Source
- **File**: `{{ class.file_path }}`
- **Line**: {{ class.line_number }}

{% if class.base_classes %}
## Inheritance
{% for base in class.base_classes %}
- {{ base }}{% endfor %}
{% endif %}

{% if class.methods %}
## Methods
{% for method in class.methods %}
### `{{ method.name }}({% for param in method.parameters %}{{ param }}{% if not loop.last %}, {% endif %}{% endfor %})`

{% if method.docstring %}
{{ method.docstring }}
{% endif %}

- **Line**: {{ method.line_number }}
{% endfor %}
{% endif %}
```

### Personalização de Templates
Usuários poderão personalizar templates de duas formas:
1. Criando templates completos que substituem os padrão
2. Estendendo templates padrão e sobrescrevendo blocos específicos

```jinja
{% extends "class.md.j2" %}

{% block class_header %}
# {{ class.name }} (Custom Format)
{% endblock %}

{% block methods %}
## Class Methods
{% for method in class.methods %}
- {{ method.name }}
{% endfor %}
{% endblock %}
```

## Critérios de Aceitação
- ✅ Todos os geradores de documentação usam templates Jinja2
- ✅ Templates existem para todos os tipos de componentes
- ✅ Usuários podem fornecer templates personalizados
- ✅ A documentação gerada é consistente com o formato esperado
- ✅ Erros em templates são reportados claramente
- ✅ A documentação do sistema de templates está completa
- ✅ Templates padrão produzem resultado igual ou melhor que o sistema atual

## Impacto
A implementação do sistema de templates proporcionará:
1. Maior flexibilidade na formatação da documentação gerada
2. Possibilidade de adaptar a documentação para necessidades específicas
3. Melhor separação entre lógica e apresentação
4. Base para futuros aprimoramentos na geração de documentação

## Riscos
- Templates muito complexos podem ser difíceis de manter
- Personalização excessiva pode resultar em documentação inconsistente
- Performance pode ser impactada se muitos templates forem carregados

## Referências
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Template Method Pattern](https://refactoring.guru/design-patterns/template-method)
- [Markdown Syntax Guide](https://www.markdownguide.org/basic-syntax/)