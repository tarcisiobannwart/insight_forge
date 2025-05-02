# Prompt para Iniciar o Desenvolvimento do Projeto InsightForge

## 🧠 Visão Geral

Estamos iniciando o desenvolvimento do **InsightForge**, uma ferramenta de engenharia reversa automatizada que:

- Analisa código-fonte de projetos (ex: Python, PHP, JS)
- Gera documentação técnica em Markdown seguindo um padrão definido
- Alimenta um modelo LLM local (ex: Claude ou Ollama) com o conhecimento extraído
- Organiza artefatos como Casos de Uso, User Stories, Regras de Negócio, Épicos e Tarefas
- Conecta entradas (como PDF, DOCX ou Confluence) à geração automática de documentos e backlog

---

## 🎯 Objetivo deste Ciclo

Iniciar a implementação da **estrutura base do InsightForge**, composta por:

1. Arquivo `main.py` — ponto de entrada do CLI
2. Módulo `reverse_engineering/` com `code_parser.py`, `doc_generator.py`, etc.
3. Diretório `/docs/` com estrutura exemplo de saída
4. Suporte à leitura de Markdown (`InsightForge-MCP-Documentacao.md`) como referência padrão

---

## 📁 Estrutura Inicial do Projeto

```
insightforge/
├── main.py
├── reverse_engineering/
│   ├── code_parser.py
│   ├── doc_generator.py
│   ├── usecase_extractor.py
│   ├── backlog_builder.py
│   └── utils.py
├── ingestion/
│   ├── pdf_reader.py
│   ├── word_reader.py
│   └── confluence_parser.py
├── ollama/
│   ├── ollama_client.py
│   └── embedder.py
├── tests/
├── docs/                      ← pasta de referência (não documentação gerada)
│   └── internal/
│       └── mcp.md
├── manuals/
│   └── mcp_user_manual.md
└── requirements.txt
```

---

## ✅ Tarefas para o primeiro commit

1. Criar estrutura de diretórios acima
2. Implementar `main.py` com entrada `--project <caminho>`
3. Implementar esqueleto de `code_parser.py` com detecção de classes e funções em `.py`
4. Criar template Markdown base em `/docs/` para referência futura
5. Criar `mcp_status.json` e `mcp.md` explicando o fluxo
6. Criar `requirements.txt` com dependências mínimas (`rich`, `markdown`, etc.)

---

## 🧱 Regras de Design

- Código modular e coeso por responsabilidade
- Tipagem forte (`mypy` clean)
- Testes unitários por módulo (iniciar com `pytest`)
- Compatível com Python 3.10+

---

## 📦 Resultado esperado

Um repositório funcional com estrutura mínima e modular, pronto para iterar nas próximas fases:
- Parsing de outras linguagens
- Geração completa de artefatos Markdown
- Integração com o modelo Claude local

---

## 🛠️ Instrução final

Inicie o desenvolvimento agora criando a estrutura e arquivos acima.

Ao finalizar, valide a execução com:

```bash
python main.py --project caminho/do/projeto
```
