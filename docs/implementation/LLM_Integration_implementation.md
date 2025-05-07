# Implementação da Integração LLM

## Visão Geral

Este documento detalha a implementação da integração de modelos de linguagem de grande escala (LLMs) no InsightForge. A implementação permite consultas em linguagem natural sobre o código, embeddings para busca semântica e geração de explicações de código, além de outros recursos avançados.

## Componentes Implementados

### 1. Interface Base (base.py)

Definimos uma interface abstrata `LLMProvider` que estabelece o contrato para todas as implementações de provedores LLM:

```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Gera texto usando o modelo LLM."""
        pass
    
    @abstractmethod
    def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Gera resposta de chat usando o modelo LLM."""
        pass
    
    @abstractmethod
    def get_embeddings(self, text: Union[str, List[str]], **kwargs) -> List[List[float]]:
        """Obtém embeddings vetoriais para texto."""
        pass
```

Esta interface garante que diferentes implementações possam ser usadas de forma intercambiável, seguindo o padrão Adapter.

### 2. Integração com Ollama (ollama.py)

Implementamos a integração com o Ollama, que permite executar modelos LLM localmente:

```python
class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model: str = "mistral", 
                 timeout: int = 60):
        """Inicializa o provedor Ollama."""
        # Inicialização...
        
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Gera texto usando o Ollama."""
        # Implementação...
        
    def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Gera resposta de chat usando o Ollama."""
        # Implementação...
        
    def get_embeddings(self, text: Union[str, List[str]], **kwargs) -> List[List[float]]:
        """Obtém embeddings usando o Ollama."""
        # Implementação...
```

A implementação utiliza a API REST do Ollama para todas as operações, permitindo geração de texto, chat e embeddings.

### 3. Sistema de Embeddings (embeddings.py)

Implementamos um sistema de armazenamento e busca de embeddings para pesquisa semântica:

```python
class EmbeddingStore:
    def __init__(self, data_dir: str, provider: LLMProvider):
        """Inicializa o armazenamento de embeddings."""
        # Inicialização...
        
    def add_embedding(self, key: str, text: str, metadata: Dict[str, Any] = None) -> None:
        """Adiciona um embedding ao armazenamento."""
        # Implementação...
        
    def search(self, query: str, top_k: int = 5, 
              filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None) -> List[Dict[str, Any]]:
        """Busca embeddings por similaridade semântica."""
        # Implementação...
```

Além disso, implementamos métodos específicos para código:

```python
def add_class_embedding(self, class_name: str, file_path: str, 
                       code: str, docstring: str,
                       metadata: Dict[str, Any] = None) -> None:
    """Adiciona um embedding de classe ao armazenamento."""
    # Implementação...

def add_function_embedding(self, function_name: str, file_path: str,
                          code: str, docstring: str,
                          metadata: Dict[str, Any] = None) -> None:
    """Adiciona um embedding de função ao armazenamento."""
    # Implementação...

def add_doc_embedding(self, doc_path: str, content: str,
                     metadata: Dict[str, Any] = None) -> None:
    """Adiciona um embedding de documentação ao armazenamento."""
    # Implementação...
```

### 4. Embedder de Código (embeddings.py)

Implementamos um utilitário `CodeEmbedder` para criar embeddings para um codebase inteiro:

```python
class CodeEmbedder:
    def __init__(self, project_path: str, data_dir: str, provider: LLMProvider):
        """Inicializa o embedder de código."""
        # Inicialização...
        
    def embed_codebase(self, parsed_data: Dict[str, Any]) -> None:
        """Cria embeddings para todo o codebase."""
        # Implementação...
        
    def embed_documentation(self, docs_dir: str) -> None:
        """Cria embeddings para arquivos de documentação."""
        # Implementação...
```

Este componente integra-se com o sistema de parsing de código para criar embeddings para classes, funções e documentação.

### 5. Motor de Consulta (query.py)

Implementamos um motor de consulta em linguagem natural:

```python
class QueryEngine:
    def __init__(self, provider: LLMProvider, embedding_store: EmbeddingStore):
        """Inicializa o motor de consulta."""
        # Inicialização...
        
    def query(self, question: str, max_sources: int = 5) -> QueryResult:
        """Responde a uma pergunta em linguagem natural sobre código."""
        # Implementação...
        
    def explain_code(self, code: str) -> QueryResult:
        """Explica um trecho de código."""
        # Implementação...
        
    def suggest_improvements(self, code: str) -> QueryResult:
        """Sugere melhorias para um trecho de código."""
        # Implementação...
        
    def generate_docstring(self, code: str, language: str = "python") -> QueryResult:
        """Gera uma docstring para um trecho de código."""
        # Implementação...
```

