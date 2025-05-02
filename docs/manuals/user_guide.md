# InsightForge - Guia do Usuário

## Introdução

InsightForge é uma ferramenta de engenharia reversa automatizada que analisa código-fonte de projetos para gerar documentação técnica estruturada, extrair casos de uso e criar backlog de produto. Este guia explica como utilizar o InsightForge em seus projetos.

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Pip (gerenciador de pacotes Python)

#### Dependências Opcionais

- **PHP**: biblioteca `phply` para análise de código PHP
  ```bash
  pip install phply
  ```

- **JavaScript/TypeScript**: Node.js e npm para análise de código JS/TS
  - [Instale Node.js e npm](https://nodejs.org/en/download/)
  - As dependências JavaScript serão instaladas automaticamente

### Passos para Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/insight_forge.git
   cd insight_forge
   ```

2. Instale as dependências:
   ```bash
   pip install -r insightforge/requirements.txt
   ```

## Uso Básico

### Analisar um Projeto

O comando básico para analisar um projeto é:

```bash
python main.py --project /caminho/do/seu/projeto
```

O InsightForge irá:
1. Analisar o código-fonte do projeto
2. Gerar documentação na pasta `/caminho/do/seu/projeto/docs/`
3. Criar um arquivo de status em `/caminho/do/seu/projeto/docs/internal/mcp_status.json`

### Opções de Linha de Comando

| Opção | Descrição |
|-------|-----------|
| `--project PATH` | Caminho para o diretório do projeto a ser analisado (obrigatório) |
| `--config PATH` | Caminho para arquivo de configuração YAML (opcional, futuro) |
| `--output PATH` | Caminho personalizado para saída (opcional, futuro) |
| `--skip-step STEP` | Pular uma etapa específica do processo (opcional, futuro) |
| `--verbose` | Exibir informações detalhadas durante o processamento (opcional, futuro) |

## Saída Gerada

Após a execução, o InsightForge gera a seguinte estrutura de documentação:

```
<project>/docs/
├── overview/              # Visão geral do projeto
│   └── README.md
├── classes/               # Documentação das classes
│   └── [ClassName].md
├── functions/             # Documentação das funções
│   └── [FunctionName].md
├── usecases/              # Casos de uso extraídos
│   └── UC-[ID].md
├── userstories/           # User stories geradas
│   └── US-[ID].md
├── business_rules/        # Regras de negócio (futuro)
│   └── BR-[ID].md
└── internal/              # Arquivos internos
    ├── mcp.md             # Descrição do processo MCP
    └── mcp_status.json    # Status da execução
```

### Arquivos Gerados

#### Documentação de Classes

Cada classe documentada inclui:
- Nome e descrição
- Métodos com parâmetros e retornos
- Localização no código (arquivo e linha)
- Relações com outras classes (futuro)

#### Documentação de Funções

Cada função documentada inclui:
- Nome e descrição
- Parâmetros e retornos
- Localização no código (arquivo e linha)
- Exemplos de uso (quando disponíveis nas docstrings)

#### Casos de Uso (UC)

Casos de uso extraídos incluem:
- Título e descrição
- Atores envolvidos (quando identificados)
- Fluxo principal e alternativo (quando identificado)
- Referências ao código-fonte

#### User Stories (US)

User stories geradas incluem:
- Formato "Como um X, eu quero Y, para que Z"
- Critérios de aceitação
- Referências aos casos de uso
- Referências ao código-fonte

## Melhores Práticas

### Para Obter Melhores Resultados

1. **Documente seu código:**
   - **Python**: Use docstrings para classes, métodos e funções
   - **PHP**: Use PHPDoc com @param, @return, etc.
   - **JavaScript/TypeScript**: Use JSDoc ou TSDoc
   - Inclua descrições, parâmetros e retornos
   - Adicione exemplos de uso quando relevante

2. **Indique casos de uso explicitamente:**
   - Use padrões como "Use Case: [descrição]" em docstrings
   - Documente fluxos alternativos com "Alternative Flow: [descrição]"

3. **Indique regras de negócio:**
   - Use padrões como "Business Rule: [descrição]" em comentários
   - Documente validações importantes

4. **Estrutura organizacional:**
   - Mantenha uma hierarquia lógica de módulos
   - Use namespaces e pacotes significativos
   - Separe claramente camadas de aplicação

## Exemplos

### Exemplos de Código Bem Documentado

#### Python

```python
class UserService:
    """
    Serviço para gerenciamento de usuários.
    
    Use Case: Autenticação de usuários no sistema
    Use Case: Gerenciamento de permissões de usuários
    
    Business Rule: Usuários inativos não podem fazer login
    Business Rule: Senhas devem ter pelo menos 8 caracteres
    """
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Autentica um usuário no sistema.
        
        Args:
            username: Nome de usuário
            password: Senha do usuário
            
        Returns:
            User: Objeto usuário se autenticação bem-sucedida
            None: Se autenticação falhar
            
        Raises:
            AccountLockedException: Se a conta estiver bloqueada
        """
        # Implementação
```

#### PHP

```php
/**
 * Serviço para gerenciamento de usuários.
 *
 * Use Case: Autenticação de usuários no sistema
 * Use Case: Gerenciamento de permissões de usuários
 *
 * Business Rule: Usuários inativos não podem fazer login
 * Business Rule: Senhas devem ter pelo menos 8 caracteres
 */
class UserService
{
    /**
     * Autentica um usuário no sistema.
     *
     * @param string $username Nome de usuário
     * @param string $password Senha do usuário
     * @return User|null Objeto usuário se autenticação bem-sucedida, null se falhar
     * @throws AccountLockedException Se a conta estiver bloqueada
     */
    public function authenticate($username, $password)
    {
        // Implementação
    }
}
```

#### JavaScript/TypeScript

```typescript
/**
 * Serviço para gerenciamento de usuários.
 *
 * Use Case: Autenticação de usuários no sistema
 * Use Case: Gerenciamento de permissões de usuários
 *
 * Business Rule: Usuários inativos não podem fazer login
 * Business Rule: Senhas devem ter pelo menos 8 caracteres
 */
class UserService {
    /**
     * Autentica um usuário no sistema.
     *
     * @param {string} username - Nome de usuário
     * @param {string} password - Senha do usuário
     * @returns {User|null} Objeto usuário se autenticação bem-sucedida, null se falhar
     * @throws {AccountLockedException} Se a conta estiver bloqueada
     */
    authenticate(username, password) {
        // Implementação
    }
}
```

## Solução de Problemas

### Problemas Comuns

#### O InsightForge não encontra meu código

- Verifique se o caminho fornecido está correto
- Verifique se você tem permissões de leitura para os arquivos
- Confirme que os arquivos têm a extensão correta:
  - Python: `.py`
  - PHP: `.php`
  - JavaScript: `.js`, `.jsx`
  - TypeScript: `.ts`, `.tsx`

#### A documentação gerada está incompleta

- Verifique se seus arquivos têm docstrings
- Examine o arquivo de log para erros de parsing
- Verifique se há erros de sintaxe no código

#### Erros durante a análise

- Verifique a versão do Python (requer 3.10+)
- Verifique se todas as dependências estão instaladas
- Para código PHP: confirme que a biblioteca phply está instalada
- Para código JavaScript/TypeScript: confirme que Node.js e npm estão instalados
- Examine mensagens de erro detalhadas no console

## Recursos Adicionais

- [GitHub do Projeto](https://github.com/seu-usuario/insight_forge)
- [Roadmap de Desenvolvimento](../project_management/roadmap.md)
- [Guia de Contribuição](../guidelines/contributing.md)