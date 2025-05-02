# Use Case: UC-003 - Use Case Extraction from Code

## Description

O sistema deve extrair automaticamente casos de uso de docstrings e comentários do código, identificando padrões que indicam funcionalidades descritas pelos desenvolvedores.

## Actors

- Analista de Requisitos
- Desenvolvedor

## Preconditions

- Análise de código concluída com sucesso (UC-001)
- Código-fonte com docstrings ou comentários significativos

## Main Flow

1. O sistema analisa docstrings de classes e métodos
2. O sistema identifica padrões como "Use Case:", "UC:" em comentários
3. O sistema extrai o título e descrição do caso de uso
4. O sistema atribui um ID único ao caso de uso (UC-XXX)
5. O sistema associa o caso de uso à classe/método de origem
6. O sistema armazena os casos de uso extraídos
7. O sistema atualiza o arquivo de status mcp_status.json

## Alternative Flows

### Nenhum Caso de Uso Encontrado

1. O sistema não identifica padrões de caso de uso nos comentários
2. O sistema tenta gerar casos de uso com base na estrutura e nomes de métodos
3. Os casos de uso gerados são marcados como "inferidos"

## Postconditions

- Lista de casos de uso extraídos do código
- Mapeamento entre casos de uso e componentes do código
- Status de extração de casos de uso atualizado em mcp_status.json

## Business Rules

- BR-007: Casos de uso devem ter IDs únicos
- BR-008: Casos de uso devem ser rastreáveis ao código-fonte
- BR-009: Comentários com padrões específicos têm prioridade na extração

## Related User Stories

- US-005: Como analista, quero extrair casos de uso do código para validar requisitos
- US-006: Como PO, quero verificar se os requisitos estão implementados no código

## Source Code References

- UseCaseExtractor: insightforge/reverse_engineering/usecase_extractor.py:11
- _extract_from_docstring: insightforge/reverse_engineering/usecase_extractor.py:52