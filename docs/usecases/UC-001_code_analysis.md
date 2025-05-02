# Use Case: UC-001 - Automated Code Analysis

## Description

O sistema deve permitir a análise automatizada de código-fonte em Python, identificando classes, métodos, funções e suas relações.

## Actors

- Engenheiro de Documentação
- Desenvolvedor

## Preconditions

- Acesso ao código-fonte do projeto a ser analisado
- Código-fonte válido em Python (inicialmente)

## Main Flow

1. O usuário fornece o caminho do projeto via parâmetro --project
2. O sistema localiza todos os arquivos .py no diretório e subdiretórios
3. Para cada arquivo, o sistema extrai:
   - Classes (nome, docstring, linha)
   - Métodos (nome, parâmetros, docstring, linha)
   - Funções (nome, parâmetros, docstring, linha)
4. O sistema identifica relações entre os componentes
5. O sistema armazena os resultados em estrutura intermediária
6. O sistema atualiza o arquivo de status mcp_status.json

## Alternative Flows

### Arquivo com Erros de Sintaxe

1. O sistema detecta erro de sintaxe em arquivo Python
2. O sistema registra o erro e continua com os demais arquivos
3. O arquivo com erro é marcado como "não analisado" no relatório

### Projeto Vazio ou Sem Arquivos Python

1. O sistema não encontra arquivos Python para analisar
2. O sistema gera uma mensagem informando que nenhum arquivo foi encontrado
3. O processo termina sem criar documentação

## Postconditions

- Estrutura de dados contendo todas as classes, métodos e funções analisadas
- Status de análise registrado em mcp_status.json

## Business Rules

- BR-001: Toda classe deve ter seus métodos associados
- BR-002: Docstrings devem ser preservadas na análise
- BR-003: Parâmetros de métodos devem excluir 'self'

## Related User Stories

- US-001: Como desenvolvedor, quero visualizar todas as classes do meu código para entender sua estrutura
- US-002: Como analista, quero extrair métodos e funções para documentar a API

## Source Code References

- CodeParser: insightforge/reverse_engineering/code_parser.py:120
- PythonAstParser: insightforge/reverse_engineering/code_parser.py:70