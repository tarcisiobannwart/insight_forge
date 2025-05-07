# InsightForge - Tarefas de Desenvolvimento Imediatas

Este documento lista as tarefas imediatas que precisam ser implementadas para avançar o projeto InsightForge para a próxima fase.

## Prioridades de Implementação

### 1. Ajustes no Code Parser

- [ ] **ID: T001** - Ajustar `PythonAstParser` para detectar relações de herança entre classes
  - Identificar classes base a partir da definição da classe
  - Armazenar referências à classe pai na estrutura de dados
  - Atualizar representação `to_dict()` para incluir informações de herança

- [ ] **ID: T002** - Implementar detecção de imports e dependências entre módulos
  - Analisar statements de import
  - Construir grafo de dependências entre arquivos
  - Identificar dependências externas vs internas

- [ ] **ID: T003** - Adicionar detecção de variáveis globais e constantes
  - Identificar atribuições no nível do módulo
  - Detectar padrões de constantes (ALL_CAPS)
  - Incluir informações de tipo quando disponíveis via anotações

- [ ] **ID: T004** - Corrigir problemas de análise em arquivos com sintaxe complexa
  - Melhorar tratamento de erros durante o parsing
  - Implementar fallback para arquivos com erros de sintaxe
  - Adicionar logging detalhado de problemas encontrados

### 2. Melhorias no Doc Generator

- [ ] **ID: T005** - Implementar sistema de templates personalizáveis
  - Criar mecanismo de templates baseado em Jinja2
  - Permitir override de templates via diretório de configuração
  - Adicionar parâmetros para customização de saída

- [ ] **ID: T006** - Adicionar geração de diagramas
  - Implementar geração de diagramas de classe usando sintaxe Mermaid
  - Criar diagrama de dependências entre módulos
  - Gerar diagrama de componentes do sistema analisado

- [ ] **ID: T007** - Melhorar navegabilidade da documentação
  - Criar índice principal com links para todas as seções
  - Implementar breadcrumbs em cada documento
  - Adicionar links "Anterior/Próximo" para navegação sequencial

- [ ] **ID: T008** - Implementar geração de tabela de rastreabilidade
  - Criar matriz de rastreabilidade entre casos de uso, classes e métodos
  - Implementar tabela de mapeamento entre regras de negócio e código
  - Gerar visualização de cobertura de requisitos

### 3. Implementação de Business Rules Extractor

- [ ] **ID: T009** - Criar estrutura base para o extrator de regras de negócio
  - Definir classes para representação de regras de negócio
  - Implementar mecanismo de detecção baseado em blocos if/else
  - Criar template para documentação de regras de negócio

- [ ] **ID: T010** - Implementar detecção de validações em código
  - Identificar blocos de validação em métodos
  - Extrair mensagens de erro como descrições de regras
  - Mapear validações para regras de negócio específicas

- [ ] **ID: T011** - Adicionar extração de regras de comentários
  - Implementar detecção de padrões como "Rule:", "BR:" em comentários
  - Extrair descrições de regras de docstrings
  - Associar regras descritas a implementações de código

### 4. Testes e Validação

- [ ] **ID: T012** - Implementar testes unitários para Code Parser
  - Criar testes para classes `CodeParser` e `PythonAstParser`
  - Adicionar casos de teste para diferentes estruturas de código
  - Implementar verificações de cobertura de código

- [ ] **ID: T013** - Implementar testes unitários para Doc Generator
  - Criar testes para classe `DocGenerator`
  - Testar diferentes formatos de entrada e saída
  - Validar estrutura dos documentos gerados

- [ ] **ID: T014** - Adicionar testes de integração para fluxo completo
  - Criar projetos de teste com diferentes estruturas
  - Implementar validação end-to-end do pipeline
  - Adicionar cases para cenários de erro e recuperação

### 5. Ingestão e Configuração

- [ ] **ID: T015** - Implementar configuração via arquivo YAML
  - Criar estrutura para configuração via arquivo
  - Suportar parâmetros para todos os componentes
  - Implementar validação de configuração

- [ ] **ID: T016** - Adicionar ingestão de documentação existente
  - Implementar parser básico para arquivos Markdown
  - Criar mecanismo para mesclar informações existentes com novas
  - Preservar seções personalizadas durante regeneração

## Próximas Etapas

Após a conclusão das tarefas acima, o foco será:

1. Expandir suporte para análise de JavaScript/TypeScript
2. Implementar a integração com Ollama para processamento local
3. Desenvolver análise incremental baseada em git diff

## Estimativas

| Grupo de Tarefas | Estimativa (dias) | Prioridade |
|------------------|-------------------|------------|
| Code Parser      | 5                 | Alta       |
| Doc Generator    | 4                 | Alta       |
| Business Rules   | 3                 | Média      |
| Testes           | 4                 | Alta       |
| Ingestão         | 2                 | Baixa      |

Total estimado: 18 dias de desenvolvimento