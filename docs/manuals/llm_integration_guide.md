# Guia de Integração LLM para Desenvolvedores

## Introdução

Este guia é destinado a desenvolvedores que desejam estender o InsightForge com suporte a novos modelos LLM ou personalizações avançadas dos recursos de LLM existentes. Vamos abordar o processo de integração passo a passo, desde a compreensão da arquitetura até a implementação de um novo provedor LLM.

## Pré-requisitos

* Conhecimento básico de Python e orientação a objetos
* Familiaridade com APIs de modelos de linguagem
* Compreensão básica de embeddings vetoriais
* Instalação do InsightForge configurada e funcional

## Arquitetura LLM do InsightForge

O sistema LLM do InsightForge segue uma arquitetura em camadas:

1. **Camada de Abstração**: Define interfaces para provedores LLM
2. **Camada de Provedores**: Implementações específicas para diferentes serviços LLM
3. **Camada de Serviços**: Funcionalidades construídas sobre os provedores (embeddings, consultas)
4. **Camada de Interface**: APIs e CLI para interagir com os serviços

A estrutura de módulos reflete esta arquitetura:

```
insightforge/llm/
├── __init__.py
├── base.py           # Abstrações e interfaces
├── ollama.py         # Implementação do provedor Ollama
├── embeddings.py     # Sistema de embeddings e busca vetorial
└── query.py          # Motor de consulta e geração
```

## Implementando um Novo Provedor LLM

### Passo 1: Entenda a Interface LLMProvider

A interface base que todos os provedores devem implementar está definida em `base.py`:

```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    def get_embeddings(self, text: Union[str, List[str]], **kwargs) -> List[List[float]]:
        pass
```

É essencial compreender a responsabilidade de cada método:

* `generate()`: Processa um prompt e retorna texto gerado
* `generate_chat()`: Processa uma conversa de múltiplas mensagens
* `get_embeddings()`: Produz representações vetoriais de texto

### Passo 2: Crie um Novo Arquivo de Provedor

Para um novo provedor (por exemplo, OpenAI), crie um arquivo dedicado:

```python
# openai_provider.py
from typing import Dict, List, Any, Optional, Union
import logging
import openai  # Importe a biblioteca necessária para seu provedor

from .base import LLMProvider, LLMResponse

class OpenAIProvider(LLMProvider):
    """Provedor para OpenAI API."""
    
    def __init__(self, api_key: str, 
                 model: str = "gpt-3.5-turbo", 
                 embedding_model: str = "text-embedding-ada-002",
                 timeout: int = 60):
        """
        Inicializa o provedor OpenAI.
        
        Args:
            api_key: Chave de API OpenAI
            model: Modelo para geração de texto
            embedding_model: Modelo para embeddings
            timeout: Timeout em segundos
        """
        # Inicialização
        self.api_key = api_key
        self.model = model
        self.embedding_model = embedding_model
        self.timeout = timeout
        
        # Configure a API
        openai.api_key = api_key
        
        self.logger = logging.getLogger(__name__)
```

### Passo 3: Implemente os Métodos Obrigatórios

#### Método generate()

```python
def generate(self, prompt: str, **kwargs) -> LLMResponse:
    """
    Gera texto usando a API OpenAI.
    
    Args:
        prompt: O prompt de entrada
        **kwargs: Parâmetros adicionais (temperature, max_tokens, etc.)
        
    Returns:
        LLMResponse: Resposta formatada
    """
    try:
        # Obter parâmetros, usar valores padrão se não fornecidos
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 1000)
        model = kwargs.get('model', self.model)
        
        # Fazer chamada à API
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout
        )
        
        # Extrair conteúdo da resposta
        content = response.choices[0].message.content
        
        # Construir objeto de resposta
        return LLMResponse(
            content=content,
            model=model,
            usage=response.usage.to_dict(),
            raw_response=response
        )
    
    except Exception as e:
        self.logger.error(f"Erro na geração de texto: {str(e)}")
        return LLMResponse(
            content=f"Erro: {str(e)}",
            model=model,
            usage={'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        )
```

#### Método generate_chat()

```python
def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
    """
    Gera resposta de chat usando a API OpenAI.
    
    Args:
        messages: Lista de mensagens com 'role' e 'content'
        **kwargs: Parâmetros adicionais
        
    Returns:
        LLMResponse: Resposta formatada
    """
    try:
        # Obter parâmetros
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 1000)
        model = kwargs.get('model', self.model)
        
        # Transformar mensagens no formato esperado pela API
        api_messages = [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in messages
        ]
        
        # Fazer chamada à API
        response = openai.ChatCompletion.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout
        )
        
        # Extrair conteúdo da resposta
        content = response.choices[0].message.content
        
        # Construir objeto de resposta
        return LLMResponse(
            content=content,
            model=model,
            usage=response.usage.to_dict(),
            raw_response=response
        )
    
    except Exception as e:
        self.logger.error(f"Erro na geração de chat: {str(e)}")
        return LLMResponse(
            content=f"Erro: {str(e)}",
            model=model,
            usage={'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        )
```

