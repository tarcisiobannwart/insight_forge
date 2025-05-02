# Épico: EP-003 - Extração de Requisitos do Código

## Descrição
Como analista de requisitos ou product owner, quero extrair automaticamente casos de uso, regras de negócio e requisitos a partir do código-fonte para garantir que a documentação de requisitos esteja alinhada com a implementação atual e para facilitar a rastreabilidade bidirecional.

## Objetivo de Negócio
Manter uma sincronia constante entre requisitos e implementação, facilitando auditorias, garantindo conformidade e permitindo evolução controlada do sistema através de rastreabilidade precisa.

## User Stories Relacionadas
- [US-003](../userstories/US-003_usecase_extraction.md): Extração de Casos de Uso
- [US-004](../userstories/US-004_backlog_generation.md): Geração de Backlog de Produto
- US-019: Extração de Regras de Negócio
- US-020: Detecção de Atores e Cenários Alternativos
- US-021: Inferência de Pré e Pós-condições
- US-022: Matriz de Rastreabilidade Requisitos-Código
- US-023: Análise de Impacto de Mudanças (futura)

## Critérios de Aceitação de Alto Nível
- Sistema deve extrair casos de uso de docstrings e comentários de código
- Regras de negócio devem ser identificadas a partir de validações e comentários
- Requisitos extraídos devem ser mapeados para componentes específicos do código
- Deve gerar matriz de rastreabilidade bidirecional
- Casos de uso extraídos devem incluir atores e cenários quando possível
- Requisitos devem ser categorizados e organizados logicamente

## Métricas de Sucesso
- Detecção de pelo menos 80% dos casos de uso descritos em docstrings
- Extração de pelo menos 70% das regras de negócio implementadas
- Redução de 60% no esforço para manter rastreabilidade
- Tempo de atualização inferior a 5 minutos após alterações no código

## Riscos e Dependências
- Altamente dependente da qualidade das docstrings e comentários
- Pode ser desafiador inferir regras de negócio de código complexo
- Requer alguma padronização nos comentários para extração eficaz

## Status
- **Estado atual**: Em andamento
- **Progresso**: 25%
- **Próximos passos**: Implementar extrator de regras de negócio e melhorar detecção de cenários alternativos

## Casos de Uso Associados
- [UC-003](../usecases/UC-003_usecase_extraction.md): Use Case Extraction from Code