O motor de consulta combina busca semântica com prompts cuidadosamente projetados para fornecer respostas úteis sobre o código.

## Padrões de Design Utilizados

### 1. Padrão Adapter

Utilizamos o padrão Adapter para desacoplar a lógica de negócios da implementação específica do LLM:

```
Interface (LLMProvider) <-- Adaptador (OllamaProvider)
```

Isso permite adicionar suporte facilmente a diferentes provedores LLM no futuro.

### 2. Padrão Repository

No sistema de embeddings, utilizamos o padrão Repository para abstrair o armazenamento e recuperação de embeddings:

```
Modelo de Domínio <--> Repositório (EmbeddingStore) <--> Armazenamento
```

### 3. Padrão Strategy

O sistema de consulta utiliza o padrão Strategy para variar os algoritmos de processamento de consultas:

```
Contexto (QueryEngine) --> Estratégia (prompts e processamento específicos)
```

## Estrutura de Dados

### Embeddings

Os embeddings são armazenados como vetores de ponto flutuante, junto com metadados:

```
embeddings = {
    "código:caminho/do/arquivo.py": [0.1, 0.2, ...],
    "classe:caminho/do/arquivo.py:NomeClasse": [0.3, 0.4, ...],
    ...
}

metadata = {
    "código:caminho/do/arquivo.py": {
        "text": "...",
        "metadata": {
            "type": "code",
            "language": "python",
            ...
        }
    },
    ...
}
```

### Consultas e Resultados

As consultas em linguagem natural retornam objetos `QueryResult` que contêm:

```
QueryResult:
  - answer: string
  - sources: [
      {
        "key": "classe:caminho/do/arquivo.py:NomeClasse",
        "similarity": 0.85,
        "text": "...",
        "metadata": { ... }
      },
      ...
    ]
  - raw_response: { ... }
```

## Considerações de Implementação

### 1. Gerenciamento de Dependências

Implementamos dependências opcionais para evitar requisitos desnecessários:

```python
try:
    import numpy as np
except ImportError:
    # Fallback ou aviso...

try:
    import requests
except ImportError:
    # Fallback ou aviso...
```

### 2. Persistência

Implementamos persistência para embeddings para evitar recalculá-los a cada execução:

```python
def _save_data(self) -> None:
    """Salva embeddings e metadados em arquivos."""
    # Implementação usando pickle e json...

def _load_data(self) -> None:
    """Carrega embeddings e metadados de arquivos."""
    # Implementação...
```

### 3. Tratamento de Erros

Implementamos tratamento robusto de erros para lidar com falhas de API:

```python
try:
    response = self._make_request("api/generate", data)
    # Processar resposta...
except OllamaAPIError as e:
    self.logger.error(f"Error generating text: {str(e)}")
    # Retornar resposta de erro...
```

### 4. Logging

Implementamos logging detalhado para facilitar o diagnóstico:

```python
self.logger = logging.getLogger(__name__)
self.logger.info(f"Processing query: {question}")
```

## Integrações

### 1. Integração com o Sistema de Configuração

A integração LLM é configurável através do sistema de configuração do InsightForge:

```yaml
llm:
  provider: "ollama"
  base_url: "http://localhost:11434"
  model: "mistral"
  embeddings_model: "mistral"
  embedding_dir: ".embeddings"
  timeout: 60
```

### 2. Integração com o CLI

Adicionamos comandos ao CLI para utilizar os recursos LLM:

```
python main.py --search "como os usuários são autenticados"
python main.py --ask "Como funciona o sistema de permissões?"
python main.py --explain --file /caminho/do/arquivo.py
python main.py --improve --file /caminho/do/arquivo.py
python main.py --generate-docs --file /caminho/do/arquivo.py
```

## Testes

A implementação inclui testes para todos os componentes:

1. **Testes Unitários**: Testes para cada classe/método
2. **Testes de Integração**: Testes para o fluxo completo
3. **Mocks**: Mocks para APIs externas para testes sem dependências

## Próximos Passos

1. Implementar provedores adicionais (OpenAI, Anthropic, etc.)
2. Melhorar a qualidade dos prompts
3. Implementar um sistema de cache para respostas
4. Adicionar suporte para fine-tuning de modelos
5. Implementar vetorização por chunks para arquivos grandes

## Considerações de Desempenho

1. Ollama requer GPU para melhor desempenho (mas funciona em CPU)
2. Os embeddings são computacionalmente intensivos, mas persistidos para reutilização
3. A busca vetorial é otimizada com numpy para desempenho

## Conclusão

A implementação da integração LLM fornece uma base sólida para recursos avançados de compreensão de código, seguindo boas práticas de engenharia de software e permitindo extensibilidade para diferentes provedores LLM.