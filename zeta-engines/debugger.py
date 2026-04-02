"""
ZETA ∞ DEBUGGER ENGINE — Code Investigation & Analysis
The microscope that sees through code to find what's wrong.

Features:
  - Static code analysis (AST-based)
  - Python runtime debugging (trace injection)
  - Performance profiling
  - Error detection and suggestion
  - Code complexity analysis
  - Security vulnerability scanning

Dependencies: tree_sitter (installed)
"""

import sys, time, ast, os, inspect, textwrap
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class DebuggerEngine:
    """Static and dynamic code debugger with multiple analysis methods"""
    
    def __init__(self):
        self.findings = []
        
        # Security patterns to detect
        self.security_patterns = {
            'eval_usage': 'eval(',
            'exec_usage': 'exec(',
            'subprocess_shell': 'shell=True',
            'sql_injection': ['?', '%s', '.format(', 'f"SELECT', "f'SELECT"],
            'path_traversal': 'open(',
            'pickle_load': 'pickle.load',
            'hardcoded_password': ['password', 'secret', 'api_key', 'token'],
            'crypto_hardcoded': ['DES', 'MD5', 'sha1']
        }
    
    def analyze_source_file(self, filepath: str) -> Dict[str, Any]:
        """Comprehensive analysis of a source file"""
        try:
            source = open(filepath).read()
        except Exception as e:
            return {'error': str(e)}
        
        return self.analyze_source(source, filepath)
    
    def analyze_source(self, source: str, name: str = 'source') -> Dict[str, Any]:
        """Full source code analysis"""
        result = {
            'name': name,
            'lines': len(source.split('\n')),
            'bytes': len(source),
        }
        
        # AST parsing
        try:
            tree = ast.parse(source)
            result['syntax'] = 'valid'
            result['ast_analysis'] = self._analyze_ast(tree, source)
        except SyntaxError as e:
            result['syntax'] = f'error: {e.msg} (line {e.lineno})'
            return result
        
        # Security scan
        result['security'] = self._security_scan(source)
        
        # Complexity analysis
        result['complexity'] = self._complexity_analysis(source)
        
        # Suggestions
        result['suggestions'] = self._generate_suggestions(result)
        
        return result
    
    def _analyze_ast(self, tree: ast.AST, source: str) -> Dict:
        """Detailed AST analysis"""
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [d.id if isinstance(d, ast.Name) else '?' for d in node.decorator_list],
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    'base_classes': [b.id if isinstance(b, ast.Name) else '?' for b in node.bases],
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                else:
                    imports.append(f"{node.module or ''}")
        
        return {
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'total_functions': len(functions),
            'total_classes': len(classes),
        }
    
    def _security_scan(self, source: str) -> Dict:
        """Security vulnerability scanning"""
        findings = []
        lines = source.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if '#' in stripped:
                stripped = stripped.split('#')[0]
            
            for pattern_name, patterns in self.security_patterns.items():
                if isinstance(patterns, str):
                    patterns = [patterns]
                
                for pattern in patterns:
                    if pattern in stripped:
                        findings.append({
                            'line': i,
                            'type': pattern_name,
                            'content': stripped[:80],
                            'severity': 'high' if pattern_name in ('eval_usage', 'exec_usage', 'subprocess_shell') 
                                       else 'medium' if pattern_name in ('sql_injection', 'pickle_load', 'path_traversal')
                                       else 'low'
                        })
        
        critical = [f for f in findings if f['severity'] == 'high']
        warnings = [f for f in findings if f['severity'] == 'medium']
        info = [f for f in findings if f['severity'] == 'low']
        
        return {
            'findings': findings,
            'summary': {
                'total': len(findings),
                'critical': len(critical),
                'warnings': len(warnings),
                'info': len(info),
                'safe': len(findings) == 0,
            }
        }
    
    def _complexity_analysis(self, source: str) -> Dict:
        """Code complexity metrics"""
        lines = source.split('\n')
        non_empty = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        blank = [l for l in lines if not l.strip()]
        comments = [l for l in lines if l.strip().startswith('#')]
        code = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        
        # Count complexity indicators
        branch_count = sum(1 for l in lines for keyword in ['if ', 'elif ', 'else:', 'for ', 'while ', 'case ', 'match '] if keyword in l)
        exception_count = sum(1 for l in lines for keyword in ['except:', 'except ', 'raise ', 'throw '] if keyword in l)
        function_calls = sum(l.count('(') for l in lines if not l.strip().startswith('#'))
        
        # Approximate cyclomatic complexity
        try:
            tree = ast.parse(source)
            complexity = 1  # Base complexity
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
                elif isinstance(node, ast.comprehension):
                    complexity += 1
        except:
            complexity = -1  # Parse error
        
        return {
            'total_lines': len(lines),
            'code_lines': len(code),
            'blank_lines': blank,
            'comment_lines': len(comments),
            'branch_points': branch_count,
            'exception_handlers': exception_count,
            'function_calls': function_calls,
            'cyclomatic_complexity': complexity,
            'complexity_rating': 'low' if complexity <= 5 else 'medium' if complexity <= 10 else 'high' if complexity <= 20 else 'very high',
        }
    
    def _generate_suggestions(self, result: Dict) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        complexity = result.get('complexity', {})
        cc = complexity.get('cyclomatic_complexity', 0)
        if cc > 10:
            suggestions.append(f"⚠️ High cyclomatic complexity ({cc}). Consider refactoring.")
        
        security = result.get('security', {})
        s = security.get('summary', {})
        if s.get('critical', 0) > 0:
            suggestions.append(f"🔴 {s['critical']} critical security issues found")
        if s.get('warnings', 0) > 0:
            suggestions.append(f"🟡 {s['warnings']} security warnings")
        
        if result.get('lines', 0) > 500:
            suggestions.append("📝 File is very long (>500 lines). Consider splitting.")
        
        return suggestions
    
    def _check_unused_imports(self, filepath: str, imports: List[str], source: str) -> List[str]:
        """Check for unused imports"""
        unused = []
        for imp in imports:
            if imp and imp not in source[source.index(imp)+len(imp):]:
                unused.append(imp)
        return unused
    
    def trace_execution(self, code: str, globals_dict: dict = None, 
                       max_traces: int = 1000, verbose: bool = False) -> Dict:
        """Trace Python code execution line-by-line"""
        trace_log = []
        trace_count = 0
        
        def tracer(frame, event, arg):
            nonlocal trace_count
            if trace_count >= max_traces:
                return None
            
            if event == 'line':
                trace_count += 1
                entry = {
                    'event': event,
                    'line': frame.f_lineno,
                    'file': frame.f_code.co_filename,
                    'function': frame.f_code.co_name,
                }
                if verbose and 'arg' in frame.f_locals:
                    entry['locals'] = {k: str(v)[:100] for k, v in frame.f_locals.items() if k != '_'}
                trace_log.append(entry)
            
            return tracer
        
        if globals_dict is None:
            globals_dict = {}
        
        try:
            sys.settrace(tracer)
            exec(code, globals_dict)
        except Exception as e:
            trace_log.append({'event': 'error', 'error': str(e)})
        finally:
            sys.settrace(None)
        
        return {
            'traces': trace_log,
            'trace_count': trace_count,
            'status': 'completed' if 'error' not in [t.get('event') for t in trace_log] else 'error'
        }
    
    def compare_files(self, file1: str, file2: str) -> Dict:
        """Compare two source files and highlight differences"""
        try:
            source1 = open(file1).read().split('\n')
            source2 = open(file2).read().split('\n')
        except Exception as e:
            return {'error': str(e)}
        
        differences = []
        max_len = max(len(source1), len(source2))
        
        for i in range(max_len):
            line1 = source1[i] if i < len(source1) else None
            line2 = source2[i] if i < len(source2) else None
            
            if line1 != line2:
                differences.append({
                    'line': i + 1,
                    'file1': line1,
                    'file2': line2,
                })
        
        # Analyze both
        analysis1 = self.analyze_source('\n'.join(source1), file1)
        analysis2 = self.analyze_source('\n'.join(source2), file2)
        
        return {
            'differences': differences,
            'diff_count': len(differences),
            'common_lines': max_len - len(differences),
            'analysis1': analysis1,
            'analysis2': analysis2,
        }


