# User Story: US-001 - Análise Automática de Código Python

## Story

**Como um** desenvolvedor ou analista técnico

**Eu quero** analisar automaticamente a estrutura de um projeto Python

**Para que** eu possa compreender rapidamente sua arquitetura sem ler todo o código manualmente

## Acceptance Criteria

- [ ] O sistema deve encontrar todos os arquivos Python em um diretório e subdiretórios
- [ ] O sistema deve extrair todas as classes, métodos e funções dos arquivos Python
- [ ] O sistema deve preservar docstrings e comentários relevantes
- [ ] O sistema deve identificar parâmetros de métodos e funções
- [ ] O sistema deve armazenar a linha onde cada elemento foi encontrado para referência
- [ ] O sistema deve lidar com erros de sintaxe sem falhar completamente
- [ ] O resultado deve ser armazenado em estrutura de dados facilmente manipulável

## Story Points

5

## Priority

Must Have

## Related Use Cases

- UC-001: Automated Code Analysis

## Implemented In

- CodeParser: insightforge/reverse_engineering/code_parser.py:120
- PythonAstParser: insightforge/reverse_engineering/code_parser.py:70

## Notes

Esta é a funcionalidade central do sistema, que permitirá todas as outras funcionalidades. A primeira versão foca apenas em Python, mas futuras versões devem expandir para outras linguagens.