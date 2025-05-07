# Issue: ISSUE-001 - Implementar Detecção de Herança entre Classes

## Descrição
Atualmente, o `PythonAstParser` detecta classes e métodos, mas não identifica relações de herança entre classes. Esta funcionalidade é essencial para entender a arquitetura orientada a objetos de um projeto.

## Detalhes Técnicos
No Python, a herança é definida na declaração da classe:
```python
class ChildClass(ParentClass):
    # implementação
```

O parser precisa extrair essa informação da AST e armazená-la na estrutura de dados.

## Tarefas
- [ ] Modificar a classe `CodeClass` para incluir um campo para classes pai
- [ ] Atualizar o método `to_dict()` para incluir informações de herança
- [ ] Modificar `PythonAstParser._process_class` para extrair classes base
- [ ] Atualizar `DocGenerator` para mostrar relações de herança na documentação
- [ ] Adicionar testes unitários para verificar a detecção de herança

## Critérios de Aceitação
- O sistema deve identificar corretamente todas as classes base diretas
- A documentação gerada deve mostrar a hierarquia de classes
- Classes sem herança explícita devem ser tratadas como derivadas de `object`
- Herança múltipla deve ser suportada (várias classes base)
- Os testes unitários devem cobrir diferentes cenários de herança

## Prioridade
Alta

## Estimativa
1.5 dias

## Épico Relacionado
[EP-001](../epics/EP-001_code_analysis.md): Análise de Código Eficiente

## Impacto
Esta melhoria permitirá uma compreensão mais profunda da estrutura de projetos orientados a objetos, especialmente para sistemas que fazem uso extensivo de herança e polimorfismo.

## Responsável
Não atribuído

## Status
Pendente