# Use Case: UC-002 - Markdown Documentation Generation

## Description

O sistema deve gerar automaticamente documentação em formato Markdown a partir do código analisado, seguindo uma estrutura padronizada.

## Actors

- Engenheiro de Documentação
- Desenvolvedor
- Product Owner

## Preconditions

- Análise de código concluída com sucesso (UC-001)
- Estrutura de dados com componentes do código disponível

## Main Flow

1. O sistema recebe a estrutura de dados com os componentes extraídos do código
2. O sistema cria os diretórios necessários para a documentação
3. O sistema gera arquivos Markdown para:
   - Visão geral do projeto
   - Documentação de classes
   - Documentação de funções
   - Casos de uso identificados
4. Cada documento segue um template padrão definido
5. Os documentos são armazenados na estrutura adequada
6. O sistema atualiza o arquivo de status mcp_status.json

## Alternative Flows

### Documentação Já Existente

1. O sistema detecta arquivos de documentação já existentes
2. O sistema pergunta se deve sobrescrever ou mesclar com os existentes
3. Caso opte por mesclar, o sistema preserva seções personalizadas

## Postconditions

- Conjunto completo de arquivos Markdown representando a documentação do projeto
- Links de navegação entre os documentos
- Status de geração de documentação atualizado em mcp_status.json

## Business Rules

- BR-004: A documentação deve seguir templates pré-definidos
- BR-005: A estrutura de diretórios deve ser mantida consistente
- BR-006: Docstrings devem ser convertidas para Markdown

## Related User Stories

- US-003: Como PM, quero documentação técnica automatizada para facilitar onboarding
- US-004: Como desenvolvedor, quero documentação de API gerada do código

## Source Code References

- DocGenerator: insightforge/reverse_engineering/doc_generator.py:12
- _generate_class_docs: insightforge/reverse_engineering/doc_generator.py:76