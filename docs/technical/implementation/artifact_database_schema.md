# Esquema de Banco de Dados para Artefatos do InsightForge

Este documento define a estrutura de dados necessária para implementar o sistema de rastreabilidade e integração de artefatos no InsightForge.

## Visão Geral

O banco de dados de artefatos armazenará todos os diferentes tipos de elementos produzidos e gerenciados pelo InsightForge, mantendo suas relações e possibilitando uma visão integrada do projeto. A estrutura é projetada para ser flexível, permitindo a adição de novos tipos de artefatos sem modificações significativas no esquema.

## Modelo Conceitual

![Modelo Conceitual](../diagrams/artifact_db_model.svg)

*Nota: O diagrama acima é uma representação conceitual. Em implementação, utilizaremos uma abordagem híbrida entre relacional e documentos.*

## Tabelas Principais

### artifacts

Armazena todos os artefatos do sistema, independente de seu tipo.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único do artefato |
| type | STRING | Tipo do artefato (code_class, user_story, use_case, etc.) |
| name | STRING | Nome/título do artefato |
| project_id | UUID | Referência ao projeto |
| status | STRING | Status do artefato (draft, active, deprecated, etc.) |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Data da última atualização |
| created_by | STRING | Usuário que criou o artefato |
| updated_by | STRING | Usuário que realizou a última atualização |
| version | INTEGER | Versão atual do artefato |
| content | JSON | Conteúdo específico do tipo de artefato |
| metadata | JSON | Metadados adicionais (depende do tipo) |

### artifact_links

Armazena os vínculos entre diferentes artefatos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único do vínculo |
| source_id | UUID | ID do artefato de origem |
| target_id | UUID | ID do artefato de destino |
| link_type | STRING | Tipo de relação (implements, depends_on, references, etc.) |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Data da última atualização |
| created_by | STRING | Usuário que criou o vínculo |
| metadata | JSON | Metadados adicionais sobre o vínculo |
| strength | FLOAT | Força da relação (0.0 a 1.0) |

### artifact_versions

Armazena o histórico de versões de cada artefato.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único do registro de versão |
| artifact_id | UUID | Referência ao artefato |
| version | INTEGER | Número da versão |
| content | JSON | Conteúdo do artefato nesta versão |
| metadata | JSON | Metadados nesta versão |
| created_at | TIMESTAMP | Data de criação da versão |
| created_by | STRING | Usuário que criou a versão |
| change_description | TEXT | Descrição das alterações nesta versão |

### projects

Armazena informações sobre os projetos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único do projeto |
| name | STRING | Nome do projeto |
| description | TEXT | Descrição do projeto |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Data da última atualização |
| settings | JSON | Configurações específicas do projeto |
| path | STRING | Caminho do projeto no sistema de arquivos |

### external_references

Armazena referências a sistemas externos (como Jira, GitHub, etc.)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único da referência externa |
| artifact_id | UUID | Referência ao artefato |
| system_type | STRING | Tipo de sistema externo (jira, github, etc.) |
| external_id | STRING | ID no sistema externo |
| url | STRING | URL para o item no sistema externo |
| sync_status | STRING | Status de sincronização |
| last_synced_at | TIMESTAMP | Data da última sincronização |
| metadata | JSON | Metadados adicionais da integração |

## Estruturas de Conteúdo por Tipo de Artefato

A seguir, detalhamos a estrutura esperada para o campo `content` de diferentes tipos de artefatos:

### code_class

```json
{
  "name": "CodeParser",
  "docstring": "Parses source code files and extracts structure.",
  "file_path": "/path/to/file.py",
  "line_number": 42,
  "base_classes": ["BaseParser"],
  "methods": [
    {
      "name": "parse",
      "docstring": "Parse the source code.",
      "parameters": ["file_path"],
      "return_type": "Dict",
      "line_number": 55
    }
  ],
  "attributes": [
    {
      "name": "project_path",
      "type": "str",
      "is_class_var": false
    }
  ]
}
```

### user_story

```json
{
  "id": "US-001",
  "title": "Login de Usuário",
  "description": "Como usuário, quero fazer login no sistema usando meu e-mail e senha para acessar minha conta.",
  "acceptance_criteria": [
    "Deve validar e-mail em formato correto",
    "Deve verificar senha com pelo menos 8 caracteres",
    "Deve bloquear conta após 3 tentativas incorretas"
  ],
  "priority": "high",
  "points": 5,
  "status": "implemented"
}
```

