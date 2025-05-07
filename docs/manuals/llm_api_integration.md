# InsightForge - API de Integração LLM

## Visão Geral

Este documento descreve a API de integração de modelos de linguagem de grande escala (LLMs) para desenvolvedores que desejam estender ou personalizar os recursos de LLM do InsightForge.

A arquitetura de integração LLM do InsightForge foi projetada para ser extensível, seguindo o padrão Adapter. Isso permite adicionar suporte para diferentes provedores de LLM além do Ollama, como OpenAI, Anthropic, Azure, etc.

## Arquitetura

A integração de LLM é organizada em vários componentes:

1. **LLMProvider (base.py)**: Interface base abstrata para todos os provedores LLM
2. **OllamaProvider (ollama.py)**: Implementação concreta para o Ollama
3. **EmbeddingStore (embeddings.py)**: Sistema de armazenamento e busca de embeddings
4. **CodeEmbedder (embeddings.py)**: Utilitário para criar embeddings de código-fonte
5. **QueryEngine (query.py)**: Motor de consulta em linguagem natural

```
Base ──> Provedores específicos (Ollama, OpenAI, etc.)
  │
  │
  ├──> Embeddings e busca semântica
  │
  └──> Motor de consulta e geração
```

## Criando um Novo Provedor LLM

Para adicionar suporte a um novo serviço LLM, crie uma nova classe que implemente `LLMProvider`:

```python
from insightforge.llm.base import LLMProvider, LLMResponse

class MyCustomProvider(LLMProvider):
    """Provider para meu serviço LLM personalizado."""
    
    def __init__(self, api_key, model_name, etc...):
        # Inicialização específica
        pass
    
    def generate(self, prompt, **kwargs):
        # Implementar geração de texto
        # Retornar objeto LLMResponse
        pass
    
    def generate_chat(self, messages, **kwargs):
        # Implementar chat
        # Retornar objeto LLMResponse
        pass
    
    def get_embeddings(self, text, **kwargs):
        # Implementar geração de embeddings
        # Retornar lista de vetores
        pass
```

## Métodos da Interface LLMProvider

### generate(prompt, **kwargs)

Gera texto a partir de um prompt único.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| prompt | str | Texto de entrada para o modelo |
| **kwargs | dict | Parâmetros adicionais (temperatura, tokens máximos, etc.) |

**Retorno**: objeto `LLMResponse`

### generate_chat(messages, **kwargs)

Gera resposta para uma conversa com múltiplas mensagens.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| messages | List[Dict] | Lista de mensagens, cada uma com 'role' e 'content' |
| **kwargs | dict | Parâmetros adicionais (temperatura, tokens máximos, etc.) |

**Retorno**: objeto `LLMResponse`

### get_embeddings(text, **kwargs)

Gera embeddings vetoriais para texto.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| text | str ou List[str] | Texto ou lista de textos para embedding |
| **kwargs | dict | Parâmetros adicionais (modelo específico, etc.) |

**Retorno**: Lista de vetores de embedding (List[List[float]])

## Interface EmbeddingStore

A classe `EmbeddingStore` gerencia armazenamento e busca de embeddings:

```python
# Criando um store de embeddings
from insightforge.llm.embeddings import EmbeddingStore
from insightforge.llm.ollama import OllamaProvider

provider = OllamaProvider()
store = EmbeddingStore(".embeddings", provider)

# Adicionando embeddings
store.add_class_embedding(
    class_name="MyClass",
    file_path="path/to/file.py",
    code="class MyClass:\n    ...",
    docstring="Class documentation"
)

# Buscando por similaridade
results = store.search("como gerenciar autenticação", top_k=5)
```

## Interface QueryEngine

A classe `QueryEngine` fornece uma interface para consultas em linguagem natural:

```python
from insightforge.llm.query import QueryEngine

# Criar o motor de consulta
engine = QueryEngine(provider, embedding_store)

# Realizar consulta
result = engine.query("Como funciona o sistema de autenticação?")

# Explicar código
explanation = engine.explain_code("def calculate_tax(amount):\n    return amount * 0.1")

# Sugerir melhorias
suggestions = engine.suggest_improvements("for i in range(len(items)):\n    print(items[i])")

# Gerar docstring
docstring = engine.generate_docstring("def add(a, b):\n    return a + b")
```

## Configuração

Os provedores LLM são configuráveis através do sistema de configuração do InsightForge:

```yaml
llm:
  # Provedor a ser utilizado
  provider: "ollama"
  
  # Configurações do Ollama
  ollama:
    base_url: "http://localhost:11434"
    model: "mistral"
    timeout: 60
  
  # Configurações de OpenAI (se implementado)
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
    
  # Configurações para embeddings
  embeddings:
    model: "mistral"
    store_dir: ".embeddings"
```

## Exemplos de Uso

### Usando o Provedor Ollama

```python
from insightforge.llm.ollama import OllamaProvider

# Criar provedor
provider = OllamaProvider(
    base_url="http://localhost:11434",
    model="mistral"
)

# Gerar texto
response = provider.generate(
    prompt="Explique como funciona um parser de código.",
    temperature=0.5,
    max_tokens=500
)

print(response.content)
```

### Usando o Motor de Consulta

```python
from insightforge.llm.query import QueryEngine
from insightforge.llm.embeddings import EmbeddingStore
from insightforge.llm.ollama import OllamaProvider

# Setup
provider = OllamaProvider()
store = EmbeddingStore(".embeddings", provider)
engine = QueryEngine(provider, store)

# Consulta
result = engine.query("Como os usuários são autenticados neste sistema?")

# Exibir resposta formatada em markdown
print(result.format_markdown())
```

### Embedding de Código

```python
from insightforge.llm.embeddings import CodeEmbedder
from insightforge.llm.ollama import OllamaProvider
from insightforge.reverse_engineering.code_parser import CodeParser

# Parse do código
parser = CodeParser("/path/to/project")
parsed_data = parser.parse()

# Criar embeddings
provider = OllamaProvider()
embedder = CodeEmbedder("/path/to/project", ".embeddings", provider)
embedder.embed_codebase(parsed_data)
```

## Melhores Práticas

1. **Tratamento de Erros**: Implemente tratamento robusto de erros para lidar com falhas de API e limites de rate.

2. **Caching**: Use caching para economizar tokens e melhorar o desempenho, especialmente para embeddings.

3. **Parâmetros Padrão**: Forneça parâmetros padrão sensatos para cada provedor.

4. **Prompts Consistentes**: Mantenha os prompts consistentes entre provedores para garantir comportamento previsível.

5. **Timeout e Retries**: Configure timeouts apropriados e implemente retries para solicitações de API.

## Extensões Futuras

Possíveis extensões para a integração LLM incluem:

1. Implementações adicionais para OpenAI, Anthropic, Hugging Face, etc.
2. Sistema avançado de prompting com templates
3. Geração de código
4. Refatoração automática
5. Detecção de bugs
6. Testes automatizados

## Considerações de Segurança

Ao implementar integrações de LLM, considere:

1. **Gerenciamento de Credenciais**: Armazene chaves de API com segurança.
2. **Validação de Saída**: Valide a saída do modelo antes de executar código gerado.
3. **Limitações de Uso**: Implemente limites de uso para evitar custos excessivos.
4. **Privacidade dos Dados**: Considere quais dados são enviados aos provedores LLM.

## Referências

- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)