#### Método get_embeddings()

```python
def get_embeddings(self, text: Union[str, List[str]], **kwargs) -> List[List[float]]:
    """
    Obtém embeddings vetoriais usando a API OpenAI.
    
    Args:
        text: Texto ou lista de textos
        **kwargs: Parâmetros adicionais
        
    Returns:
        Lista de vetores de embedding
    """
    try:
        # Determinar modelo a usar
        model = kwargs.get('model', self.embedding_model)
        
        # Normalizar entrada para lista
        texts = [text] if isinstance(text, str) else text
        
        # Fazer chamada à API
        response = openai.Embedding.create(
            input=texts,
            model=model,
            timeout=self.timeout
        )
        
        # Extrair embeddings
        embeddings = [item.embedding for item in response.data]
        
        return embeddings
    
    except Exception as e:
        self.logger.error(f"Erro na geração de embeddings: {str(e)}")
        # Retornar lista vazia em caso de erro
        return [[] for _ in range(len(texts) if isinstance(text, list) else 1)]
```

### Passo 4: Implemente Métodos Auxiliares Específicos

Adicione métodos específicos do seu provedor:

```python
def list_available_models(self) -> List[str]:
    """Lista modelos disponíveis na API OpenAI."""
    try:
        response = openai.Model.list()
        return [model.id for model in response.data]
    except Exception as e:
        self.logger.error(f"Erro ao listar modelos: {str(e)}")
        return []
```

### Passo 5: Atualize a Configuração

Modifique o esquema de configuração para suportar seu novo provedor:

```python
# config_schema.py
SCHEMA = {
    # ... esquema existente
    "llm": {
        "type": "dict",
        "schema": {
            "provider": {
                "type": "string", 
                "allowed": ["ollama", "openai"],  # Adicione seu provedor
                "default": "ollama"
            },
            "ollama": {
                "type": "dict",
                "schema": {
                    # ... configuração Ollama existente
                }
            },
            "openai": {  # Adicione configuração para seu provedor
                "type": "dict",
                "schema": {
                    "api_key": {"type": "string", "required": True},
                    "model": {"type": "string", "default": "gpt-3.5-turbo"},
                    "embedding_model": {"type": "string", "default": "text-embedding-ada-002"},
                    "timeout": {"type": "integer", "default": 60}
                }
            }
        }
    }
}
```

### Passo 6: Atualize a Fábrica de Provedores

Modifique o mecanismo que instancia os provedores:

```python
# __init__.py
from .base import LLMProvider
from .ollama import OllamaProvider
from .openai_provider import OpenAIProvider  # Importe seu provedor

def create_provider(config) -> LLMProvider:
    """
    Cria um provedor LLM baseado na configuração.
    
    Args:
        config: Configuração do LLM
        
    Returns:
        LLMProvider: O provedor instanciado
    """
    provider_name = config.get("provider", "ollama")
    
    if provider_name == "ollama":
        # Configuração Ollama
        base_url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
        model = config.get("ollama", {}).get("model", "mistral")
        timeout = config.get("ollama", {}).get("timeout", 60)
        
        return OllamaProvider(
            base_url=base_url,
            model=model,
            timeout=timeout
        )
    
    elif provider_name == "openai":
        # Configuração OpenAI
        api_key = config.get("openai", {}).get("api_key")
        if not api_key:
            raise ValueError("API key is required for OpenAI provider")
            
        model = config.get("openai", {}).get("model", "gpt-3.5-turbo")
        embedding_model = config.get("openai", {}).get("embedding_model", "text-embedding-ada-002")
        timeout = config.get("openai", {}).get("timeout", 60)
        
        return OpenAIProvider(
            api_key=api_key,
            model=model,
            embedding_model=embedding_model,
            timeout=timeout
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
```

### Passo 7: Teste seu Provedor

Crie testes unitários para seu provedor:

```python
# test_openai_provider.py
import unittest
from unittest.mock import patch, MagicMock
from insightforge.llm.openai_provider import OpenAIProvider

class TestOpenAIProvider(unittest.TestCase):
    
    @patch('openai.ChatCompletion.create')
    def test_generate(self, mock_create):
        # Configurar mock
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.to_dict.return_value = {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
        mock_create.return_value = mock_response
        
        # Criar provedor
        provider = OpenAIProvider(api_key="test_key")
        
        # Testar método
        response = provider.generate("Test prompt")
        
        # Verificar resultado
        self.assertEqual(response.content, "Test response")
        self.assertEqual(response.usage["total_tokens"], 30)
        mock_create.assert_called_once()
        
    # Adicionar mais testes...
```

## Integração com Outras Partes do Sistema

### Uso com o Sistema de Embeddings

