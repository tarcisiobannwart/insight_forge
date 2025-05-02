# Configuração do InsightForge

Este documento descreve as opções de configuração disponíveis no InsightForge.

## Visão Geral

O InsightForge suporta configuração através dos seguintes métodos, em ordem de precedência (do mais alto para o mais baixo):

1. **Argumentos de linha de comando**: Sobrescrevem todas as outras configurações
2. **Variáveis de ambiente**: Sobrescrevem configurações de arquivo
3. **Arquivo de configuração**: Arquivo YAML ou JSON
4. **Valores padrão**: Utilizados quando nenhuma outra configuração é fornecida

## Arquivo de Configuração

Por padrão, o InsightForge procura por um arquivo de configuração nos seguintes locais, em ordem:

1. `./insightforge.yml` ou `./insightforge.yaml` (diretório atual)
2. `./insightforge.json` (diretório atual)
3. `./config/insightforge.yml` ou `./config/insightforge.yaml` (subdiretório config)
4. `./config/insightforge.json` (subdiretório config)
5. `~/.config/insightforge/config.yml` (diretório de configuração do usuário)
6. `/etc/insightforge/config.yml` (em sistemas Linux/Mac)

Você também pode especificar explicitamente um arquivo de configuração com a opção `--config`:

```bash
insightforge --project ./meu-projeto --config ./minha-config.yml
```

### Formato

A configuração pode ser especificada em formato YAML ou JSON. Ambos os formatos suportam as mesmas opções.

## Gerando um Arquivo de Configuração

Você pode gerar um arquivo de configuração padrão com a opção `--generate-config`:

```bash
insightforge --generate-config ./insightforge.yml
```

## Perfis de Configuração

O InsightForge suporta perfis de configuração para diferentes ambientes:

- `default`: Configuração padrão
- `minimal`: Configuração mínima com apenas os recursos essenciais
- `production`: Configuração otimizada para uso em produção

Você pode especificar o perfil com a opção `--profile`:

```bash
insightforge --project ./meu-projeto --profile production
```

## Variáveis de Ambiente

As variáveis de ambiente devem começar com o prefixo `INSIGHTFORGE_` seguido pela seção e chave separadas por underscore. Por exemplo:

```bash
export INSIGHTFORGE_GENERAL_OUTPUT_DIR=/path/to/output
export INSIGHTFORGE_PARSER_LANGUAGES_PYTHON_ENABLED=true
```

## Referência de Opções

### Seção `general`

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `output_dir` | string | `./output` | Diretório de saída para a documentação gerada |
| `log_level` | string | `INFO` | Nível de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `profile` | string | `default` | Perfil de configuração |

### Seção `parser`

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `exclude_dirs` | array | `["venv", "env", ".git", ...]` | Diretórios a serem excluídos da análise |
| `exclude_files` | array | `["*.pyc", "*.pyo", ...]` | Arquivos a serem excluídos da análise |
| `languages` | object | | Configuração por linguagem |

#### Configuração de Linguagens

##### Python

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita ou desabilita a análise de Python |
| `extensions` | array | `[".py"]` | Extensões de arquivo para análise |
| `detect_docstrings` | boolean | `true` | Detecta docstrings em código Python |
| `detect_types` | boolean | `true` | Detecta tipos em anotações Python |

##### PHP

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita ou desabilita a análise de PHP |
| `extensions` | array | `[".php"]` | Extensões de arquivo para análise |
| `detect_docstrings` | boolean | `true` | Detecta docstrings em código PHP |

##### JavaScript

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `enabled` | boolean | `false` | Habilita ou desabilita a análise de JavaScript |
| `extensions` | array | `[".js", ".jsx"]` | Extensões de arquivo para análise |
| `detect_jsdoc` | boolean | `true` | Detecta comentários JSDoc |

##### TypeScript

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `enabled` | boolean | `false` | Habilita ou desabilita a análise de TypeScript |
| `extensions` | array | `[".ts", ".tsx"]` | Extensões de arquivo para análise |
| `detect_tsdoc` | boolean | `true` | Detecta comentários TSDoc |

### Seção `doc_generator`

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `output_format` | string | `markdown` | Formato de saída (`markdown`, `html`, `pdf`) |
| `template_dir` | string | `null` | Diretório de templates customizados |
| `generate_diagrams` | boolean | `true` | Gera diagramas |
| `diagram_format` | string | `mermaid` | Formato de diagramas (`mermaid`, `plantuml`) |
| `diagram_types` | array | `["class", "module", "sequence"]` | Tipos de diagramas a gerar |
| `index_template` | string | `index.md.j2` | Template para o índice |
| `include_source_links` | boolean | `true` | Inclui links para o código fonte |

