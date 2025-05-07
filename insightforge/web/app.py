"""
Web Interface for InsightForge Configuration
-------------------------------------------
Simple web interface for managing InsightForge configuration.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add project root to path if running as script
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if script_dir not in sys.path:
    sys.path.insert(0, os.path.dirname(script_dir))

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

# Local imports
try:
    from insightforge.config.advanced_config_manager import AdvancedConfigManager, ModelConfig, ProviderConfig
    from insightforge.config.credentials_manager import get_credentials_manager
except ImportError:
    print("Error: InsightForge module not found in path.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("insightforge.web")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize configuration and credentials managers
config_manager = None
credentials_manager = None


def init_managers(config_file: Optional[str] = None):
    """Initialize configuration and credentials managers."""
    global config_manager, credentials_manager
    
    if config_file:
        config_path = config_file
    else:
        # Try to find config file
        config_path = os.path.join(os.getcwd(), "insightforge.yml")
        if not os.path.exists(config_path):
            # Try in the app's directory
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "insightforge.yml")
        
    # Initialize configuration manager
    config_manager = AdvancedConfigManager(config_path)
    
    # Initialize credentials manager
    credentials_manager = get_credentials_manager()


@app.before_request
def before_request():
    """Initialize configuration managers before each request."""
    if config_manager is None or credentials_manager is None:
        init_managers()


@app.route('/')
def home():
    """Home page."""
    return render_template('index.html')


@app.route('/config')
def config_overview():
    """Configuration overview page."""
    if config_manager is None:
        flash("Error: Configuration manager not initialized.", "error")
        return redirect(url_for('home'))
    
    # Get configuration
    secure_config = config_manager.get_secure_config()
    
    # Get LLM providers
    providers = config_manager.get_llm_providers()
    
    # Get integrations
    integrations = config_manager.get_integrations()
    
    # Get project paths
    project_paths = config_manager.get_project_paths()
    
    return render_template(
        'config.html',
        providers=providers,
        integrations=integrations,
        project_paths=project_paths,
        config_file=config_manager.config_file
    )


@app.route('/config/jira', methods=['GET', 'POST'])
def config_jira():
    """Jira configuration page."""
    if config_manager is None or credentials_manager is None:
        flash("Error: Configuration managers not initialized.", "error")
        return redirect(url_for('home'))
    
    # Get current Jira configuration
    integrations = config_manager.get_integrations()
    jira_config = integrations.get('jira')
    
    if request.method == 'POST':
        # Get form data
        jira_url = request.form.get('jira_url')
        username = request.form.get('username')
        api_token = request.form.get('api_token')
        project_key = request.form.get('project_key')
        
        # Get sync settings
        auto_create = 'auto_create' in request.form
        auto_update = 'auto_update' in request.form
        sync_interval = request.form.get('sync_interval', '0')
        try:
            sync_interval = int(sync_interval)
        except ValueError:
            sync_interval = 0
        
        # Test connection if requested
        if 'test_connection' in request.form:
            import requests
            from requests.auth import HTTPBasicAuth
            
            try:
                test_url = f"{jira_url.rstrip('/')}/rest/api/3/myself"
                response = requests.get(
                    test_url,
                    auth=HTTPBasicAuth(username, api_token),
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    display_name = user_data.get("displayName", "Unknown")
                    flash(f"Connection successful! Logged in as: {display_name}", "success")
                else:
                    flash(f"Connection failed! Status code: {response.status_code}", "error")
                    flash(f"Error: {response.text}", "error")
            except Exception as e:
                flash(f"Error testing connection: {str(e)}", "error")
        else:
            # Save configuration
            if api_token:
                credentials_manager.set_credential("jira", "api_token", api_token)
            
            # Save other settings
            config_manager.update_integration(
                name="jira",
                settings={
                    "url": jira_url,
                    "project_key": project_key,
                    "sync_settings": {
                        "auto_create": auto_create,
                        "auto_update": auto_update,
                        "sync_interval": sync_interval
                    }
                },
                credentials={
                    "username": username,
                    "api_token": "<CREDENTIAL_PLACEHOLDER>"
                }
            )
            
            # Save configuration
            config_manager.save()
            
            flash("Jira configuration saved successfully!", "success")
            return redirect(url_for('config_overview'))
    
    # Set default values
    defaults = {
        'url': '',
        'username': '',
        'project_key': '',
        'auto_create': False,
        'auto_update': False,
        'sync_interval': 0
    }
    
    if jira_config:
        defaults.update({
            'url': jira_config.settings.get('url', ''),
            'username': jira_config.credentials.get('username', ''),
            'project_key': jira_config.settings.get('project_key', ''),
            'auto_create': jira_config.settings.get('sync_settings', {}).get('auto_create', False),
            'auto_update': jira_config.settings.get('sync_settings', {}).get('auto_update', False),
            'sync_interval': jira_config.settings.get('sync_settings', {}).get('sync_interval', 0)
        })
    
    return render_template('jira_config.html', defaults=defaults)


@app.route('/config/github', methods=['GET', 'POST'])
def config_github():
    """GitHub configuration page."""
    if config_manager is None or credentials_manager is None:
        flash("Error: Configuration managers not initialized.", "error")
        return redirect(url_for('home'))
    
    # Get current GitHub configuration
    integrations = config_manager.get_integrations()
    github_config = integrations.get('github')
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        token = request.form.get('token')
        repository = request.form.get('repository')
        branch = request.form.get('branch')
        
        # Test connection if requested
        if 'test_connection' in request.form:
            import requests
            
            try:
                api_url = "https://api.github.com/user"
                response = requests.get(
                    api_url,
                    headers={
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    display_name = user_data.get("name", user_data.get("login", "Unknown"))
                    flash(f"Connection successful! Logged in as: {display_name}", "success")
                else:
                    flash(f"Connection failed! Status code: {response.status_code}", "error")
                    flash(f"Error: {response.text}", "error")
            except Exception as e:
                flash(f"Error testing connection: {str(e)}", "error")
        else:
            # Save configuration
            if token:
                credentials_manager.set_credential("github", "token", token)
            
            # Save other settings
            config_manager.update_integration(
                name="github",
                settings={
                    "repository": repository,
                    "branch": branch
                },
                credentials={
                    "username": username,
                    "token": "<CREDENTIAL_PLACEHOLDER>"
                }
            )
            
            # Save configuration
            config_manager.save()
            
            flash("GitHub configuration saved successfully!", "success")
            return redirect(url_for('config_overview'))
    
    # Set default values
    defaults = {
        'username': '',
        'repository': '',
        'branch': 'main'
    }
    
    if github_config:
        defaults.update({
            'username': github_config.credentials.get('username', ''),
            'repository': github_config.settings.get('repository', ''),
            'branch': github_config.settings.get('branch', 'main')
        })
    
    return render_template('github_config.html', defaults=defaults)


@app.route('/config/llm', methods=['GET', 'POST'])
def config_llm():
    """LLM configuration page."""
    if config_manager is None:
        flash("Error: Configuration manager not initialized.", "error")
        return redirect(url_for('home'))
    
    # Get LLM providers
    providers = config_manager.get_llm_providers()
    
    if request.method == 'POST':
        # Get form data
        provider_type = request.form.get('provider_type')
        provider_name = request.form.get('provider_name')
        is_default = 'is_default' in request.form
        
        model_id = request.form.get('model_id')
        model_name = request.form.get('model_name')
        api_key = request.form.get('api_key')
        endpoint = request.form.get('endpoint')
        
        # Get default tasks
        default_for = []
        for task in ['code_analysis', 'documentation', 'query', 'chat', 'embedding']:
            if f'default_for_{task}' in request.form:
                default_for.append(task)
        
        # Create model
        model = ModelConfig(
            id=model_id,
            display_name=model_name,
            api_key=api_key,
            endpoint=endpoint,
            default_for=default_for,
            parameters={
                "temperature": float(request.form.get('temperature', 0.7)),
                "max_tokens": int(request.form.get('max_tokens', 1000))
            }
        )
        
        # Create or update provider
        provider = ProviderConfig(
            name=provider_name,
            type=provider_type,
            default=is_default,
            models=[model]
        )
        
        # Save configuration
        config_manager.add_llm_provider(provider)
        config_manager.save()
        
        flash("LLM configuration saved successfully!", "success")
        return redirect(url_for('config_overview'))
    
    return render_template('llm_config.html', providers=providers)


@app.route('/config/project', methods=['GET', 'POST'])
def config_project():
    """Project paths configuration page."""
    if config_manager is None:
        flash("Error: Configuration manager not initialized.", "error")
        return redirect(url_for('home'))
    
    # Get project settings
    project_name = config_manager.get('project.name', 'Project')
    project_description = config_manager.get('project.description', '')
    project_paths = config_manager.get_project_paths()
    
    if request.method == 'POST':
        # Get project info
        new_name = request.form.get('project_name')
        new_description = request.form.get('project_description')
        
        # Update project info
        config_manager.set('project.name', new_name)
        config_manager.set('project.description', new_description)
        
        # Update paths
        for key in ['source_code', 'documentation', 'guides', 'prompts', 
                   'snippets', 'diagrams', 'issues', 'screens']:
            if key in request.form:
                config_manager.set_project_path(key, request.form.get(key))
        
        # Save configuration
        config_manager.save()
        
        flash("Project configuration saved successfully!", "success")
        return redirect(url_for('config_overview'))
    
    return render_template(
        'project_config.html', 
        project_name=project_name,
        project_description=project_description,
        project_paths=project_paths
    )


@app.route('/config/save', methods=['POST'])
def save_config():
    """Save configuration."""
    if config_manager is None:
        return jsonify({"status": "error", "message": "Configuration manager not initialized"})
    
    try:
        config_manager.save()
        return jsonify({"status": "success", "message": "Configuration saved successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/api/test_jira', methods=['POST'])
def test_jira_connection():
    """Test Jira connection."""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No data provided"})
    
    url = data.get('url')
    username = data.get('username')
    token = data.get('token')
    
    if not url or not username or not token:
        return jsonify({"status": "error", "message": "Missing required parameters"})
    
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        test_url = f"{url.rstrip('/')}/rest/api/3/myself"
        response = requests.get(
            test_url,
            auth=HTTPBasicAuth(username, token),
            headers={"Accept": "application/json"}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            display_name = user_data.get("displayName", "Unknown")
            return jsonify({
                "status": "success", 
                "message": f"Connection successful! Logged in as: {display_name}"
            })
        else:
            return jsonify({
                "status": "error", 
                "message": f"Connection failed! Status code: {response.status_code}",
                "details": response.text
            })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error testing connection: {str(e)}"})


@app.route('/api/test_github', methods=['POST'])
def test_github_connection():
    """Test GitHub connection."""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No data provided"})
    
    token = data.get('token')
    
    if not token:
        return jsonify({"status": "error", "message": "Missing token parameter"})
    
    try:
        import requests
        
        api_url = "https://api.github.com/user"
        response = requests.get(
            api_url,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        if response.status_code == 200:
            user_data = response.json()
            display_name = user_data.get("name", user_data.get("login", "Unknown"))
            return jsonify({
                "status": "success", 
                "message": f"Connection successful! Logged in as: {display_name}"
            })
        else:
            return jsonify({
                "status": "error", 
                "message": f"Connection failed! Status code: {response.status_code}",
                "details": response.text
            })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error testing connection: {str(e)}"})


@app.route('/api/ollama_models', methods=['GET'])
def get_ollama_models():
    """Get available Ollama models."""
    endpoint = request.args.get('endpoint', 'http://localhost:11434')
    
    try:
        import requests
        
        url = f"{endpoint.rstrip('/')}/api/tags"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return jsonify({"status": "success", "models": models})
        else:
            return jsonify({
                "status": "error", 
                "message": f"Failed to query models. Status code: {response.status_code}"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error querying Ollama: {str(e)}"})


def main():
    """Run the web application."""
    parser = argparse.ArgumentParser(description="InsightForge Web Interface")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Initialize configuration managers
    init_managers(args.config)
    
    # Run the app
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    import argparse
    main()