```python
from insightforge.llm import create_provider
from insightforge.llm.embeddings import EmbeddingStore
from insightforge.config.config_manager import ConfigManager

# Carregar configuração
config_manager = ConfigManager("config.yml")
config = config_manager.get_config()

# Criar provedor conforme configuração
provider = create_provider(config.get("llm", {}))

# Criar store de embeddings
embedding_store = EmbeddingStore(
    data_dir=config.get("llm", {}).get("embedding_dir", ".embeddings"),
    provider=provider
)

# Usar o store
embedding_store.add_embedding("test", "This is a test")
results = embedding_store.search("example query")
```

### Uso com o Motor de Consulta

```python
from insightforge.llm import create_provider
from insightforge.llm.embeddings import EmbeddingStore
from insightforge.llm.query import QueryEngine

# Configurar provedor e embeddings
provider = create_provider(config.get("llm", {}))
embedding_store = EmbeddingStore(data_dir, provider)

# Criar motor de consulta
query_engine = QueryEngine(provider, embedding_store)

# Fazer consulta
result = query_engine.query("Como funciona a autenticação?")
print(result.format_markdown())
```

## Boas Práticas para Extensões LLM

1. **Tratamento de Erros Robusto**: Sempre capture exceções e forneça fallbacks apropriados.

2. **Respeite os Limites de Rate**: Implemente backoff exponencial para respeitar limites de API.

3. **Segurança de Credenciais**: Nunca hardcode chaves de API; use variáveis de ambiente ou gerenciamento seguro de credenciais.

4. **Consistência de Resposta**: Mantenha o formato de resposta consistente entre provedores.

5. **Personalização de Prompts**: Permita personalização de prompts para diferentes casos de uso.

6. **Testes Abrangentes**: Crie mocks para APIs externas para garantir testabilidade.

## Depuração

Para depurar problemas em integrações LLM:

1. Ative logging detalhado:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Verifique erros de API:

```python
try:
    # Código que faz chamada de API
except Exception as e:
    print(f"API Error: {str(e)}")
    print(f"Request details: {prompt[:100]}...")
```

3. Inspecione respostas brutas:

```python
response = provider.generate("Test")
print("Raw response:", response.raw_response)
```

## Casos de Uso Avançados

### 1. Sistema de Fallback entre Provedores

```python
class FallbackProvider(LLMProvider):
    """Provedor que tenta múltiplos provedores em sequência."""
    
    def __init__(self, providers: List[LLMProvider]):
        self.providers = providers
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Tenta cada provedor até um ter sucesso."""
        last_error = None
        
        for provider in self.providers:
            try:
                response = provider.generate(prompt, **kwargs)
                if "Error" not in response.content:
                    return response
            except Exception as e:
                last_error = e
        
        # Se todos falharem, retorna erro
        return LLMResponse(
            content=f"All providers failed. Last error: {str(last_error)}",
            model="fallback",
            usage={'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        )
    
    # Implementar também generate_chat e get_embeddings
```

### 2. Cache de Respostas

```python
import hashlib
import json
import os

class CachedProvider(LLMProvider):
    """Provedor com cache de respostas."""
    
    def __init__(self, base_provider: LLMProvider, cache_dir: str = ".cache"):
        self.provider = base_provider
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, prompt: str, **kwargs) -> str:
        """Gera uma chave de cache a partir do prompt e parâmetros."""
        cache_data = {"prompt": prompt, "params": kwargs}
        data_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """Retorna o caminho para o arquivo de cache."""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Gera texto com cache."""
        cache_key = self._get_cache_key(prompt, **kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        # Verificar cache
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
                return LLMResponse(
                    content=cached_data['content'],
                    model=cached_data['model'],
                    usage=cached_data['usage'],
                    raw_response=cached_data.get('raw_response')
                )
        
        # Gerar resposta e armazenar no cache
        response = self.provider.generate(prompt, **kwargs)
        
        # Salvar no cache
        cached_data = {
            'content': response.content,
            'model': response.model,
            'usage': response.usage
        }
        with open(cache_path, 'w') as f:
            json.dump(cached_data, f)
        
        return response
    
    # Implementar também generate_chat e get_embeddings
```

## Conclusão

Estender o InsightForge com novos provedores LLM é um processo direto que envolve a implementação da interface `LLMProvider`. Seguindo os padrões e práticas descritos neste guia, você pode adicionar suporte para qualquer serviço LLM e personalizar o comportamento conforme necessário.

Lembre-se de que o padrão Adapter utilizado permite que o resto do sistema trabalhe com seu novo provedor sem alterações adicionais, desde que você siga a interface definida.

## Recursos Adicionais

- [Código-fonte do módulo LLM](https://github.com/seu-repo/insight_forge/tree/main/insightforge/llm)
- [Documentação da API Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Documentação da API OpenAI](https://platform.openai.com/docs/api-reference)
- [Conceitos de Embeddings](https://platform.openai.com/docs/guides/embeddings)