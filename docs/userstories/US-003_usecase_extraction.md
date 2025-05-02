# User Story: US-003 - Extração de Casos de Uso

## Story

**Como um** analista de requisitos ou product owner

**Eu quero** extrair casos de uso diretamente dos comentários e código-fonte

**Para que** eu possa validar que a implementação está alinhada com os requisitos originais

## Acceptance Criteria

- [ ] O sistema deve detectar padrões em docstrings que indicam casos de uso ("Use Case:", "UC:")
- [ ] Cada caso de uso identificado deve receber um ID único
- [ ] Os casos de uso extraídos devem incluir título, descrição e origem
- [ ] O sistema deve associar casos de uso às classes/métodos correspondentes
- [ ] Quando nenhum caso de uso é explicitamente documentado, o sistema deve inferir casos de uso da estrutura do código
- [ ] Os casos de uso extraídos devem ser exportados em formato Markdown
- [ ] Deve existir rastreabilidade bidirecional entre casos de uso e código-fonte

## Story Points

5

## Priority

Should Have

## Related Use Cases

- UC-003: Use Case Extraction from Code

## Implemented In

- UseCaseExtractor: insightforge/reverse_engineering/usecase_extractor.py:11
- _extract_from_docstring: insightforge/reverse_engineering/usecase_extractor.py:52

## Notes

Esta funcionalidade é especialmente útil para projetos legados ou sistemas onde a documentação de requisitos está desatualizada em relação ao código.