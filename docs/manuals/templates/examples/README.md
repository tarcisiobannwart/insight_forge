# Exemplos de Templates Personalizados

Este diretório contém exemplos de templates personalizados para o sistema de documentação do InsightForge. Estes templates demonstram como você pode personalizar a aparência e o conteúdo da documentação gerada.

## Arquivos Incluídos

- `custom_class_template.md.j2` - Template personalizado para documentação de classes
- `custom_rule_template.md.j2` - Template personalizado para documentação de regras de negócio

## Como Usar

Para usar estes templates personalizados:

1. Crie um diretório para seus templates personalizados:
```bash
mkdir -p meus_templates
```

2. Copie os templates de exemplo que deseja usar:
```bash
cp docs/manuals/templates/examples/custom_class_template.md.j2 meus_templates/class.md.j2
cp docs/manuals/templates/examples/custom_rule_template.md.j2 meus_templates/businessrule.md.j2
```

3. Inicialize o DocGenerator com seu diretório de templates:
```python
from insightforge.reverse_engineering.doc_generator import DocGenerator

doc_generator = DocGenerator(
    "/caminho/para/saida",
    custom_templates_dir="meus_templates"
)

# Gerar documentação
doc_generator.generate(parsed_data)
```

## Personalizando Templates

Sinta-se à vontade para modificar estes templates para atender às suas necessidades específicas. Consulte a documentação completa do sistema de templates para mais informações:

- [Visão Geral do Sistema de Templates](../overview.md)
- [Guia de Customização](../customization.md)
- [Referência de Variáveis](../variables-reference.md)

## Exemplos de Saída

### Template de Classe Personalizado

O template `custom_class_template.md.j2` produz documentação com:

- Badge no topo
- Tabela de resumo dos métodos
- Detalhes dos métodos em formato expandido
- Diagrama Mermaid para mostrar a hierarquia de herança
- Rodapé personalizado

### Template de Regra de Negócio Personalizado

O template `custom_rule_template.md.j2` produz documentação com:

- Destaque visual para regras críticas ou de alta prioridade
- Formatação condicional baseada no tipo de regra
- Tabela de metadados
- Pseudocódigo representando a implementação da regra
- Links para regras relacionadas