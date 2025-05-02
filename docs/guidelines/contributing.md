# Guia de Contribuição - InsightForge

Este documento descreve as diretrizes para contribuir com o projeto InsightForge. Por favor, leia atentamente antes de enviar pull requests ou começar o desenvolvimento.

## Princípios de Design

O InsightForge segue estes princípios fundamentais:

1. **Modularidade**: Componentes devem ter responsabilidades bem definidas e interfaces claras
2. **Extensibilidade**: O sistema deve ser facilmente extensível para novas linguagens e formatos
3. **Não-intrusivo**: Análise sem execução de código ou modificação dos projetos analisados
4. **Documentável**: O código deve ser bem documentado, servindo como exemplo do próprio propósito do projeto
5. **Qualidade**: Testes abrangentes e tipagem forte são essenciais

## Fluxo de Trabalho

1. Selecione uma tarefa do arquivo `docs/project_management/development_tasks.md`
2. Crie um branch com o formato `feature/[ID]-descricao-curta` (ex: `feature/T001-deteccao-heranca`)
3. Implemente a funcionalidade com testes apropriados
4. Atualize a documentação relevante
5. Envie um pull request para revisão

## Padrões de Código

### Estilo

Seguimos as convenções PEP 8 com algumas adaptações:

- Comprimento máximo de linha: 100 caracteres
- Indentação: 4 espaços (sem tabs)
- Docstrings: Formato Google style

### Tipagem

- Uso obrigatório de type hints para todos os parâmetros e retornos
- Código deve passar no mypy sem erros
- Use `Optional[T]` para parâmetros que podem ser None

### Docstrings

Todas as classes e métodos públicos devem ter docstrings que expliquem:

```python
"""
Breve descrição em uma linha.

Descrição mais detalhada com múltiplas linhas
explicando o propósito e comportamento.

Args:
    param1 (tipo): Descrição do primeiro parâmetro
    param2 (tipo): Descrição do segundo parâmetro

Returns:
    tipo: Descrição do valor de retorno

Raises:
    ExceptionType: Descrição das condições que geram a exceção

Example:
    >>> exemplo_de_uso(param1, param2)
    resultado_esperado
"""
```

### Testes

- Todo código deve ter testes unitários
- Mínimo de 80% de cobertura de código para novos módulos
- Testes devem ser independentes (não depender de outros testes)
- Use fixtures e mocks para isolar testes de dependências externas

## Estrutura do Projeto

```
insightforge/
├── main.py                 # Ponto de entrada CLI
├── reverse_engineering/    # Módulos de análise e geração
│   ├── code_parser.py      # Analisador de código
│   ├── doc_generator.py    # Gerador de documentação
│   ├── usecase_extractor.py # Extrator de casos de uso
│   ├── backlog_builder.py  # Construtor de backlog
│   └── business_rules.py   # Extrator de regras de negócio (planejado)
├── ingestion/              # Módulos de ingestão de docs existentes
├── ollama/                 # Integração com modelos de linguagem
├── tests/                  # Testes unitários e de integração
│   ├── test_code_parser.py
│   ├── test_doc_generator.py
│   └── ...
└── docs/                   # Templates e documentação interna
```

## Processo de Revisão

Pull requests serão revisados considerando:

1. Aderência aos padrões de código
2. Cobertura e qualidade dos testes
3. Qualidade da documentação
4. Manutenibilidade e legibilidade
5. Performance e uso de recursos

## Registro de Alterações

Para cada contribuição, adicione uma entrada ao arquivo CHANGELOG.md no formato:

```
## [Próxima Versão]
### Adicionado
- [ID da Tarefa] Descrição da nova funcionalidade

### Alterado
- [ID da Tarefa] Descrição da alteração

### Corrigido
- [ID da Tarefa] Descrição da correção
```

## Notas para Desenvolvimento

### Dicas para Análise AST

A análise AST (Abstract Syntax Tree) em Python pode ser complexa. Algumas dicas:

- Use `ast.dump(node, annotate_fields=True)` para depuração
- Familiarize-se com a hierarquia de nós em `ast`
- Considere o uso de `astor` para análises mais complexas

### Geração de Documentação

Para gerar documentação consistente:

- Use templates parametrizados em vez de strings literais
- Considere a formatação Markdown durante a geração
- Mantenha links relativos para navegação entre documentos
- Preserve formatação de código em docstrings

### Análise Multi-linguagem

Ao implementar suporte para novas linguagens:

- Mantenha uma representação intermediária comum
- Isole o parsing específico da linguagem em módulos separados
- Reutilize a lógica de geração de documentação
- Documente as peculiaridades de cada linguagem suportada