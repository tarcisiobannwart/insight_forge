# InsightForge - Recursos de LLM

## Introdução

O InsightForge possui integração com modelos de linguagem de grande escala (LLMs) para melhorar a análise de código e fornecer funcionalidades avançadas como pesquisa semântica, explicação de código, e respostas a perguntas em linguagem natural sobre o código-fonte.

Este documento detalha os recursos de LLM disponíveis no InsightForge, como configurá-los e como utilizá-los para obter o máximo de produtividade na compreensão de código.

## Recursos Disponíveis

### 1. Integração com Ollama

O InsightForge integra-se com [Ollama](https://ollama.ai/) para executar modelos LLM localmente, oferecendo:

- Baixo tempo de resposta por não depender de serviços em nuvem
- Privacidade dos dados e código
- Suporte a múltiplos modelos (Mistral, Llama, etc.)
- Processamento econômico sem custos de API

### 2. Pesquisa Semântica de Código

Realize pesquisas de código baseadas em significado, não apenas texto literal:

- Pesquise por conceitos ou funcionalidades
- Encontre classes e funções com base em descrições
- Pesquisa multilíngue (Python, PHP, JavaScript/TypeScript)
- Resultados ordenados por relevância semântica

### 3. Resposta a Perguntas sobre o Código

Faça perguntas em linguagem natural sobre seu código e obtenha respostas baseadas no contexto:

- "Como funciona o sistema de autenticação neste projeto?"
- "Qual classe é responsável por processar pagamentos?"
- "Como os dados são persistidos no banco de dados?"
- "Como implementar uma nova funcionalidade específica?"

### 4. Explicação de Código

Obtenha explicações detalhadas de trechos de código:

- Descrição de alto nível do funcionamento
- Detalhamento de componentes-chave
- Fluxo de execução explicado
- Identificação de padrões de design utilizados

### 5. Sugestão de Melhorias

Receba sugestões para aprimorar seu código:

- Identificação de potenciais bugs
- Otimizações de desempenho
- Melhorias de legibilidade
- Sugestões baseadas em boas práticas

### 6. Geração de Documentação

Gere automaticamente docstrings e documentação:

- Docstrings para classes e funções
- Descrições de parâmetros e retornos
- Exemplos de uso
- Documentação no estilo de cada linguagem (PEP257, JSDoc, PHPDoc)

## Configuração

### Pré-requisitos

Para usar os recursos de LLM com Ollama:

1. Instale o [Ollama](https://ollama.ai/download) em sua máquina
2. Puxe um modelo compatível:
   ```bash
   ollama pull mistral
   # ou
   ollama pull llama2
   ```

### Configuração no InsightForge

Configure os recursos de LLM no arquivo de configuração:

```yaml
llm:
  provider: "ollama"  # Provedor de LLM (atualmente suporta "ollama")
  base_url: "http://localhost:11434"  # URL da API Ollama
  model: "mistral"  # Modelo a ser utilizado
  embeddings_model: "mistral"  # Modelo para geração de embeddings
  embedding_dir: ".embeddings"  # Diretório para armazenar embeddings
  timeout: 60  # Timeout em segundos para chamadas de API
```

## Uso

### Pesquisa Semântica

Pesquise no código usando a CLI:

```bash
python main.py --project /caminho/do/projeto --search "como os usuários são autenticados"
```

Resultados serão ordenados por relevância semântica, mostrando trechos de código e documentação relacionados.

### Consulta em Linguagem Natural

Faça perguntas sobre o código:

```bash
python main.py --project /caminho/do/projeto --ask "Como funciona o sistema de permissões?"
```

A resposta incluirá:
- Explicação baseada no código-fonte
- Referências a classes e funções relevantes
- Links para artefatos de código importantes

### Explicação de Código

Explique um trecho de código específico:

```bash
python main.py --explain --file /caminho/do/projeto/arquivo.py --start-line 10 --end-line 50
```

Ou forneça o código diretamente:

```bash
python main.py --explain-code "código a ser explicado"
```

### Sugestão de Melhorias

Obtenha sugestões para melhorar um arquivo:

```bash
python main.py --improve --file /caminho/do/projeto/arquivo.py
```

### Geração de Documentação

Gere docstrings para código sem documentação:

```bash
python main.py --generate-docs --file /caminho/do/projeto/arquivo.py
```

## Parâmetros Avançados

Você pode ajustar o comportamento dos modelos LLM:

```bash
python main.py --project /caminho/do/projeto --ask "Como funciona a autenticação?" \
  --temperature 0.3 \  # Menor temperatura = respostas mais determinísticas
  --max-tokens 1000 \  # Limite de tokens na resposta
  --model llama2       # Especifica o modelo a ser usado
```

## Embedddings e Persistência

O InsightForge armazena embeddings para acelerar pesquisas futuras:

- Os embeddings são armazenados em `.embeddings/` por padrão
- Embeddings são gerados durante a primeira análise
- Use `--rebuild-embeddings` para reconstruir embeddings após mudanças significativas no código

## Considerações de Performance

- Ollama requer GPU para melhor desempenho (mas funciona em CPU)
- Modelos maiores oferecem respostas melhores mas são mais lentos
- Use modelos 7B para laptops com recursos limitados
- Modelos 13B+ oferecem qualidade superior em máquinas mais potentes

## Modelos Recomendados

- **mistral**: Bom equilíbrio entre performance e qualidade
- **llama2**: Ótimo para explicações detalhadas
- **codellama**: Especializado em código e programação
- **nous-hermes**: Excelente para respostas técnicas precisas

## Suporte a Linguagens

Os recursos LLM suportam todas as linguagens reconhecidas pelo InsightForge:

- Python
- PHP
- JavaScript/TypeScript

## Limitações Atuais

- Respostas sobre bases de código muito grandes podem perder detalhes específicos
- A qualidade das respostas depende da documentação existente no código
- Modelos locais podem ter limitações de conhecimento comparados a serviços em nuvem
- Código altamente especializado ou específico de domínio pode ter respostas menos precisas