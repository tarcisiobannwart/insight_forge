# Épico: EP-004 - Integração com Modelos de Linguagem

## Descrição
Como usuário técnico ou não-técnico, quero consultar um assistente inteligente que entenda o código-fonte do projeto para obter respostas sobre funcionalidades, estrutura e comportamento do sistema através de perguntas em linguagem natural.

## Objetivo de Negócio
Democratizar o acesso ao conhecimento técnico do sistema, permitindo que todos os stakeholders (técnicos e não-técnicos) possam obter informações sobre o projeto sem depender de especialistas ou ler código.

## User Stories Relacionadas
- [US-005](../userstories/US-005_llm_integration.md): Integração com Modelos de Linguagem
- US-024: Cliente Ollama para Processamento Local
- US-025: Sistema de Embeddings para Pesquisa Semântica
- US-026: Interface de Perguntas e Respostas sobre o Código
- US-027: Geração de Sugestões de Melhoria de Código
- US-028: Geração Automática de Testes (futura)
- US-029: Explicação de Algoritmos Complexos (futura)

## Critérios de Aceitação de Alto Nível
- Sistema deve alimentar modelos LLM com conhecimento extraído do código
- Usuários devem poder fazer perguntas em linguagem natural sobre o sistema
- Respostas devem ser precisas e referenciarem componentes específicos do código
- Deve funcionar offline, sem necessidade de conexão à internet
- Interface deve ser acessível via CLI e futuramente via API
- Deve suportar perguntas sobre requisitos, implementação e arquitetura

## Métricas de Sucesso
- 85% de precisão nas respostas sobre estrutura de código
- 75% de precisão em perguntas sobre comportamento funcional
- Tempo de resposta médio inferior a 3 segundos
- Redução de 50% na necessidade de consultar especialistas

## Riscos e Dependências
- Qualidade do modelo LLM impacta diretamente a qualidade das respostas
- Processamento local pode exigir recursos computacionais significativos
- Pode ter dificuldade com código muito complexo ou mal documentado

## Status
- **Estado atual**: Planejado
- **Progresso**: 0%
- **Próximos passos**: Implementar cliente Ollama e sistema básico de embeddings

## Casos de Uso Associados
- UC-004: Consulta Inteligente sobre o Código (a ser implementado)