### use_case

```json
{
  "id": "UC-001",
  "title": "Autenticação de Usuário",
  "actor": "Usuário Final",
  "description": "Este caso de uso descreve o processo de autenticação do usuário no sistema.",
  "preconditions": [
    "Usuário deve estar cadastrado no sistema"
  ],
  "main_flow": [
    "Usuário navega até a página de login",
    "Usuário insere e-mail e senha",
    "Sistema valida as credenciais",
    "Sistema redireciona para a página inicial"
  ],
  "alternative_flows": [
    {
      "name": "Credenciais Inválidas",
      "steps": [
        "Sistema exibe mensagem de erro",
        "Usuário pode tentar novamente"
      ]
    }
  ],
  "postconditions": [
    "Usuário está autenticado no sistema"
  ]
}
```

### ui_screen

```json
{
  "name": "Login Screen",
  "url": "https://example.com/login",
  "screenshot_path": "/screenshots/login.png",
  "description": "Tela de login principal do sistema",
  "components": [
    {
      "type": "input",
      "name": "email",
      "label": "E-mail",
      "position": {"x": 150, "y": 200, "width": 300, "height": 40}
    },
    {
      "type": "input",
      "name": "password",
      "label": "Senha",
      "position": {"x": 150, "y": 260, "width": 300, "height": 40}
    },
    {
      "type": "button",
      "name": "login_button",
      "label": "Entrar",
      "position": {"x": 250, "y": 320, "width": 100, "height": 40}
    }
  ],
  "flow_links": [
    {
      "target": "Dashboard",
      "condition": "Credenciais válidas",
      "interaction": "Click on login_button"
    }
  ]
}
```

### business_rule

```json
{
  "id": "BR-001",
  "title": "Validação de Senha",
  "description": "Regras para validação de senha no sistema",
  "rules": [
    "Senha deve ter no mínimo 8 caracteres",
    "Senha deve conter pelo menos uma letra maiúscula",
    "Senha deve conter pelo menos um número",
    "Senha deve conter pelo menos um caractere especial"
  ],
  "implementation": {
    "files": ["auth/validators.py"],
    "function": "validate_password"
  }
}
```

## Índices

Para garantir performance adequada, recomendamos os seguintes índices:

1. `artifacts(id)` - Chave primária
2. `artifacts(project_id, type)` - Pesquisa por tipo em um projeto 
3. `artifacts(name)` - Pesquisa por nome
4. `artifact_links(source_id)` - Pesquisa de vínculos por origem
5. `artifact_links(target_id)` - Pesquisa de vínculos por destino
6. `artifact_links(source_id, target_id)` - Verificação de vínculos existentes
7. `artifact_versions(artifact_id, version)` - Pesquisa de versões específicas
8. `external_references(system_type, external_id)` - Pesquisa por referência externa

## Considerações de Implementação

### Opções de Armazenamento

Recomendamos as seguintes abordagens, dependendo do contexto:

1. **PostgreSQL com JSONB**
   - Ideal para equilíbrio entre estrutura e flexibilidade
   - Suporte a consultas dentro dos campos JSON
   - Transações ACID
   
2. **MongoDB**
   - Maior flexibilidade para esquemas variáveis
   - Boa performance para documentos grandes
   - Mais simples para prototipagem rápida

3. **Abordagem Híbrida com SQLite + JSON**
   - Mais leve para instalações locais
   - Facilidade de backup e portabilidade
   - Menor overhead operacional

### Estratégias de Migração

Para suportar a evolução do esquema ao longo do tempo:

1. Utilizar versionamento de esquema explícito
2. Implementar migrações automáticas para estrutura básica
3. Usar abordagem tolerante para campos content/metadata
4. Documentar em código a estrutura esperada para cada tipo de artefato

### Segurança

Recomendações para proteção de dados:

1. Criptografar campos sensíveis (tokens, credenciais)
2. Implementar controle de acesso granular por projeto e tipo de artefato
3. Manter logs detalhados de alterações em artefatos críticos
4. Realizar backups regulares com testes de restauração

## Próximos Passos

1. Implementar esquema base no banco de dados escolhido
2. Criar APIs para CRUD de artefatos e vínculos
3. Desenvolver sistema de migrações para evolução do esquema
4. Implementar mecanismos de validação por tipo de artefato