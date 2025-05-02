#!/usr/bin/env python3
"""
InsightForge - Automated Reverse Engineering Tool
-------------------------------------------------
Main entry point for the CLI application.
"""

import argparse
import os
import sys
import json
from datetime import datetime

# Simple colored print function to avoid rich dependency for the test
def cprint(text, color=None):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    
    if color and color in colors:
        print(f"{colors[color]}{text}{colors['end']}")
    else:
        print(text)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="InsightForge - Automated Reverse Engineering Tool"
    )
    
    # Project analysis group
    project_group = parser.add_argument_group("Project Analysis")
    project_group.add_argument(
        "--project",
        type=str,
        help="Path to the project directory to analyze",
    )
    project_group.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for documentation (defaults to <project>/docs)",
    )
    project_group.add_argument(
        "--skip-rules",
        action="store_true",
        help="Skip business rules extraction",
    )
    project_group.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )
    
    # LLM Features group
    llm_group = parser.add_argument_group("LLM Features")
    llm_group.add_argument(
        "--search",
        type=str,
        help="Search the codebase using semantic search",
    )
    llm_group.add_argument(
        "--ask",
        type=str,
        help="Ask a question about the codebase in natural language",
    )
    llm_group.add_argument(
        "--explain",
        action="store_true",
        help="Explain a specific file or code section",
    )
    llm_group.add_argument(
        "--file",
        type=str,
        help="File to explain or improve (used with --explain or --improve)",
    )
    llm_group.add_argument(
        "--start-line",
        type=int,
        help="Starting line for code explanation (used with --explain)",
    )
    llm_group.add_argument(
        "--end-line",
        type=int,
        help="Ending line for code explanation (used with --explain)",
    )
    llm_group.add_argument(
        "--explain-code",
        type=str,
        help="Explain a code snippet provided as a string",
    )
    llm_group.add_argument(
        "--improve",
        action="store_true",
        help="Suggest improvements for a file",
    )
    llm_group.add_argument(
        "--generate-docs",
        action="store_true",
        help="Generate documentation for a file",
    )
    llm_group.add_argument(
        "--rebuild-embeddings",
        action="store_true",
        help="Rebuild embeddings for semantic search",
    )
    
    # LLM Configuration group
    llm_config_group = parser.add_argument_group("LLM Configuration")
    llm_config_group.add_argument(
        "--model",
        type=str,
        default="mistral",
        help="Model to use for LLM features (default: mistral)",
    )
    llm_config_group.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for LLM generation (default: 0.7)",
    )
    llm_config_group.add_argument(
        "--max-tokens",
        type=int,
        default=1000,
        help="Maximum tokens for LLM generation (default: 1000)",
    )
    
    args = parser.parse_args()
    
    # Validate that at least one main action is specified
    if not (args.project or args.search or args.ask or args.explain or 
            args.explain_code or args.improve or args.generate_docs):
        parser.error("At least one action must be specified (--project, --search, --ask, etc.)")
    
    return args


def validate_project_path(project_path):
    """Validate that the provided project path exists and is a directory."""
    if not os.path.exists(project_path):
        cprint(f"Error: Project path '{project_path}' does not exist.", 'red')
        return False
    
    if not os.path.isdir(project_path):
        cprint(f"Error: Project path '{project_path}' is not a directory.", 'red')
        return False
    
    return True


