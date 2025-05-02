# InsightForge - Documentação do MCP

## 🧠 Visão Geral do MCP (Multi-Component Process)
O MCP do InsightForge é o núcleo orquestrador que coordena a execução de múltiplos módulos responsáveis pela análise, documentação e alimentação de modelos de linguagem com base no código-fonte de um projeto.

---

## 🔄 Fluxo de Execução

```
1. Receber caminho do projeto (--project)
2. Executar análise de código
3. Gerar documentação em Markdown
4. Extrair Casos de Uso e User Stories
5. Construir regras de negócio e mapeamento de dependências
6. Alimentar o Ollama com o conhecimento extraído
```

---

## 📁 Finalidade da Pasta `/docs`

A pasta `/docs` do InsightForge **não armazena documentação de sistemas analisados**.

Ela serve exclusivamente como:

> **📘 Um exemplo de estrutura de documentação reversa esperada**

Ou seja, seu conteúdo demonstra o formato ideal que será gerado automaticamente dentro de cada projeto analisado. Ela funciona como **referência e guia de padronização**.

Toda documentação real será gerada em tempo de execução na pasta `docs/` dentro do diretório do projeto analisado.

---

## 📁 Estrutura Demonstrativa de Documentação Reversa (Exemplo)

```
/docs/                         ← Exemplo base de estrutura esperada
├── overview/
├── business_rules/
├── usecases/
├── userstories/
├── project_management/
├── architecture/
├── api_reference/
├── traceability/
├── guidelines/
├── manuals/
│   └── mcp_user_manual.md
├── internal/
│   ├── mcp.md
│   └── mcp_status.json
```

> Essa estrutura não será replicada em produção. Ela existe apenas para demonstrar como a documentação final de engenharia reversa deve ser organizada em cada sistema analisado.

---

## 📁 Local Correto da Documentação Final

A documentação gerada para um sistema será sempre armazenada em:

```
<projeto-analisado>/docs/
├── overview/
├── usecases/
├── userstories/
├── business_rules/
├── manual/
│   └── user_manual.md
├── ...
```

---

## 📊 Arquivo de Controle de Execução

Arquivo: `/docs/internal/mcp_status.json`

```json
{
  "project": "caminho/para/projeto",
  "steps": {
    "code_analysis": true,
    "doc_generation": true,
    "usecase_extraction": true,
    "backlog_generation": true,
    "llm_ingestion": true
  },
  "generated_at": "2025-05-02T22:00:00Z"
}
```

---

## 🔌 Integrações Futuras

| Recurso                  | Descrição                                    |
|-------------------------|----------------------------------------------|
| Confluence ingestion     | Parser da API Confluence (OAuth/token)       |
| Git diff incremental     | Detectar alterações desde último commit      |
| Exportação Jira/Trello   | Criar issues diretamente via REST API        |
| Fine-tuning com Ollama   | Pipeline de reentrenamento local             |
| Auto-validação CI/CD     | Bloquear PRs sem documentação atualizada     |

---

## 🔗 Rastreabilidade

Tabela de rastreabilidade UC ↔ BR ↔ US ↔ código:

| UC     | BR       | US       | Código            | Teste             |
|--------|----------|----------|-------------------|-------------------|
| UC-001 | BR-001   | US-001   | `AuthController`  | `test_login()`    |
| UC-002 | BR-002   | US-002   | `PasswordService` | `test_forgot()`   |

---

## ✅ Arquivos MCP Planejados

- `mcp.py` – Executa todos os módulos em ordem lógica
- `mcp_status.json` – Representa o status atual da execução

Toda essa estrutura será mantida como exemplo e documentação de referência do próprio InsightForge.
