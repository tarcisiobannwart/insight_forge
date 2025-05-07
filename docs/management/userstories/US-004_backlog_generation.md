# User Story: US-004 - Geração de Backlog de Produto

## Story

**Como um** gerente de produto ou scrum master

**Eu quero** gerar automaticamente um backlog de produto a partir do código e casos de uso

**Para que** eu possa planejar o desenvolvimento futuro com base no código existente

## Acceptance Criteria

- [ ] O sistema deve converter casos de uso em user stories
- [ ] As user stories devem seguir o formato "Como um X, eu quero Y, para que Z"
- [ ] O sistema deve gerar critérios de aceitação preliminares para cada user story
- [ ] User stories relacionadas devem ser agrupadas em épicos
- [ ] O sistema deve atribuir IDs únicos para user stories e épicos
- [ ] O backlog gerado deve ser exportado em formato Markdown
- [ ] Deve existir rastreabilidade entre user stories e casos de uso/código-fonte

## Story Points

8

## Priority

Should Have

## Related Use Cases

- UC-003: Use Case Extraction from Code

## Implemented In

- BacklogBuilder: insightforge/reverse_engineering/backlog_builder.py:121
- UserStory: insightforge/reverse_engineering/backlog_builder.py:9
- Epic: insightforge/reverse_engineering/backlog_builder.py:50

## Notes

A geração de backlog automatizada não substitui o refinamento manual, mas fornece um ponto de partida valioso, especialmente para projetos legados ou durante transições de equipe.