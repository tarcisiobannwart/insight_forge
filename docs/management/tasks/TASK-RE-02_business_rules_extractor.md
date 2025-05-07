# TASK-RE-02: Implementar Extrator de Regras de Negócio

## Descrição
Criar um novo módulo para extrair automaticamente regras de negócio do código-fonte. As regras de negócio são restrições, validações e comportamentos que refletem os requisitos do domínio, geralmente implementados como validações, verificações condicionais e documentados em comentários.

## Detalhes
- **Prioridade**: Alta
- **Estimativa**: 4 dias
- **Épico**: [EP-003](../epics/EP-003_requirements_extraction.md)
- **Issue**: [ISSUE-002](../issues/ISSUE-002_business_rules_extractor.md)
- **Responsável**: Não atribuído
- **Status**: Pendente

## Requisitos

### Funcionais
- O sistema deve identificar regras de negócio explícitas em comentários
- O sistema deve extrair regras implícitas de validações e condicionais
- Cada regra deve ter um ID único (BR-XXX)
- As regras devem ser classificadas por tipo e severidade
- As regras devem ser associadas a componentes específicos do código

### Técnicos
- O extrator deve trabalhar com os dados produzidos pelo CodeParser
- O desempenho deve ser O(n) em relação ao tamanho do código
- A precisão da extração deve ser maior que 80%
- O código deve ter cobertura de testes de pelo menos 90%

## Subtarefas

### 1. Criar framework para regras de negócio
- [ ] Definir estrutura de dados para representar regras
- [ ] Criar sistema de geração de IDs únicos para regras (BR-XXX)
- [ ] Implementar serialização/deserialização de regras
- [ ] Criar template para documentação de regras
- [ ] Implementar rastreabilidade entre regras e código

### 2. Detectar regras em validações
- [ ] Identificar validações em parâmetros de entrada
- [ ] Analisar condicionais (if/else) para regras de negócio
- [ ] Extrair mensagens de erro como descrições de regras
- [ ] Identificar invariantes em loops e condicionais
- [ ] Detectar regras em anotações/decoradores

### 3. Detectar regras em comentários
- [ ] Implementar parsing de comentários para padrões de regras
- [ ] Extrair regras de docstrings com formato específico
- [ ] Detectar descrições de restrições em comentários
- [ ] Associar comentários de regras ao código relacionado
- [ ] Implementar agrupamento de regras relacionadas

### 4. Integrar com sistema de documentação
- [ ] Criar modelo de documento para regras de negócio
- [ ] Implementar geração de documentação de regras
- [ ] Adicionar links bidirecionais entre regras e código
- [ ] Criar índice de regras de negócio
- [ ] Implementar visualização de dependências entre regras

## Abordagem Técnica

### Estrutura de Dados
Precisamos de uma estrutura robusta para representar regras de negócio:

```python
@dataclass
class BusinessRule:
    id: str                 # ID único (BR-XXX)
    name: str               # Nome descritivo
    description: str        # Descrição completa
    type: str               # Tipo de regra (validação, cálculo, processo, etc.)
    severity: str           # Importância (crítica, alta, média, baixa)
    source: str             # Fonte (código, comentário, inferido)
    file_path: str          # Arquivo onde foi encontrada
    line_number: int        # Linha onde foi encontrada
    code_component: str     # Componente relacionado (classe/método)
    related_rules: List[str] # IDs de regras relacionadas
```

### Detecção em Validações
Para extrair regras de validações, vamos analisar:

1. Blocos condicionais: 
   ```python
   if user.age < 18:
       raise InvalidAgeError("User must be 18 or older")
   ```

2. Expressões de validação:
   ```python
   assert price > 0, "Price must be positive"
   ```

3. Decoradores de validação:
   ```python
   @validate_input
   def create_user(username, email):
       # ...
   ```

As mensagens de erro são especialmente úteis, pois geralmente descrevem a regra de negócio violada.

### Detecção em Comentários
Procuraremos por padrões em comentários:

1. Padrões explícitos:
   ```python
   # Business Rule: Users cannot delete their account if they have active subscriptions
   ```

2. Docstrings com seções específicas:
   ```python
   """
   ...
   Business Rules:
       - BR-001: Email must be unique
       - BR-002: Username must be alphanumeric
   """
   ```

### Classificação de Regras
Categorizaremos as regras por tipo:
- **Validação**: Regras que validam dados
- **Cálculo**: Regras que definem cálculos específicos
- **Processo**: Regras que definem fluxos de processo
- **Restrição**: Limitações no comportamento do sistema
- **Derivação**: Regras que definem como valores são derivados

## Critérios de Aceitação
- ✅ O sistema identifica regras de negócio explícitas em comentários
- ✅ Regras implícitas em validações são detectadas quando possível
- ✅ Cada regra tem um ID único (BR-XXX)
- ✅ Regras são classificadas por tipo e severidade
- ✅ Regras são associadas a classes/métodos relevantes
- ✅ A documentação gerada lista todas as regras identificadas
- ✅ Existe rastreabilidade entre regras e implementação
- ✅ O sistema tem cobertura de testes de pelo menos 90%

## Impacto
A implementação desse extrator de regras de negócio permitirá:
1. Melhor compreensão das regras de domínio implementadas no código
2. Facilitar a validação de que todas as regras de negócio estão implementadas
3. Melhorar a manutenibilidade do sistema através de documentação clara
4. Facilitar a transferência de conhecimento entre equipes

## Riscos
- Dependência da qualidade dos comentários e nomes no código
- Falsos positivos em validações técnicas vs. regras de negócio
- Dificuldade em detectar regras complexas ou compostas

## Referências
- [Domain-Driven Design concepts](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Business Rules Extraction techniques](https://www.sciencedirect.com/science/article/pii/S0164121216301030)