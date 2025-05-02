---
layout: default
title: API de Referência
---

# API de Referência

Esta seção documenta a API pública do InsightForge.

## Módulos Principais

- [Config](#config)
- [Reverse Engineering](#reverse-engineering)
- [LLM Integration](#llm-integration)
- [Exporters](#exporters)

## Config

### ConfigManager

```python
class ConfigManager:
    def __init__(self, config_path=None, initial_config=None):
        """
        Inicializa o gerenciador de configuração.
        
        Args:
            config_path: Caminho para o arquivo de configuração
            initial_config: Configuração inicial como dicionário
        """
        
    def load(self, config_path):
        """Carrega a configuração do arquivo especificado."""
        
    def save(self, config_path=None):
        """Salva a configuração no arquivo especificado."""
        
    def get(self, key, default=None):
        """Obtém um valor de configuração pelo caminho da chave."""
        
    def set(self, key, value):
        """Define um valor de configuração pelo caminho da chave."""
        
    def as_dict(self):
        """Retorna a configuração como um dicionário."""
```

## Reverse Engineering

### CodeParser

```python
class CodeParser:
    def __init__(self, project_path, exclude_dirs=None, exclude_files=None):
        """
        Inicializa o parser de código.
        
        Args:
            project_path: Caminho do projeto a ser analisado
            exclude_dirs: Lista de diretórios a serem excluídos
            exclude_files: Lista de arquivos a serem excluídos
        """
        
    def parse(self):
        """
        Analisa o projeto e retorna os dados analisados.
        
        Returns:
            Dicionário com dados analisados do projeto
        """
```

### DiagramGenerator

```python
class DiagramGenerator:
    def __init__(self, max_items_per_diagram=20, detect_relationships=True):
        """
        Inicializa o gerador de diagramas.
        
        Args:
            max_items_per_diagram: Número máximo de itens por diagrama
            detect_relationships: Se deve detectar relacionamentos automaticamente
        """
        
    def generate_class_diagram(self, parsed_data, include_methods=True, 
                            include_attributes=True, include_private=False,
                            max_methods=5, filter_classes=None, languages=None):
        """
        Gera um diagrama de classe a partir dos dados analisados.
        
        Returns:
            String contendo o diagrama em sintaxe Mermaid
        """
        
    def generate_module_diagram(self, parsed_data, group_by_package=True,
                             include_external=False, max_modules=30, styles=True):
        """
        Gera um diagrama de módulo a partir dos dados analisados.
        
        Returns:
            String contendo o diagrama em sintaxe Mermaid
        """
        
    def generate_sequence_diagram(self, parsed_data, flow_name, max_depth=5, analyze_flows=True):
        """
        Gera um diagrama de sequência para um fluxo específico.
        
        Returns:
            String contendo o diagrama em sintaxe Mermaid
        """
```

### DocGenerator

```python
class DocGenerator:
    def __init__(self, output_dir, custom_templates_dir=None, generate_diagrams=True, max_items_per_diagram=20):
        """
        Inicializa o gerador de documentação.
        
        Args:
            output_dir: Diretório de saída para a documentação
            custom_templates_dir: Diretório opcional para templates personalizados
            generate_diagrams: Se deve gerar diagramas
            max_items_per_diagram: Número máximo de itens por diagrama
        """
        
    def generate(self, parsed_data, project_name="Project", project_description=""):
        """
        Gera documentação a partir dos dados analisados.
        
        Args:
            parsed_data: Dicionário contendo os dados analisados
            project_name: Nome do projeto
            project_description: Descrição do projeto
        """
```

## LLM Integration

### LLMProvider

```python
class LLMProvider(ABC):
    """Classe base para provedores de LLM."""
    
    @abstractmethod
    def generate(self, prompt, **kwargs):
        """
        Gera texto usando o modelo LLM.
        
        Args:
            prompt: O prompt de texto para o modelo
            
        Returns:
            LLMResponse contendo texto gerado e metadados
        """
        
    @abstractmethod
    def generate_chat(self, messages, **kwargs):
        """
        Gera respostas de chat usando o modelo LLM.
        
        Args:
            messages: Lista de mensagens de chat
            
        Returns:
            LLMResponse contendo texto gerado e metadados
        """
        
    @abstractmethod
    def get_embeddings(self, texts, **kwargs):
        """
        Gera embeddings para textos.
        
        Args:
            texts: Lista de textos para gerar embeddings
            
        Returns:
            Lista de embeddings de vetores
        """
```

## Exporters

### GitHubExporter

```python
class GitHubExporter:
    def __init__(self, source_dir, github_repo_dir=None, github_pages_dir="docs", use_jekyll=True):
        """
        Inicializa o exportador para GitHub.
        
        Args:
            source_dir: Diretório contendo a documentação gerada
            github_repo_dir: Caminho para o repositório GitHub (None para apenas preparar arquivos)
            github_pages_dir: Diretório no repositório para GitHub Pages (geralmente "docs")
            use_jekyll: Se deve configurar para GitHub Pages com Jekyll
        """
        
    def export(self, project_name, project_description=""):
        """
        Exporta a documentação para formato GitHub.
        
        Returns:
            Caminho para a documentação exportada
        """
        
    def publish(self, branch="gh-pages", commit_message="Update documentation", force_push=False):
        """
        Publica a documentação no repositório GitHub.
        
        Returns:
            True se bem-sucedido, False caso contrário
        """
```