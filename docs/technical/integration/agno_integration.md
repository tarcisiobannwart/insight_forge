# Integração InsightForge com Agno

Esta documentação explica como usar o InsightForge como uma ferramenta para agentes Agno, permitindo a análise de código, geração de documentação e consultas em linguagem natural sobre o código através de agentes IA.

## Visão Geral

A integração do InsightForge com o [Agno](https://github.com/agno-agi/agno) permite que agentes IA possam:

1. Analisar projetos de código-fonte em múltiplas linguagens
2. Gerar documentação técnica com diagramas
3. Responder perguntas em linguagem natural sobre o código

## Pré-requisitos

- InsightForge instalado
- Agno instalado (`pip install agno`)
- Um modelo LLM configurado no Agno (Claude, GPT, etc.)

## Instalação

A integração está incluída no pacote InsightForge. Não é necessária instalação adicional além dos pré-requisitos.

## Uso Básico

### Importando a Integração

```python
from insightforge.tools import InsightForgeTools
from agno import Agent
from agno.models import Claude  # ou outro modelo suportado
```

### Criando um Agente com Ferramentas InsightForge

```python
agent = Agent(
    model=Claude(id="claude-3-opus-20240229"),
    tools=[
        InsightForgeTools(
            analyze_project=True,
            generate_documentation=True,
            query_code=True
        )
    ]
)

# Exemplo de consulta para o agente
response = agent.generate(
    "Analise o projeto em './meu-projeto' e explique sua arquitetura"
)
```

## Opções de Configuração

A classe `InsightForgeTools` aceita os seguintes parâmetros:

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `base_url` | str | "http://localhost:8000" | URL base para a API do InsightForge |
| `analyze_project` | bool | True | Habilitar análise de projetos |
| `generate_documentation` | bool | True | Habilitar geração de documentação |
| `query_code` | bool | True | Habilitar consultas sobre código |

## Métodos Disponíveis

### analyze_project

Analisa um projeto e extrai informações sobre classes, funções e relacionamentos.

```python
result = agent.tools.analyze_project(
    project_path="./meu-projeto",
    output_dir="./documentacao",  # opcional
    config_path="./config.yml"  # opcional
)
```

### generate_documentation

Gera documentação a partir de dados analisados previamente.

```python
result = agent.tools.generate_documentation(
    parsed_data=data,  # dados de analyze_project
    output_dir="./documentacao",
    project_name="Meu Projeto",
    project_description="Descrição do projeto"
)
```

### query_code

Responde perguntas sobre o código usando LLMs.

```python
result = agent.tools.query_code(
    question="Como funciona a classe UserService?",
    project_path="./meu-projeto"  # ou forneça parsed_data
)
```

## Uso Avançado

### Fluxos de Trabalho com Múltiplos Agentes

O InsightForge pode ser integrado em fluxos de trabalho complexos com múltiplos agentes, onde cada agente tem um papel especializado:

```python
from agno import Team

# Criar agentes especializados
code_analyzer = Agent(
    name="AnalisadorDeCódigo",
    model=Claude(id="claude-3-sonnet-20240229"),
    tools=[InsightForgeTools(analyze_project=True)]
)

documentation_generator = Agent(
    name="GeradorDeDocumentação",
    model=Claude(id="claude-3-sonnet-20240229"),
    tools=[InsightForgeTools(generate_documentation=True)]
)

# Criar equipe
team = Team(
    agents=[code_analyzer, documentation_generator],
    instructions="Trabalhem juntos para analisar e documentar o projeto."
)

# Executar a consulta na equipe
response = team.generate(
    "Analisem o projeto em './meu-projeto' e gerem documentação detalhada."
)
```

### Uso sem Agno

Se o Agno não estiver disponível, você pode usar as APIs do InsightForge diretamente:

```python
from insightforge.tools import InsightForgeAPI

api = InsightForgeAPI()
result = api.analyze_project("./meu-projeto")
```

## Exemplos

Consulte os exemplos na pasta `examples/` para ver código funcional da integração:

- `agno_integration_example.py`: Exemplo básico de integração
- `agno_multi_agent.py`: Exemplo com múltiplos agentes especializados

## Resolução de Problemas

### O agente não consegue encontrar o projeto

Certifique-se de fornecer um caminho absoluto para o projeto ou um caminho relativo ao diretório de trabalho atual.

### Erros ao gerar documentação

Verifique se o diretório de saída existe e tem permissões de escrita. Se estiver usando um diretório customizado para templates, certifique-se de que os arquivos de template estão no formato correto.

### Problemas de desempenho com projetos grandes

Para projetos muito grandes, considere analisar apenas subdiretórios específicos ou excluir diretórios que não são relevantes (como `node_modules`, `venv`, etc.).

## Contribuindo

Contribuições para a integração InsightForge-Agno são bem-vindas. Por favor, consulte as diretrizes de contribuição do projeto InsightForge.

## Licença

Esta integração está licenciada sob a mesma licença do InsightForge (MIT).