# ── Quick test ─────────────────────────────────────────────────
if __name__ == '__main__':
    print("⚡ ZETA ∞ DEBUGGER ENGINE")
    print("=" * 50)
    
    engine = DebuggerEngine()
    
    # Test: Analyze a sample Python module
    test_code = '''
import os
import sys

def unsafe_function(user_input: str) -> dict:
    result = eval(user_input)
    with open("config.txt", "w") as f:
        f.write(result)
    return {"status": "ok"}

def safe_function(data: list) -> int:
    total = 0
    for item in data:
        if item > 0:
            total += item
        elif item == 0:
            continue
        else:
            total = max(total, item)
    return total
'''
    
    print("\n📝 Analyzing code...")
    analysis = engine.analyze_source(test_code, 'test_module')
    
    print(f"\n📊 Syntax: {analysis['syntax']}")
    print(f"📏 Lines: {analysis['lines']}")
    print(f"🧩 Complexity: {analysis['complexity']['complexity_rating']} ({analysis['complexity'].get('cyclomatic_complexity', '?')})")
    
    print(f"\n🔍 Security scan:")
    sec = analysis['security']
    print(f"   Total findings: {sec['summary']['total']}")
    print(f"   🔴 Critical: {sec['summary']['critical']}")
    print(f"   🟡 Warnings: {sec['summary']['warnings']}")
    
    for finding in analysis['security']['findings']:
        print(f"   - Line {finding['line']}: {finding['type']} ({finding['severity']}): {finding['content'][:60]}")
    
    print(f"\n💡 Suggestions:")
    for suggestion in analysis['suggestions']:
        print(f"   {suggestion}")
    
    # Test: Trace execution
    print("\n🔍 Execution trace test:")
    trace = engine.trace_execution('x = 5; y = x + 1; print(f"result: {y}")', verbose=True)
    print(f"   Traces captured: {trace['trace_count']}")
    print(f"   Status: {trace['status']}")
    
    print("\n✅ Debugger Engine operational")
