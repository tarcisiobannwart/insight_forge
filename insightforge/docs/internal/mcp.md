# InsightForge MCP (Multi-Component Process)

## Overview

The MCP (Multi-Component Process) is the core orchestration mechanism of InsightForge. It coordinates the execution of multiple modules responsible for analyzing source code, generating documentation, extracting use cases, building backlogs, and feeding language models.

## Execution Flow

```
1. Receive project path (--project parameter)
2. Perform code analysis (extract classes, functions, relationships)
3. Generate Markdown documentation
4. Extract use cases and business rules
5. Build user stories and epics for backlog
6. Prepare and ingest data into the language model (Ollama/Claude)
```

## Components

### 1. Code Parser

- **Purpose**: Analyze source code to extract classes, functions, relationships, and documentation
- **Input**: Project source files (.py, .js, .php, etc.)
- **Output**: Structured data representing code components and relationships
- **Key Files**: `code_parser.py`

### 2. Documentation Generator

- **Purpose**: Generate comprehensive Markdown documentation from parsed code
- **Input**: Structured data from Code Parser
- **Output**: Markdown files in a standardized structure
- **Key Files**: `doc_generator.py`

### 3. Use Case Extractor

- **Purpose**: Extract use cases from code comments and documentation
- **Input**: Parsed code data and existing documentation
- **Output**: Structured use case definitions
- **Key Files**: `usecase_extractor.py`

### 4. Backlog Builder

- **Purpose**: Generate user stories, epics, and tasks from use cases
- **Input**: Use cases and business rules
- **Output**: Structured backlog items in Markdown format
- **Key Files**: `backlog_builder.py`

### 5. LLM Integration

- **Purpose**: Feed extracted knowledge into language models
- **Input**: All generated documentation and structured data
- **Output**: Configured language model with project knowledge
- **Key Files**: `ollama_client.py`, `embedder.py`

## Status Tracking

The MCP status is tracked in `mcp_status.json`, which records the progress of each step in the process. This file is updated as each step completes, providing a record of what has been processed.

## Output Structure

All generated documentation follows a standardized structure:

```
<project>/docs/
├── overview/
├── business_rules/
├── usecases/
├── userstories/
├── project_management/
├── architecture/
├── api_reference/
├── traceability/
├── guidelines/
├── internal/
    ├── mcp.md
    └── mcp_status.json
```

## Error Handling

The MCP process includes error handling at each step, ensuring that failures in one component don't prevent others from executing. All errors are logged and reported to the user.

## Future Enhancements

- Support for additional programming languages
- Integration with project management tools (Jira, Trello)
- Automated diagram generation
- Incremental analysis based on git diff
- Custom documentation templates