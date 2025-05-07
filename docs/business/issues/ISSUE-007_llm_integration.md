# ISSUE-007: Implementação de Integração LLM no InsightForge

## Descrição
Esta issue trata da implementação de recursos de Large Language Models (LLM) no InsightForge, permitindo consultas em linguagem natural sobre o código-fonte, compreensão semântica e outros recursos avançados de análise.

## Funcionalidades Implementadas

### 1. Integração com Ollama
- Criação de interface para comunicação com modelos locais via Ollama
- Suporte para geração de texto, chat e embeddings
- Design resiliente com tratamento de erros
- Customização de parâmetros como temperatura e tokens máximos

### 2. Sistema de Embeddings
- Implementação de armazenamento e busca por embeddings
- Suporte para embeddings de classes, funções, arquivos e documentação
- Pesquisa semântica por relevância
- Persistência de embeddings para uso entre sessões

### 3. Motor de Consulta em Linguagem Natural
- Interface para consultas sobre o código em linguagem natural
- Busca de trechos relevantes usando embeddings
- Geração de respostas contextualizadas
- Inclusão de referências às fontes utilizadas

### 4. Explicador de Código
- Funcionalidade para explicar trechos de código
- Identificação de padrões e fluxos
- Explicações em linguagem clara e acessível
- Suporte a múltiplas linguagens (Python, PHP, JavaScript/TypeScript)

### 5. Sugestão de Melhorias
- Analisador de código para sugerir melhorias
- Detecção de potenciais bugs ou problemas
- Sugestões de otimizações de performance
- Recomendações de boas práticas

### 6. Gerador de Documentação
- Geração automática de docstrings
- Documentação no estilo adequado para cada linguagem
- Descrição de parâmetros, retornos e exceções
- Exemplos de uso quando aplicável

## Impacto na Arquitetura
A implementação manteve a arquitetura modular existente, adicionando novos componentes:
- **llm/base.py**: Interface base para provedores LLM
- **llm/ollama.py**: Implementação da integração com Ollama
- **llm/embeddings.py**: Sistema de embeddings para busca semântica
- **llm/query.py**: Motor de consulta em linguagem natural

Modificações foram feitas nos seguintes componentes:
- **config_schema.py**: Atualizado para incluir configurações LLM
- **main.py**: Adicionados comandos de linha de comando para recursos LLM

## Requisitos
- Dependência opcional de **requests** para comunicação com a API Ollama
- Dependência opcional de **numpy** para cálculos de similaridade
- Sem alterações nos requisitos principais do sistema
- Ollama instalado localmente para execução completa das funcionalidades

## Status
✅ Completo

## Tarefas Relacionadas
- TASK-LLM-01: Implementar integração base com modelos LLM
- TASK-LLM-02: Criar sistema de embeddings para busca semântica
- TASK-LLM-03: Implementar motor de consulta em linguagem natural
- TASK-LLM-04: Desenvolver explicador de código
- TASK-LLM-05: Implementar sugestão de melhorias
- TASK-LLM-06: Criar gerador de documentação
- TASK-LLM-07: Escrever documentação para recursos LLM

## Referências
- [Ollama](https://ollama.ai/)
- [Embedding Models](https://platform.openai.com/docs/guides/embeddings)
- [Vector Search for Code](https://huggingface.co/blog/vector-search)
- [Mistral AI](https://mistral.ai/)
- [Llama 2](https://ai.meta.com/llama/)