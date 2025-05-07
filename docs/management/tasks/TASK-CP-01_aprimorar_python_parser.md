# TASK-CP-01: Aprimorar PythonAstParser

## Descrição
Ampliar as capacidades do analisador de código Python para detectar relações entre classes, melhorar a extração de docstrings e detectar atributos. Esta tarefa é fundamental para criar uma representação mais completa e precisa do código analisado.

## Detalhes
- **Prioridade**: Alta
- **Estimativa**: 5 dias
- **Épico**: [EP-001](../epics/EP-001_code_analysis.md)
- **Issue**: [ISSUE-001](../issues/ISSUE-001_class_inheritance.md)
- **Responsável**: Não atribuído
- **Status**: Pendente

## Requisitos

### Funcionais
- O parser deve detectar relações de herança entre classes
- O parser deve identificar todos os atributos de classe e instância
- O parser deve extrair informações completas de docstrings
- As relações entre classes devem ser representadas visualmente

### Técnicos
- Compatibilidade com Python 3.6+
- Processo de análise deve ser não-destrutivo
- Performance deve ser mantida mesmo para projetos grandes
- O código deve ter cobertura de testes de pelo menos 90%

## Subtarefas

### 1. Implementar detecção de herança
- [ ] Modificar a classe `CodeClass` para armazenar classes base
- [ ] Atualizar `_process_class()` para extrair informações de herança
- [ ] Implementar verificação de herança múltipla
- [ ] Atualizar método `to_dict()` para incluir informações de herança
- [ ] Adicionar testes unitários para detecção de herança

### 2. Implementar detecção de dependências entre módulos
- [ ] Analisar statements `import` e `from...import`
- [ ] Criar estrutura para armazenar dependências entre módulos
- [ ] Detectar importações internas vs externas
- [ ] Construir grafo de dependências do projeto
- [ ] Adicionar visualização do grafo de dependências

### 3. Melhorar detecção de docstrings
- [ ] Aprimorar extração de docstrings em formatos diversos (Google, NumPy, reST)
- [ ] Implementar parser de parâmetros em docstrings
- [ ] Detectar seções em docstrings (Parameters, Returns, Examples, etc.)
- [ ] Extrair exemplos de código de docstrings
- [ ] Detectar tipos de retorno e parâmetros em docstrings

### 4. Adicionar detecção de atributos de classes
- [ ] Detectar atributos definidos no `__init__`
- [ ] Identificar propriedades (usando decorador `@property`)
- [ ] Detectar atributos de classe vs instância
- [ ] Associar tipos aos atributos (quando disponíveis)
- [ ] Incluir atributos na documentação das classes

## Abordagem Técnica

### Detecção de Herança
Para detectar herança em Python, precisamos analisar a definição de classe no AST:

```python
class ChildClass(ParentClass1, ParentClass2):
    # implementação
```

No AST, isso é representado como um nó `ClassDef` com um atributo `bases` que contém as classes pai. Podemos extrair essa informação e armazená-la na nossa estrutura `CodeClass`.

### Parser de Docstrings
Para melhorar a extração de docstrings, vamos usar uma abordagem em duas etapas:
1. Extrair a docstring bruta usando `ast.get_docstring()`
2. Analisar a estrutura da docstring para identificar seções como parâmetros, retornos, exemplos, etc.

Suportaremos diferentes formatos de docstring:
- Google style
- NumPy style
- reStructuredText style

### Detecção de Atributos
Para detectar atributos de classe, vamos:
1. Analisar atribuições diretamente no corpo da classe (atributos de classe)
2. Analisar o método `__init__` para extrair atribuições a `self.attribute` (atributos de instância)
3. Identificar propriedades usando decoradores `@property`

## Critérios de Aceitação
- ✅ O parser identifica corretamente todas as classes base (incluindo herança múltipla)
- ✅ Atributos de classe e instância são detectados e documentados
- ✅ Docstrings são analisadas corretamente, extraindo parâmetros, retornos e exemplos
- ✅ Dependências entre módulos são identificadas e visualizadas
- ✅ Todos os testes unitários passam com cobertura > 90%
- ✅ A performance é mantida dentro de limites aceitáveis (analisar um projeto de 1000 arquivos em < 2 minutos)

## Impacto
A implementação dessa tarefa melhorará significativamente a qualidade da documentação gerada, especialmente para projetos com arquitetura orientada a objetos complexa. A detecção de relações entre classes permitirá a geração de diagramas de classe mais completos e úteis.

## Riscos
- Herança complexa (mixins, metaclasses) pode ser difícil de representar
- Performance pode ser impactada em projetos muito grandes
- Diferentes estilos de código podem requerer lógica especial

## Referências
- [AST Module Documentation](https://docs.python.org/3/library/ast.html)
- [PEP 257 -- Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)