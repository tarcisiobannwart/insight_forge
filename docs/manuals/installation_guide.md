# Guia de Instalação e Configuração do InsightForge

Este guia fornece instruções detalhadas para instalar, configurar e começar a usar o InsightForge para análise e documentação de código.

## Índice

- [Requisitos do Sistema](#requisitos-do-sistema)
- [Instalação](#instalação)
  - [Instalação via pip](#instalação-via-pip)
  - [Instalação a partir do código-fonte](#instalação-a-partir-do-código-fonte)
  - [Instalação de dependências opcionais](#instalação-de-dependências-opcionais)
- [Configuração Básica](#configuração-básica)
  - [Configuração via linha de comando](#configuração-via-linha-de-comando)
  - [Usando o arquivo de configuração](#usando-o-arquivo-de-configuração)
- [Configuração Avançada](#configuração-avançada)
  - [Configurando a Interface Web](#configurando-a-interface-web)
  - [Configurando Perfis](#configurando-perfis)
  - [Segurança de Credenciais](#segurança-de-credenciais)
- [Integrações](#integrações)
  - [Configurando Integração com Jira](#configurando-integração-com-jira)
  - [Configurando Integração com GitHub](#configurando-integração-com-github)
  - [Configurando Integração com LLMs](#configurando-integração-com-llms)
- [Resolução de Problemas](#resolução-de-problemas)
  - [Problemas Comuns](#problemas-comuns)
  - [Registro de Logs](#registro-de-logs)

## Requisitos do Sistema

Antes de instalar o InsightForge, certifique-se de que seu sistema atende aos seguintes requisitos:

- **Python**: Versão 3.8 ou superior
- **Sistema Operacional**: Windows, macOS ou Linux
- **Espaço em Disco**: Mínimo de 100MB para a instalação básica (mais espaço necessário para projetos grandes)
- **Memória**: Mínimo de 2GB de RAM (4GB+ recomendado para projetos grandes)
- **Processador**: Múltiplos núcleos recomendados para análise paralela

## Instalação

### Instalação via pip

O método mais simples de instalação é através do pip, o gerenciador de pacotes do Python:

```bash
pip install insightforge
```

Para garantir que você tenha a versão mais recente, você pode especificar:

```bash
pip install --upgrade insightforge
```

### Instalação a partir do código-fonte

Para instalar a partir do código-fonte, clone o repositório e execute o script de instalação:

```bash
git clone https://github.com/seu-usuario/insight_forge.git
cd insight_forge
pip install -e .
```

Esta instalação em modo edição (`-e`) é útil para desenvolvimento, pois reflete imediatamente as alterações no código-fonte.

### Instalação de dependências opcionais

O InsightForge tem diversos grupos de dependências opcionais que podem ser instalados conforme necessário:

```bash
# Para suporte a interface web
pip install insightforge[web]

# Para integração com Jira
pip install insightforge[jira]

# Para webscraping
pip install insightforge[webscraping]

# Para todas as funcionalidades extras
pip install insightforge[all]
```

## Configuração Básica

Após a instalação, você pode configurar o InsightForge usando a linha de comando ou um arquivo de configuração.

### Configuração via linha de comando

O InsightForge inclui uma ferramenta de configuração simplificada que guiará você pelo processo inicial:

```bash
insightforge-config setup
```

Este comando interativo ajudará você a configurar:
- Caminhos do projeto
- Integração com LLMs (como Ollama)
- Integração com Jira e GitHub (opcional)

Você também pode configurar aspectos específicos:

```bash
# Configurar integração com Jira
insightforge-config jira

# Configurar integração com GitHub
insightforge-config github

# Configurar caminhos do projeto
insightforge-config paths
```

### Usando o arquivo de configuração

O InsightForge usa arquivos YAML para configuração. Um arquivo de configuração padrão pode ser gerado com:

```bash
insightforge generate-config insightforge.yml
```

O arquivo gerado terá esta estrutura básica:

```yaml
general:
  output_dir: ./output
  log_level: INFO
  profile: default

project:
  name: Meu Projeto
  description: Descrição do meu projeto
  path: ./src
  paths:
    source_code: ./src
    documentation: ./docs
    guides: ./docs/guides
    prompts: ./prompts
    diagrams: ./docs/diagrams

parser:
  exclude_dirs:
    - venv
    - node_modules
    - __pycache__
  exclude_files:
    - "*.pyc"
    - "*.min.js"
```

Para usar este arquivo de configuração em comandos:

```bash
insightforge analyze --project ./meu-projeto --config insightforge.yml
```

## Configuração Avançada

### Configurando a Interface Web

O InsightForge inclui uma interface web para gerenciamento de configurações. Para iniciá-la:

```bash
insightforge-web-ui
```

Por padrão, a interface estará disponível em http://localhost:5000.

Opções de inicialização:

```bash
# Especificar host e porta
insightforge-web-ui --host 0.0.0.0 --port 8080

# Usar arquivo de configuração específico
insightforge-web-ui --config ./meu-config.yml

# Ativar modo de debug
insightforge-web-ui --debug
```

### Configurando Perfis

Os perfis permitem manter diferentes configurações para diferentes projetos ou ambientes:

```yaml
general:
  profile: development  # Nome do perfil ativo

profiles:
  development:
    # Configurações específicas para desenvolvimento
    parser:
      exclude_dirs:
        - tests
  
  production:
    # Configurações específicas para produção
    parser:
      exclude_dirs:
        - tests
        - examples
```

Para alternar entre perfis:

```bash
insightforge analyze --project ./meu-projeto --profile production
```

### Segurança de Credenciais

O InsightForge armazena credenciais (tokens de API, senhas) de forma segura usando o módulo `keyring`, que integra-se com o gerenciador de senhas do sistema operacional.

As credenciais podem ser gerenciadas através da CLI:

```bash
# Adicionar um token
insightforge-config token --service jira --key api_token --value seu-token

# Listar tokens armazenados
insightforge-config token --list

# Remover um token
insightforge-config token --service jira --key api_token --delete
```

## Integrações

### Configurando Integração com Jira

A integração com Jira permite sincronização bidirecional entre issues do InsightForge e do Jira.

Configuração via CLI:

```bash
insightforge-config jira
```

Configuração manual no arquivo YAML:

```yaml
integrations:
  jira:
    url: https://sua-empresa.atlassian.net
    project_key: PROJ
    username: seu-email@exemplo.com
    api_token: <CREDENTIAL_PLACEHOLDER>  # Token armazenado no gerenciador de credenciais
    sync_settings:
      auto_create: true
      auto_update: true
      sync_interval: 30  # minutos
```

### Configurando Integração com GitHub

A integração com GitHub permite exportação automática de documentação para GitHub Pages e gerenciamento de issues.

Configuração via CLI:

```bash
insightforge-config github
```

Configuração manual no arquivo YAML:

```yaml
integrations:
  github:
    username: seu-usuario
    repository: usuario/repo
    branch: gh-pages
    token: <CREDENTIAL_PLACEHOLDER>  # Token armazenado no gerenciador de credenciais
```

### Configurando Integração com LLMs

O InsightForge pode integrar-se com diversos provedores LLM:

Configuração do Ollama (local):

```yaml
llm:
  providers:
    - name: Ollama
      type: ollama
      default: true
      models:
        - id: llama3
          display_name: Llama 3
          endpoint: http://localhost:11434
          default_for:
            - code_analysis
            - documentation
          parameters:
            temperature: 0.7
            max_tokens: 1000
```

Configuração do OpenAI:

```yaml
llm:
  providers:
    - name: OpenAI
      type: openai
      default: false
      models:
        - id: gpt-4
          display_name: GPT-4
          api_key: <CREDENTIAL_PLACEHOLDER>
          default_for:
            - query
            - chat
          parameters:
            temperature: 0.4
            max_tokens: 2000
```

## Resolução de Problemas

### Problemas Comuns

**Problema**: Erro ao analisar arquivos PHP
```
Solution: Instale as dependências opcionais para suporte a PHP:
pip install insightforge[php]
```

**Problema**: Erro de conexão com o Jira
```
Solution: Verifique se o URL do Jira e o token API estão corretos. 
Use insightforge-config jira para reconfigurar.
```

**Problema**: Erros de memória em projetos grandes
```
Solution: Aumente o limite de memória e use exclusões para filtrar arquivos irrelevantes:
parser:
  exclude_dirs:
    - node_modules
    - venv
    - dist
```

### Registro de Logs

Para ativar o modo de debug e obter mais informações de logs:

```bash
insightforge analyze --project ./meu-projeto --log-level DEBUG
```

Os logs são gravados no console e no arquivo `.insightforge/logs/insightforge.log`.

## Próximos Passos

Após a instalação e configuração, você pode começar a usar o InsightForge para analisar e documentar seus projetos:

```bash
# Analisar um projeto
insightforge analyze --project ./meu-projeto --output-dir ./documentacao

# Exportar documentação para GitHub Pages
insightforge github-export --docs-dir ./documentacao --project-name "Meu Projeto"

# Publicar documentação no GitHub Pages
insightforge github-publish --docs-dir ./documentacao --repo-url https://github.com/usuario/repo --project-name "Meu Projeto" --setup-actions
```

Para ajuda com comandos específicos:

```bash
insightforge --help
insightforge analyze --help
```

Para mais informações, consulte a [Documentação completa](https://seu-usuario.github.io/insight_forge/).

---

## Apêndice: Dependências

O InsightForge depende dos seguintes pacotes Python:

- **Principais**: pyyaml, jinja2, rich
- **Web**: flask, werkzeug
- **Segurança**: cryptography, keyring
- **Jira**: requests, atlassian-python-api
- **GitHub**: pygithub, requests
- **Webscraping**: playwright, beautifulsoup4
- **LLM**: requests, numpy
- **Análise de Código**: ast, phpparser (opcional), esprima-python (opcional)

Para instalar todas as dependências:

```bash
pip install insightforge[all]
```