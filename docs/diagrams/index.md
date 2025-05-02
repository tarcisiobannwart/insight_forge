---
layout: default
title: Diagramas
---

# Diagramas

Esta seção contém os diagramas gerados para o projeto InsightForge.

## Diagrama de Classe

O diagrama abaixo mostra as principais classes do InsightForge e seus relacionamentos:

```mermaid
classDiagram
    class CodeParser {
        +project_path: str
        +exclude_dirs: List[str]
        +exclude_files: List[str]
        +parse() Dict
        -_parse_file(file_path) Dict
        -_detect_language(file_path) str
    }
    
    class DiagramGenerator {
        +max_items_per_diagram: int
        +detect_relationships: bool
        +generate_class_diagram(parsed_data) str
        +generate_module_diagram(parsed_data) str
        +generate_sequence_diagram(parsed_data, flow_name) str
    }
    
    class DocGenerator {
        +output_dir: str
        +generate_diagrams: bool
        +generate(parsed_data, project_name) None
        -_generate_overview(parsed_data) None
        -_generate_class_docs(classes) None
    }
    
    class TemplateManager {
        +output_dir: str
        +render_class(class_data) str
        +render_function(function_data) str
        +render_overview(parsed_data) str
    }
    
    class RelationshipDetector {
        +detect_relationships(parsed_data) Dict
    }
    
    class FlowAnalyzer {
        +analyze(parsed_data) Dict
    }
    
    class LLMProvider {
        <<abstract>>
        +generate(prompt) LLMResponse
        +generate_chat(messages) LLMResponse
        +get_embeddings(texts) List
    }
    
    class OllamaProvider {
        +base_url: str
        +model: str
        +generate(prompt) LLMResponse
        +generate_chat(messages) LLMResponse
        +get_embeddings(texts) List
    }
    
    class EmbeddingStore {
        +data_dir: str
        +provider: LLMProvider
        +embeddings: Dict
        +add(key, text, metadata) None
        +search(query, top_k) List
    }
    
    class GitHubExporter {
        +source_dir: str
        +target_dir: str
        +export(project_name) str
        +publish(branch) bool
    }
    
    CodeParser --> DiagramGenerator: uses
    CodeParser --> DocGenerator: provides data to
    DocGenerator --> TemplateManager: uses
    DocGenerator --> DiagramGenerator: uses
    DiagramGenerator --> RelationshipDetector: uses
    DiagramGenerator --> FlowAnalyzer: uses
    LLMProvider <|-- OllamaProvider: implements
    OllamaProvider --> EmbeddingStore: provides embeddings for
    DocGenerator --> GitHubExporter: outputs to
```

## Diagrama de Módulos

O diagrama abaixo mostra a estrutura de módulos do InsightForge:

```mermaid
graph TD
    %% Styles
    classDef core fill:#3572A5,stroke:#2B5B84,color:white;
    classDef parser fill:#4F5D95,stroke:#3F4A77,color:white;
    classDef diagrams fill:#F7DF1E,stroke:#C6B318,color:black;
    classDef llm fill:#007ACC,stroke:#005F9E,color:white;
    classDef export fill:#EAEAEA,stroke:#CCCCCC,color:black;
    
    %% Core modules
    insightforge[insightforge]
    main[main.py]
    config[config]
    
    %% Parsing modules
    re[reverse_engineering]
    code_parser[code_parser.py]
    php_parser[php_parser.py]
    js_parser[javascript_parser.py]
    
    %% Diagram modules
    rel_detector[relationship_detector.py]
    flow_analyzer[flow_analyzer.py]
    diagram_gen[diagram_generator.py]
    
    %% Documentation modules
    doc_gen[doc_generator.py]
    template_sys[template_system.py]
    
    %% LLM modules
    llm[llm]
    llm_base[base.py]
    ollama[ollama.py]
    embed[embeddings.py]
    query[query.py]
    
    %% Export modules
    exporters[exporters]
    github_exp[github_exporter.py]
    github_int[github_integration.py]
    
    %% Relationships
    insightforge --> main
    insightforge --> config
    insightforge --> re
    insightforge --> llm
    insightforge --> exporters
    
    re --> code_parser
    re --> php_parser
    re --> js_parser
    re --> rel_detector
    re --> flow_analyzer
    re --> diagram_gen
    re --> doc_gen
    re --> template_sys
    
    code_parser --> php_parser
    code_parser --> js_parser
    
    diagram_gen --> rel_detector
    diagram_gen --> flow_analyzer
    
    doc_gen --> template_sys
    doc_gen --> diagram_gen
    
    llm --> llm_base
    llm --> ollama
    llm --> embed
    llm --> query
    
    ollama --> llm_base
    embed --> llm_base
    query --> llm_base
    query --> embed
    
    exporters --> github_exp
    exporters --> github_int
    github_exp --> github_int
    
    %% Apply styles
    class insightforge,main,config core;
    class re,code_parser,php_parser,js_parser parser;
    class rel_detector,flow_analyzer,diagram_gen,doc_gen,template_sys diagrams;
    class llm,llm_base,ollama,embed,query llm;
    class exporters,github_exp,github_int export;
```

## Diagrama de Sequência

O diagrama abaixo mostra o fluxo de processamento principal do InsightForge:

```mermaid
sequenceDiagram
    participant User
    participant Main as Main CLI
    participant Parser as CodeParser
    participant RelDetector as RelationshipDetector
    participant FlowAnalyzer
    participant DiagramGen as DiagramGenerator
    participant DocGen as DocGenerator
    participant Exporter as GitHubExporter
    
    User->>+Main: insightforge analyze
    Main->>+Parser: parse()
    Parser-->>-Main: parsed_data
    
    Main->>+RelDetector: detect_relationships(parsed_data)
    RelDetector-->>-Main: enriched_data
    
    Main->>+FlowAnalyzer: analyze(enriched_data)
    FlowAnalyzer-->>-Main: flow_data
    
    Main->>+DiagramGen: generate_diagrams(flow_data)
    DiagramGen-->>-Main: diagrams
    
    Main->>+DocGen: generate(flow_data, diagrams)
    DocGen-->>-Main: documentation
    
    User->>Main: insightforge github-publish
    Main->>+Exporter: export(documentation)
    Exporter-->>Main: exported_docs
    Main->>+Exporter: publish(exported_docs)
    Exporter-->>-Main: success
    
    Main-->>-User: Documentation published successfully
```