def handle_llm_features(args):
    """Handle LLM-specific features."""
    # Import LLM components
    try:
        from insightforge.llm import OllamaProvider
        from insightforge.llm.embeddings import EmbeddingStore, CodeEmbedder
        from insightforge.llm.query import QueryEngine, QueryResult
    except ImportError:
        cprint("Error: Required LLM modules not available.", 'red')
        return 1
    
    # Initialize Ollama provider
    provider = OllamaProvider(model=args.model)
    
    # Determine project path and embedding directory
    project_path = args.project
    if not project_path and args.file:
        project_path = os.path.dirname(os.path.abspath(args.file))
    
    if not project_path:
        cprint("Error: Project path is required for LLM features.", 'red')
        return 1
    
    embedding_dir = os.path.join(project_path, ".embeddings")
    
    # Initialize embedding store and query engine
    embedding_store = EmbeddingStore(embedding_dir, provider)
    query_engine = QueryEngine(provider, embedding_store)
    
    # Rebuild embeddings if requested
    if args.rebuild_embeddings:
        cprint("Rebuilding embeddings...", 'magenta')
        
        # First clear existing embeddings
        embedding_store.clear()
        
        # Import CodeParser to get parsed data
        from insightforge.reverse_engineering import CodeParser
        
        # Parse the code
        parser = CodeParser(project_path)
        parsed_data = parser.parse()
        
        # Create embeddings
        code_embedder = CodeEmbedder(project_path, embedding_dir, provider)
        code_embedder.embed_codebase(parsed_data)
        
        # Embed documentation if it exists
        docs_dir = os.path.join(project_path, "docs")
        if os.path.exists(docs_dir) and os.path.isdir(docs_dir):
            code_embedder.embed_documentation(docs_dir)
        
        cprint("Embeddings rebuilt successfully.", 'green')
    
    # Handle semantic search
    if args.search:
        cprint(f"Searching for: {args.search}", 'magenta')
        results = embedding_store.search(args.search, top_k=5)
        
        if not results:
            cprint("No results found.", 'yellow')
        else:
            cprint("\nSearch Results:", 'green')
            for i, result in enumerate(results):
                cprint(f"\n[{i+1}] Similarity: {result['similarity']:.4f}", 'blue')
                
                # Print metadata based on type
                metadata = result.get('metadata', {})
                if metadata.get('type') == 'class':
                    cprint(f"Class: {metadata.get('name')}", 'bold')
                    cprint(f"File: {metadata.get('file_path')}")
                elif metadata.get('type') == 'function':
                    cprint(f"Function: {metadata.get('name')}", 'bold')
                    cprint(f"File: {metadata.get('file_path')}")
                elif metadata.get('type') == 'doc':
                    cprint(f"Document: {metadata.get('title', 'Untitled')}", 'bold')
                    cprint(f"Path: {metadata.get('file_path')}")
                
                # Print preview of the text
                preview = result.get('text', '')[:200] + "..." if len(result.get('text', '')) > 200 else result.get('text', '')
                print(f"\n{preview}\n")
    
    # Handle natural language query
    if args.ask:
        cprint(f"Question: {args.ask}", 'magenta')
        query_result = query_engine.query(args.ask)
        
        cprint("\nAnswer:", 'green')
        print(f"\n{query_result.answer}\n")
        
        if query_result.sources:
            cprint("\nSources:", 'blue')
            for i, source in enumerate(query_result.sources):
                metadata = source.get('metadata', {})
                src_type = metadata.get('type', 'unknown')
                if src_type == 'class':
                    print(f"[{i+1}] Class: {metadata.get('name')} (File: {metadata.get('file_path')})")
                elif src_type == 'function':
                    print(f"[{i+1}] Function: {metadata.get('name')} (File: {metadata.get('file_path')})")
                elif src_type == 'doc':
                    print(f"[{i+1}] Document: {metadata.get('title', 'Untitled')} (File: {metadata.get('file_path')})")
                else:
                    print(f"[{i+1}] {src_type.capitalize()} (Similarity: {source.get('similarity', 0):.4f})")
    
    # Handle code explanation
    if args.explain and args.file:
        cprint(f"Explaining file: {args.file}", 'magenta')
        
        try:
            # Read the file content
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # If start-line and end-line are provided, extract just that section
            if args.start_line and args.end_line:
                lines = content.split('\n')
                if args.start_line <= len(lines) and args.end_line <= len(lines):
                    content = '\n'.join(lines[args.start_line-1:args.end_line])
                    cprint(f"Explaining lines {args.start_line}-{args.end_line}", 'blue')
            
            # Get explanation
            query_result = query_engine.explain_code(content)
            
            cprint("\nExplanation:", 'green')
            print(f"\n{query_result.answer}\n")
            
        except FileNotFoundError:
            cprint(f"Error: File '{args.file}' not found.", 'red')
            return 1
    
    # Handle code snippet explanation
    if args.explain_code:
        cprint("Explaining code snippet:", 'magenta')
        print(f"\n{args.explain_code}\n")
        
        query_result = query_engine.explain_code(args.explain_code)
        
        cprint("\nExplanation:", 'green')
        print(f"\n{query_result.answer}\n")
    
    # Handle code improvement suggestions
    if args.improve and args.file:
        cprint(f"Suggesting improvements for file: {args.file}", 'magenta')
        
        try:
            # Read the file content
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get improvement suggestions
            query_result = query_engine.suggest_improvements(content)
            
            cprint("\nImprovement Suggestions:", 'green')
            print(f"\n{query_result.answer}\n")
            
        except FileNotFoundError:
            cprint(f"Error: File '{args.file}' not found.", 'red')
            return 1
    
    # Handle documentation generation
    if args.generate_docs and args.file:
        cprint(f"Generating documentation for file: {args.file}", 'magenta')
        
        try:
            # Read the file content
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine language from file extension
            ext = os.path.splitext(args.file)[1].lower()
            language = 'python'  # Default
            if ext in ['.js', '.jsx']:
                language = 'javascript'
            elif ext in ['.ts', '.tsx']:
                language = 'typescript'
            elif ext == '.php':
                language = 'php'
            
            # Generate documentation
            query_result = query_engine.generate_docstring(content, language)
            
            cprint("\nGenerated Documentation:", 'green')
            print(f"\n{query_result.answer}\n")
            
        except FileNotFoundError:
            cprint(f"Error: File '{args.file}' not found.", 'red')
            return 1
    
    return 0


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Check if we're using LLM features
    if args.search or args.ask or args.explain or args.explain_code or args.improve or args.generate_docs or args.rebuild_embeddings:
        return handle_llm_features(args)
    
    # If not using LLM features, we're doing project analysis
    if not args.project:
        cprint("Error: Project path is required for analysis.", 'red')
        return 1
    
    # Validate project path
    if not validate_project_path(args.project):
        return 1
    
    # Determine output directory
    output_dir = args.output or os.path.join(args.project, "docs")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create internal directory for status and metadata
    internal_dir = os.path.join(output_dir, "internal")
    os.makedirs(internal_dir, exist_ok=True)
    
    # Display start message
    cprint("Starting InsightForge analysis...", 'green')
    cprint(f"Project: {args.project}", 'bold')
    cprint(f"Output: {output_dir}", 'bold')
    
    # Initialize status
    status_data = {
        "project": args.project,
        "steps": {
            "code_analysis": False,
            "doc_generation": False,
            "usecase_extraction": False,
            "business_rules_extraction": False,
            "backlog_generation": False,
            "llm_ingestion": False
        },
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "files_analyzed": 0
    }
    
    try:
        # Import components (for easier testing)
        from insightforge.reverse_engineering import (
            CodeParser, DocGenerator, UseCaseExtractor, 
            BacklogBuilder, BusinessRulesExtractor
        )
        
        # Step 1: Parse code
        cprint("Step 1: Parsing project code...", 'magenta')
        parser = CodeParser(args.project)
        parsed_data = parser.parse()
        
        # Update status
        status_data["steps"]["code_analysis"] = True
        status_data["files_analyzed"] = len(parsed_data.get("functions", []))
        cprint(f"Found {len(parsed_data.get('classes', []))} classes and {len(parsed_data.get('functions', []))} functions", 'blue')
        
        # Step 2: Extract use cases
        cprint("\nStep 2: Extracting use cases...", 'magenta')
        usecase_extractor = UseCaseExtractor()
        use_cases = usecase_extractor.extract(parsed_data)
        
        # Update status
        status_data["steps"]["usecase_extraction"] = True
        cprint(f"Extracted {len(use_cases)} use cases", 'blue')
        
        # Step 3: Extract business rules (if not skipped)
        if not args.skip_rules:
            cprint("\nStep 3: Extracting business rules...", 'magenta')
            rules_extractor = BusinessRulesExtractor()
            business_rules = rules_extractor.extract_from_parsed_data(parsed_data)
            
            # Update status
            status_data["steps"]["business_rules_extraction"] = True
            cprint(f"Extracted {len(business_rules)} business rules", 'blue')
        else:
            cprint("\nStep 3: Skipping business rules extraction", 'yellow')
            business_rules = []
        
        # Step 4: Generate documentation
        cprint("\nStep 4: Generating documentation...", 'magenta')
        doc_generator = DocGenerator(output_dir)
        doc_generator.generate(parsed_data)
        
        # Create directories for use cases and business rules if they don't exist
        usecases_dir = os.path.join(output_dir, "usecases")
        os.makedirs(usecases_dir, exist_ok=True)
        
        business_rules_dir = os.path.join(output_dir, "business_rules")
        os.makedirs(business_rules_dir, exist_ok=True)
        
        # Generate use case documentation
        for uc in use_cases:
            uc_file = os.path.join(usecases_dir, f"{uc['id']}.md")
            with open(uc_file, 'w', encoding='utf-8') as f:
                f.write(f"# Use Case: {uc['id']} - {uc['name']}\n\n")
                f.write(f"## Description\n\n{uc['description']}\n\n")
                f.write(f"## Source\n\n")
                f.write(f"- **Component**: {uc['source']}\n")
                f.write(f"- **File**: {uc['file_path']}\n")
        
        # Generate business rules documentation
        for rule in business_rules:
            rule_file = os.path.join(business_rules_dir, f"{rule.id}.md")
            with open(rule_file, 'w', encoding='utf-8') as f:
                f.write(rule.to_markdown())
        
        # Update status
        status_data["steps"]["doc_generation"] = True
        
        # Step 5: Generate backlog items
        cprint("\nStep 5: Generating backlog items...", 'magenta')
        backlog_builder = BacklogBuilder()
        backlog = backlog_builder.build_from_use_cases(use_cases)
        
        # Generate backlog documentation
        backlog_builder.generate_markdown(output_dir)
        
        # Update status
        status_data["steps"]["backlog_generation"] = True
        cprint(f"Generated {len(backlog.get('user_stories', []))} user stories", 'blue')
        cprint(f"Generated {len(backlog.get('epics', []))} epics", 'blue')
        
        # Step 6: Initialize LLM features (generate embeddings)
        try:
            cprint("\nStep 6: Initializing LLM features...", 'magenta')
            
            from insightforge.llm import OllamaProvider
            from insightforge.llm.embeddings import CodeEmbedder
            
            # Initialize provider
            provider = OllamaProvider()
            
            # Set up embedding directory
            embedding_dir = os.path.join(args.project, ".embeddings")
            os.makedirs(embedding_dir, exist_ok=True)
            
            # Create embeddings
            code_embedder = CodeEmbedder(args.project, embedding_dir, provider)
            code_embedder.embed_codebase(parsed_data)
            
            # Embed documentation
            code_embedder.embed_documentation(output_dir)
            
            # Update status
            status_data["steps"]["llm_ingestion"] = True
            cprint("LLM features initialized", 'blue')
            
        except ImportError:
            cprint("\nSkipping LLM feature initialization (required modules not available)", 'yellow')
        except Exception as e:
            cprint(f"\nError initializing LLM features: {str(e)}", 'yellow')
        
        # Save status
        status_file = os.path.join(internal_dir, "mcp_status.json")
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        cprint("\nAnalysis complete!", 'green')
        cprint(f"Documentation generated in {output_dir}", 'blue')
        cprint(f"Status saved to {status_file}", 'blue')
        
        return 0
    
    except Exception as e:
        cprint(f"Error during analysis: {str(e)}", 'red')
        # Save current status even if there was an error
        status_file = os.path.join(internal_dir, "mcp_status.json")
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        return 1


if __name__ == "__main__":
    sys.exit(main())