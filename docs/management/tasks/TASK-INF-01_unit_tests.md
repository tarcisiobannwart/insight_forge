# TASK-INF-01: Implementar Testes Unitários

## Descrição
Desenvolver uma suíte completa de testes unitários para todos os componentes do InsightForge, garantindo a qualidade do código, facilitando refatorações e prevenindo regressões. Esta tarefa inclui a configuração do framework de testes, implementação de testes para cada componente e configuração de métricas de cobertura.

## Detalhes
- **Prioridade**: Alta
- **Estimativa**: 5 dias
- **Épico**: Todos
- **Issue**: [ISSUE-004](../issues/ISSUE-004_unit_tests.md)
- **Responsável**: InsightForge Team
- **Status**: Concluído

## Requisitos

### Funcionais
- Todos os componentes principais devem ter testes unitários
- Os testes devem verificar o comportamento esperado em cenários normais e de erro
- Deve haver testes para casos limite e exceções
- Os testes devem ser independentes uns dos outros
- Deve haver integração com sistemas de CI

### Técnicos
- Usar pytest como framework principal de testes
- Atingir cobertura de código de pelo menos 80% para cada componente
- O tempo de execução total dos testes deve ser inferior a 60 segundos
- Os testes devem ser isolados de dependências externas usando mocks
- A execução deve ser reproduzível (sem dependências de estado externo)

## Subtarefas

### 1. Configurar framework de testes
- [x] Configurar pytest como framework principal
- [x] Implementar fixtures para projetos de teste
- [x] Configurar cobertura de código com pytest-cov
- [x] Criar mocks para dependências externas
- [x] Configurar execução paralela de testes

### 2. Implementar testes para CodeParser
- [x] Testes para class `CodeParser`
- [x] Testes para class `PythonAstParser`
- [x] Testes para os modelos de dados (CodeClass, CodeMethod)
- [x] Testes para detecção de herança
- [x] Testes para cenários de erro e recuperação

### 3. Implementar testes para DocGenerator
- [x] Testes para geração de documentação de classes
- [x] Testes para geração de documentação de funções
- [x] Testes para geração de índices e navegação
- [x] Testes para cenários de erro (arquivos inválidos, etc.)
- [x] Testes para personalização de templates

### 4. Implementar testes para UseCaseExtractor e BacklogBuilder
- [x] Testes para extração de casos de uso de docstrings
- [x] Testes para cenários sem casos de uso explícitos
- [x] Testes para geração de user stories
- [x] Testes para agrupamento em épicos
- [x] Testes para personalização de templates de saída

### 5. Implementar testes de integração
- [x] Testes para o fluxo completo com um projeto simples
- [x] Testes para configurações diferentes
- [x] Testes de performance em projetos maiores
- [x] Testes para diferentes formatos de saída
- [x] Testes para cenários de erro no fluxo completo

## Abordagem Técnica

### Estrutura de Testes
Seguiremos a estrutura padrão do pytest:

```
tests/
├── conftest.py              # Fixtures compartilhadas
├── test_code_parser.py      # Testes para CodeParser
├── test_doc_generator.py    # Testes para DocGenerator
├── test_usecase_extractor.py # Testes para UseCaseExtractor
├── test_backlog_builder.py  # Testes para BacklogBuilder
└── integration/             # Testes de integração
    ├── test_simple_project.py
    └── test_complex_project.py
```

### Fixtures de Teste
Criaremos fixtures para diferentes cenários:

```python
@pytest.fixture
def simple_python_file():
    """Fixture with a simple Python file content."""
    return """
class SimpleClass:
    \"\"\"A simple class for testing.
    
    Use Case: Testing the parser
    \"\"\"
    
    def __init__(self, value):
        self.value = value
        
    def get_value(self):
        \"\"\"Return the stored value.\"\"\"
        return self.value
"""

@pytest.fixture
def complex_project(tmp_path):
    """Create a temp project with multiple files for testing."""
    # Setup a temporary project structure
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create multiple Python files
    # ...
    
    return project_dir
```

### Mocks e Isolamento
Para isolar os testes de dependências externas, usaremos:

```python
@pytest.fixture
def mock_file_system(monkeypatch):
    """Mock file system operations."""
    mock_open = mock.mock_open(read_data="mocked file content")
    monkeypatch.setattr("builtins.open", mock_open)
    monkeypatch.setattr(os.path, "exists", lambda x: True)
    return mock_open

def test_doc_generator_with_mock_fs(mock_file_system):
    """Test with mocked file system."""
    generator = DocGenerator("/fake/path")
    # Test implementation...
```

### Cobertura de Código
Configuraremos pytest-cov para verificar a cobertura:

```bash
pytest --cov=insightforge tests/
```

E asseguraremos que cada módulo tem cobertura adequada:

```bash
pytest --cov=insightforge.reverse_engineering.code_parser tests/test_code_parser.py
```

## Critérios de Aceitação
- ✓ Framework de testes está configurado corretamente
- ✓ Todos os componentes principais têm testes unitários
- ✓ Cobertura de código é de pelo menos 80% para cada componente
- ✓ Todos os testes passam consistentemente
- ✓ Testes são independentes e não interferem uns com os outros
- ✓ Testes de integração verificam o fluxo completo
- ✓ O tempo de execução total dos testes é inferior a 60 segundos
- ✓ Documentação sobre como executar e estender os testes está disponível

## Impacto
A implementação de testes abrangentes proporcionará:
1. Maior confiança no código e suas funcionalidades
2. Facilidade para refatorar e melhorar o código existente
3. Detecção precoce de regressões
4. Documentação viva do comportamento esperado
5. Base para implementação de CI/CD

## Riscos
- Testes muito acoplados ao código podem dificultar refatorações
- Testes muito lentos podem desencorajar sua execução frequente
- Cobertura alta de código não garante ausência de bugs lógicos

## Referências
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Test-Driven Development](https://www.agilealliance.org/glossary/tdd/)