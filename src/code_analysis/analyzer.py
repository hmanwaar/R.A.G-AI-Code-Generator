import ast
import subprocess
from typing import Dict, List, Any
import pylint.lint
from pylint.reporters import JSONReporter
import bandit.core.manager
import bandit.core.issue
import black
import io
import json

class CodeAnalyzer:
    def __init__(self):
        self.pylint_reporter = JSONReporter()
        
    def analyze_code(self, code: str, file_path: str = None) -> Dict[str, Any]:
        """Perform comprehensive code analysis."""
        results = {
            "pylint": self._run_pylint(code, file_path),
            "bandit": self._run_bandit(code, file_path),
            "black": self._run_black(code),
            "ast_analysis": self._analyze_ast(code)
        }
        return results
    
    def _run_pylint(self, code: str, file_path: str = None) -> List[Dict[str, Any]]:
        """Run pylint analysis on the code."""
        if file_path:
            with open(file_path, 'w') as f:
                f.write(code)
            pylint.lint.Run([file_path], reporter=self.pylint_reporter, do_exit=False)
        else:
            pylint.lint.Run(['--from-stdin'], reporter=self.pylint_reporter, do_exit=False)
            self.pylint_reporter.set_source(code)
        return self.pylint_reporter.messages
    
    def _run_bandit(self, code: str, file_path: str = None) -> List[Dict[str, Any]]:
        """Run bandit security analysis on the code."""
        if file_path:
            with open(file_path, 'w') as f:
                f.write(code)
            b_mgr = bandit.core.manager.BanditManager()
            b_mgr.discover_files([file_path])
            b_mgr.run_tests()
        else:
            b_mgr = bandit.core.manager.BanditManager()
            b_mgr.discover_files(['-'])
            b_mgr.run_tests()
            b_mgr.files_list = ['-']
            b_mgr.files_data = {'-': code}
        
        return [
            {
                "issue": issue.text,
                "severity": issue.severity,
                "confidence": issue.confidence,
                "line": issue.lineno,
                "col": issue.col_offset
            }
            for issue in b_mgr.get_issue_list()
        ]
    
    def _run_black(self, code: str) -> Dict[str, Any]:
        """Run black code formatter to check code style."""
        try:
            formatted_code = black.format_str(code, mode=black.FileMode())
            return {
                "needs_formatting": formatted_code != code,
                "formatted_code": formatted_code
            }
        except Exception as e:
            return {
                "error": str(e),
                "needs_formatting": True
            }
    
    def _analyze_ast(self, code: str) -> Dict[str, Any]:
        """Analyze code using AST for structural issues."""
        try:
            tree = ast.parse(code)
            analysis = {
                "imports": [],
                "functions": [],
                "classes": [],
                "complexity": self._calculate_complexity(tree)
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    analysis["imports"].extend(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    analysis["imports"].append(f"{node.module}.{node.names[0].name}")
                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "lineno": node.lineno
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "lineno": node.lineno
                    })
            
            return analysis
        except SyntaxError as e:
            return {"error": f"Syntax error: {str(e)}"}
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate code complexity metrics."""
        complexity = {
            "branches": 0,
            "loops": 0,
            "functions": 0,
            "classes": 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.Try, ast.ExceptHandler)):
                complexity["branches"] += 1
            elif isinstance(node, (ast.For, ast.While)):
                complexity["loops"] += 1
            elif isinstance(node, ast.FunctionDef):
                complexity["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                complexity["classes"] += 1
        
        return complexity
    
    def get_improvement_suggestions(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on analysis results."""
        suggestions = []
        
        # Pylint suggestions
        for msg in analysis_results["pylint"]:
            if msg["type"] in ["error", "warning"]:
                suggestions.append(f"Pylint {msg['type']}: {msg['message']} (line {msg['line']})")
        
        # Bandit suggestions
        for issue in analysis_results["bandit"]:
            if issue["severity"] in ["HIGH", "MEDIUM"]:
                suggestions.append(
                    f"Security issue ({issue['severity']}): {issue['issue']} "
                    f"(line {issue['line']}, confidence: {issue['confidence']})"
                )
        
        # Black suggestions
        if analysis_results["black"].get("needs_formatting", False):
            suggestions.append("Code formatting: Consider using Black to format your code")
        
        # AST analysis suggestions
        ast_analysis = analysis_results["ast_analysis"]
        if "error" not in ast_analysis:
            complexity = ast_analysis["complexity"]
            if complexity["functions"] > 10:
                suggestions.append("Consider breaking down the code into smaller modules")
            if complexity["branches"] > 5:
                suggestions.append("High cyclomatic complexity detected. Consider simplifying the logic")
        
        return suggestions
