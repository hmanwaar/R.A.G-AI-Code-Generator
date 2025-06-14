import os
import json
from typing import Dict, Any, List
import tempfile
from pathlib import Path

def ensure_directory(directory: str) -> None:
    """Ensure that a directory exists, create it if it doesn't."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def save_to_temp_file(content: str, suffix: str = '.py') -> str:
    """Save content to a temporary file and return the file path."""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Error loading JSON file {file_path}: {str(e)}")

def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """Save data to a JSON file."""
    ensure_directory(os.path.dirname(file_path))
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def format_code_analysis_results(results: Dict[str, Any]) -> str:
    """Format code analysis results into a readable string."""
    output = []
    
    # Format Pylint results
    if results.get("pylint"):
        output.append("=== Pylint Analysis ===")
        for msg in results["pylint"]:
            output.append(f"[{msg['type'].upper()}] Line {msg['line']}: {msg['message']}")
    
    # Format Bandit results
    if results.get("bandit"):
        output.append("\n=== Security Analysis (Bandit) ===")
        for issue in results["bandit"]:
            output.append(
                f"[{issue['severity']}] Line {issue['line']}: {issue['issue']} "
                f"(Confidence: {issue['confidence']})"
            )
    
    # Format Black results
    if results.get("black"):
        black_results = results["black"]
        output.append("\n=== Code Formatting (Black) ===")
        if black_results.get("needs_formatting"):
            output.append("Code needs formatting. Consider using Black to format the code.")
        if black_results.get("error"):
            output.append(f"Error during formatting check: {black_results['error']}")
    
    # Format AST analysis
    if results.get("ast_analysis"):
        ast_results = results["ast_analysis"]
        if "error" not in ast_results:
            output.append("\n=== Code Structure Analysis ===")
            complexity = ast_results["complexity"]
            output.append(f"Functions: {complexity['functions']}")
            output.append(f"Classes: {complexity['classes']}")
            output.append(f"Branches: {complexity['branches']}")
            output.append(f"Loops: {complexity['loops']}")
            
            if ast_results["imports"]:
                output.append("\nImports:")
                for imp in ast_results["imports"]:
                    output.append(f"  - {imp}")
            
            if ast_results["functions"]:
                output.append("\nFunctions:")
                for func in ast_results["functions"]:
                    output.append(f"  - {func['name']}({', '.join(func['args'])})")
            
            if ast_results["classes"]:
                output.append("\nClasses:")
                for cls in ast_results["classes"]:
                    output.append(f"  - {cls['name']}")
                    for method in cls["methods"]:
                        output.append(f"    * {method}")
    
    return "\n".join(output)

def get_file_extension(file_path: str) -> str:
    """Get the file extension from a file path."""
    return os.path.splitext(file_path)[1].lower()

def is_python_file(file_path: str) -> bool:
    """Check if a file is a Python file."""
    return get_file_extension(file_path) == '.py'

def get_relative_path(file_path: str, base_dir: str) -> str:
    """Get the relative path of a file from a base directory."""
    try:
        return os.path.relpath(file_path, base_dir)
    except ValueError:
        return file_path 