### Seção `business_rules`

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita extração de regras de negócio |
| `extract_from_code` | boolean | `true` | Extrai regras de validações no código |
| `extract_from_comments` | boolean | `true` | Extrai regras de comentários |
| `extract_from_docstrings` | boolean | `true` | Extrai regras de docstrings |
| `patterns` | array | `["Business Rule:", "BR:", ...]` | Padrões para identificar regras |

### Seção `usecase_extractor`

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita extração de casos de uso |
| `extract_from_docstrings` | boolean | `true` | Extrai casos de uso de docstrings |
| `extract_from_comments` | boolean | `true` | Extrai casos de uso de comentários |
| `extract_from_method_names` | boolean | `true` | Infere casos de uso de nomes de métodos |

### Seção `backlog_builder`

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita geração de backlog |
| `format` | string | `markdown` | Formato de saída (`markdown`, `json`, `yaml`, `csv`) |
| `include_priority` | boolean | `true` | Inclui prioridade no backlog |
| `include_story_points` | boolean | `true` | Inclui story points no backlog |

### Seção `llm` (Integração com Modelos de Linguagem)

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `enabled` | boolean | `false` | Habilita integração com LLM |
| `provider` | string | `ollama` | Provedor LLM (`ollama`, `openai`, `anthropic`, `local`, `huggingface`) |
| `model` | string | `llama2` | Modelo a utilizar |
| `endpoint` | string | `http://localhost:11434/api` | Endpoint da API |
| `max_tokens` | integer | `1024` | Máximo de tokens a gerar |
| `temperature` | float | `0.7` | Temperatura (0-1) |
| `embeddings_model` | string | `all-MiniLM-L6-v2` | Modelo para embeddings |

## Exemplo de Configuração Completa

```yaml
# Configuração do InsightForge
general:
  output_dir: "./output"
  log_level: "INFO"
  profile: "default"

parser:
  exclude_dirs:
    - "venv"
    - "env"
    - ".git"
    - ".github"
    - "node_modules"
    - "__pycache__"
    - ".vscode"
    - ".idea"
  exclude_files:
    - "*.pyc"
    - "*.pyo"
    - "*.pyd"
    - "*.so"
    - "*.dylib"
    - "*.dll"
    - "*.egg-info"
    - "*.egg"
    - "*.whl"
  languages:
    python:
      enabled: true
      extensions: [".py"]
      detect_docstrings: true
      detect_types: true
    php:
      enabled: true
      extensions: [".php"]
      detect_docstrings: true
    javascript:
      enabled: false
      extensions: [".js", ".jsx"]
      detect_jsdoc: true
    typescript:
      enabled: false
      extensions: [".ts", ".tsx"]
      detect_tsdoc: true

doc_generator:
  output_format: "markdown"
  template_dir: null
  generate_diagrams: true
  diagram_format: "mermaid"
  diagram_types: ["class", "module", "sequence"]
  index_template: "index.md.j2"
  include_source_links: true

business_rules:
  enabled: true
  extract_from_code: true
  extract_from_comments: true
  extract_from_docstrings: true
  patterns:
    - "Business Rule:"
    - "BR:"
    - "must"
    - "should"
    - "required"
    - "cannot"
    - "must not"

usecase_extractor:
  enabled: true
  extract_from_docstrings: true
  extract_from_comments: true
  extract_from_method_names: true

backlog_builder:
  enabled: true
  format: "markdown"
  include_priority: true
  include_story_points: true

llm:
  enabled: false
  provider: "ollama"
  model: "llama2"
  endpoint: "http://localhost:11434/api"
  max_tokens: 1024
  temperature: 0.7
  embeddings_model: "all-MiniLM-L6-v2"
```

## Configuração Mínima

Para começar rapidamente, uma configuração mínima pode ser usada:

```yaml
general:
  output_dir: "./docs"
  log_level: "INFO"

parser:
  exclude_dirs:
    - "venv"
    - "node_modules"
  languages:
    python:
      enabled: true
      extensions: [".py"]

doc_generator:
  output_format: "markdown"
  generate_diagrams: true

business_rules:
  enabled: true

usecase_extractor:
  enabled: true

backlog_builder:
  enabled: true
  format: "markdown"
```