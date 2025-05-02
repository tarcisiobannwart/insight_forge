---
layout: default
title: Contribuindo para o InsightForge
---

# Contribuindo para o InsightForge

Obrigado pelo seu interesse em contribuir para o InsightForge! Este documento fornece orientações sobre como você pode ajudar a melhorar este projeto.

## Código de Conduta

Ao participar deste projeto, você concorda em manter um ambiente respeitoso e colaborativo. Pedimos que todos os colaboradores sejam respeitosos, inclusivos e considerem diferentes perspectivas.

## Como Contribuir

### Reportando Bugs

Se você encontrar um bug, por favor, crie uma issue no GitHub com os seguintes detalhes:

1. Um título claro e descritivo
2. Passos para reproduzir o problema
3. Comportamento esperado vs. comportamento atual
4. Ambiente (sistema operacional, versão do Python, etc.)
5. Quaisquer logs ou mensagens de erro relevantes

### Sugerindo Melhorias

Se você tem uma ideia para melhorar o InsightForge, sinta-se à vontade para criar uma issue no GitHub:

1. Descreva claramente a melhoria que você gostaria de ver
2. Explique por que isso seria valioso para o projeto
3. Se possível, forneça exemplos ou casos de uso

### Pull Requests

1. Fork o repositório
2. Crie uma nova branch para sua feature ou bugfix: `git checkout -b feature/nova-feature` ou `git checkout -b fix/bug-fix`
3. Faça suas alterações e certifique-se de que o código funciona
4. Adicione testes para suas alterações
5. Execute os testes existentes para garantir que suas alterações não quebrem nada: `pytest`
6. Envie um pull request

## Padrões de Código

- Siga o estilo PEP 8 para código Python
- Escreva docstrings no formato Google Python Style
- Adicione comentários quando o código não for auto-explicativo
- Escreva testes para novas funcionalidades

## Estrutura do Projeto

```
insightforge/
├── config/                  # Gerenciamento de configuração
├── reverse_engineering/     # Componentes de engenharia reversa
├── llm/                     # Integração com modelos de linguagem
├── exporters/               # Exportadores de documentação
└── main.py                  # Ponto de entrada da CLI
```

## Adicionando Novos Recursos

### Adicionando Suporte para Nova Linguagem

1. Crie um novo arquivo em `reverse_engineering/` com o nome da linguagem (por exemplo, `ruby_parser.py`)
2. Implemente a classe parser que estende a classe base `CodeParser`
3. Implemente os métodos necessários para análise de código
4. Registre o novo parser no `CodeParser` principal

### Adicionando Novo Exportador

1. Crie um novo arquivo em `exporters/` (por exemplo, `confluence_exporter.py`)
2. Implemente a classe de exportador com métodos para exportar e publicar
3. Integre o novo exportador na CLI principal

## Ambiente de Desenvolvimento

Para configurar seu ambiente de desenvolvimento:

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/insight_forge.git
cd insight_forge

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências de desenvolvimento
pip install -e ".[dev]"
```

## Testes

O InsightForge usa pytest para testes. Para executar os testes:

```bash
# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=insightforge

# Executar testes específicos
pytest tests/reverse_engineering/test_code_parser.py
```

## Processo de Release

1. Atualize a versão em `setup.py`
2. Atualize o CHANGELOG.md
3. Crie um novo tag com a versão: `git tag v1.0.0`
4. Envie os commits e tags: `git push && git push --tags`
5. Uma nova release será criada automaticamente pelo GitHub Actions