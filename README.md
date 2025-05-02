# InsightForge

## Visão Geral

InsightForge é uma ferramenta de engenharia reversa automatizada que transforma código-fonte em documentação técnica estruturada, criando casos de uso, user stories e alimentando modelos de linguagem com o conhecimento extraído.

## 🚀 Recursos

- **Análise de Código**: Extração automática de classes, métodos, funções e suas relações
- **Documentação Markdown**: Geração de documentação técnica estruturada e navegável
- **Extração de Casos de Uso**: Identificação de funcionalidades a partir de comentários e código
- **Geração de Backlog**: Criação de user stories e épicos para planejamento ágil
- **Integração com LLM**: Alimentação de modelos como Ollama e Claude com o conhecimento do projeto

## 🛠️ Tecnologias

- Python 3.10+
- AST (Abstract Syntax Tree) para análise de código
- Markdown para geração de documentação
- Integração com modelos de linguagem local

## 📋 Requisitos

- Python 3.10 ou superior
- Dependências listadas em `requirements.txt`

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/insight_forge.git
cd insight_forge
```

2. Instale as dependências:
```bash
pip install -r insightforge/requirements.txt
```

## 📊 Uso

Análise básica de um projeto:

```bash
python main.py --project /caminho/do/seu/projeto
```

## 📁 Estrutura do Projeto

```
insightforge/
├── main.py                 # Ponto de entrada CLI
├── reverse_engineering/    # Módulos de análise e geração
│   ├── code_parser.py      # Analisador de código
│   ├── doc_generator.py    # Gerador de documentação
│   ├── usecase_extractor.py # Extrator de casos de uso
│   └── backlog_builder.py  # Construtor de backlog
├── ingestion/              # Módulos de ingestão de docs existentes
├── ollama/                 # Integração com modelos de linguagem
└── docs/                   # Templates e documentação interna
```

## 📝 Status do Projeto

Este projeto está em desenvolvimento ativo. Consulte o arquivo `docs/internal/mcp_status.json` para status detalhado.

## 🔮 Próximos Passos

- Suporte para mais linguagens além de Python
- Integração com sistemas de gerenciamento de projetos
- UI para visualização e navegação da documentação
- Análise incremental baseada em git diff

## 📄 Licença

[MIT](LICENSE)