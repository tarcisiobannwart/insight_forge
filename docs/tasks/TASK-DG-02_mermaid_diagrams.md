# TASK-DG-02: Geração de Diagramas com Mermaid

## Descrição
Implementar a geração automática de diagramas usando a sintaxe Mermaid para melhorar a compreensão visual da arquitetura e estrutura do código. Os diagramas serão incorporados nos arquivos Markdown e representarão classes, pacotes e suas relações.

## Detalhes
- **Prioridade**: Média
- **Estimativa**: 4 dias
- **Épico**: [EP-002](../epics/EP-002_documentation_generation.md)
- **Issue**: [ISSUE-003](../issues/ISSUE-003_mermaid_diagrams.md)
- **Responsável**: InsightForge Team
- **Status**: Concluído

## Requisitos

### Funcionais
- O sistema deve gerar diagramas de classe usando sintaxe Mermaid
- O sistema deve gerar diagramas de pacotes/módulos
- Os diagramas devem mostrar relações entre classes e módulos
- Deve ser possível configurar o nível de detalhe dos diagramas
- Diagramas devem ser incluídos nos arquivos Markdown gerados

### Técnicos
- Os diagramas devem usar a sintaxe Mermaid correta e verificada
- Deve haver mecanismos para lidar com diagramas muito grandes
- O código deve ter cobertura de testes de pelo menos 90%
- Os diagramas devem ser renderizáveis em GitHub, GitLab e outras plataformas

## Subtarefas

### 1. Implementar diagrama de classes
- [x] Criar gerador de sintaxe Mermaid para diagrama de classes
- [x] Incluir herança e relações entre classes
- [x] Mostrar métodos e atributos principais
- [x] Implementar filtragem para reduzir complexidade
- [x] Adicionar links dos diagramas para a documentação detalhada

### 2. Implementar diagrama de pacotes/módulos
- [x] Criar gerador de diagrama de pacotes usando Mermaid
- [x] Mostrar dependências entre módulos
- [x] Implementar agrupamento de módulos relacionados
- [x] Adicionar métricas de acoplamento nos diagramas
- [x] Criar visualização hierárquica para grandes projetos

### 3. Implementar diagramas de sequência
- [x] Identificar fluxos de chamada entre métodos
- [x] Gerar diagramas de sequência para cenários principais
- [x] Extrair diagramas de sequência de docstrings específicas
- [x] Criar diagramas para casos de uso principais
- [x] Limitar profundidade de chamadas para manter diagramas legíveis

### 4. Integrar com o sistema de documentação
- [x] Modificar DocGenerator para incluir diagramas
- [x] Adicionar opções de configuração para diagramas
- [x] Implementar mecanismos de particionamento para diagramas grandes
- [x] Criar índice de diagramas disponíveis
- [x] Adicionar links entre diagramas e código

## Abordagem Técnica

### Mermaid Syntax
Mermaid é uma linguagem baseada em JavaScript para criação de diagramas a partir de texto. A sintaxe básica para um diagrama de classe é:

```
classDiagram
    Class01 <|-- AveryLongClass : extends
    Class03 *-- Class04 : contains
    Class05 o-- Class06 : aggregation
    Class07 .. Class08 : association
    Class09 --> C2 : dependência
    
    class Class01 {
        +String publicField
        -int privateField
        #method(Type): Type
    }
```

### Diagramas de Classe
Para gerar diagramas de classe, vamos:
1. Extrair classes e suas relações do resultado do CodeParser
2. Gerar a sintaxe Mermaid apropriada
3. Implementar técnicas de filtragem para classes muito complexas:
   - Mostrar apenas métodos públicos
   - Limitar o número de métodos mostrados
   - Agrupar classes por pacote
   - Usar cores para distinguir tipos de classes

### Diagramas de Módulos
Para módulos, criaremos um diagrama de pacotes:

```
graph TD
    A[Core Module] --> B[Utils Module]
    A --> C[Database Module]
    B --> D[External API Module]
    C --> D
```

Usaremos informações de importação para determinar dependências entre módulos.

### Estratégias para Diagramas Grandes
Diagramas muito grandes podem ser difíceis de ler. Implementaremos:
1. Particionamento automático em subdiagramas
2. Visualização em diferentes níveis de detalhes
3. Agrupamento de componentes relacionados
4. Filtragem configurable de elementos
5. Geração de links navegáveis entre subdiagramas

## Critérios de Aceitação
- ✓ Diagramas de classe são gerados corretamente para todas as classes
- ✓ Herança e relações entre classes são mostradas corretamente
- ✓ Diagrama de pacotes mostra corretamente dependências entre módulos
- ✓ Diagramas são incluídos nos arquivos Markdown gerados
- ✓ A sintaxe Mermaid gerada é válida e renderizável
- ✓ Diagramas grandes são divididos ou filtrados para manter legibilidade
- ✓ Os diagramas têm links para a documentação detalhada
- ✓ O código tem cobertura de testes de pelo menos 90%

## Impacto
A adição de diagramas visuais melhorará significativamente a compreensão da estrutura do código, especialmente para novos membros da equipe ou para sistemas complexos. Diagramas visuais facilitam a comunicação entre equipes técnicas e não técnicas.

## Riscos
- Projetos muito grandes podem gerar diagramas excessivamente complexos
- Diferentes convenções de código podem afetar a qualidade dos diagramas
- A geração de diagramas pode impactar o desempenho para projetos muito grandes

## Referências
- [Mermaid Official Documentation](https://mermaid-js.github.io/mermaid/#/)
- [Class Diagram Syntax](https://mermaid-js.github.io/mermaid/#/classDiagram)
- [Package Diagram Best Practices](https://www.uml-diagrams.org/package-diagrams.html)