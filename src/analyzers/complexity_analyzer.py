"""Code complexity analysis using static analysis techniques"""

import ast
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from src.models import ComplexityMetrics, RiskLevel


class CyclomaticComplexityVisitor(ast.NodeVisitor):
    """Calculate cyclomatic complexity of Python code"""

    def __init__(self):
        self.complexity = 1  # Base complexity is 1
        self.function_complexity = {}
        self.current_function = None

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_Except(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # Count 'and' and 'or' operators
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Store previous complexity
        prev_complexity = self.complexity
        self.complexity = 1
        old_function = self.current_function
        self.current_function = node.name

        self.generic_visit(node)

        # Store function complexity and restore
        self.function_complexity[node.name] = self.complexity
        self.complexity = prev_complexity
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Lambda(self, node):
        self.complexity += 1
        self.generic_visit(node)


class ComplexityAnalyzer:
    """Analyzes code complexity metrics"""

    def __init__(self, cyclomatic_threshold: int = 10, loc_threshold: int = 200):
        self.cyclomatic_threshold = cyclomatic_threshold
        self.loc_threshold = loc_threshold

    def analyze_file(self, file_path: str) -> Optional[ComplexityMetrics]:
        """Analyze complexity metrics for a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return None

        loc = self._count_lines_of_code(lines)
        
        # For Python files, use AST analysis
        if file_path.endswith('.py'):
            try:
                tree = ast.parse(content)
                visitor = CyclomaticComplexityVisitor()
                visitor.visit(tree)
                cyclomatic = visitor.complexity
            except:
                # If AST parsing fails, use heuristic
                cyclomatic = self._estimate_complexity_heuristic(lines)
        else:
            cyclomatic = self._estimate_complexity_heuristic(lines)

        cognitive = self._estimate_cognitive_complexity(lines)
        maintainability_index = self._calculate_maintainability_index(loc, cyclomatic, cognitive)
        risk_level = self._determine_complexity_risk(cyclomatic, loc)

        return ComplexityMetrics(
            file_path=file_path,
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            maintainability_index=maintainability_index,
            risk_level=risk_level
        )

    def analyze_directory(self, directory: str, ignore_patterns: List[str] = None) -> List[ComplexityMetrics]:
        """Analyze complexity for all files in directory"""
        metrics = []
        ignore_patterns = ignore_patterns or []
        supported_extensions = ['.py', '.js', '.java', '.go', '.rb', '.php', '.ts', '.cpp', '.c']

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not any(p in d for p in ignore_patterns)]

            for file in files:
                file_path = os.path.join(root, file)
                
                if any(p in file_path for p in ignore_patterns):
                    continue

                _, ext = os.path.splitext(file_path)
                if ext.lower() in supported_extensions:
                    metric = self.analyze_file(file_path)
                    if metric:
                        metrics.append(metric)

        return metrics

    def _count_lines_of_code(self, lines: List[str]) -> int:
        """Count lines of actual code (excluding blanks and comments)"""
        loc = 0
        in_multiline_comment = False

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Handle multiline comments (Python and others)
            if '"""' in stripped or "'''" in stripped:
                in_multiline_comment = not in_multiline_comment
                continue

            if in_multiline_comment:
                continue

            # Skip pure comment lines
            if stripped.startswith('#') or stripped.startswith('//'):
                continue

            loc += 1

        return loc

    def _estimate_complexity_heuristic(self, lines: List[str]) -> int:
        """Estimate cyclomatic complexity using heuristics for non-Python files"""
        complexity = 1
        
        for line in lines:
            stripped = line.strip()
            
            # Skip comments and empty lines
            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue

            # Count decision points
            if any(keyword in stripped for keyword in ['if', 'else', 'elif', 'switch', 'case']):
                complexity += 1
            if any(keyword in stripped for keyword in ['for', 'while', 'do']):
                complexity += 1
            if '||' in stripped or ' or ' in stripped.lower():
                complexity += 1
            if '&&' in stripped or ' and ' in stripped.lower():
                complexity += 1
            if '?' in stripped and ':' in stripped:  # Ternary operator
                complexity += 1
            if 'catch' in stripped or 'except' in stripped:
                complexity += 1

        return complexity

    def _estimate_cognitive_complexity(self, lines: List[str]) -> int:
        """Estimate cognitive complexity (how hard to understand)"""
        complexity = 0
        nesting_level = 0

        for line in lines:
            stripped = line.strip()

            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue

            # Count nesting (indentation indicates nesting)
            indent = len(line) - len(line.lstrip())
            nesting_level = indent // 4  # Assuming 4-space indentation

            # Cognitive complexity increases with nesting
            if any(keyword in stripped for keyword in ['if', 'for', 'while', 'switch', 'try']):
                complexity += 1 + nesting_level

        return complexity

    def _calculate_maintainability_index(self, loc: int, cyclomatic: int, cognitive: int) -> float:
        """
        Calculate maintainability index (0-100)
        Based on lines of code, cyclomatic complexity, and cognitive complexity
        """
        # Formula: 171 - 5.2 * ln(halstead_volume) - 0.23 * cyclomatic - 16.2 * ln(loc)
        # Simplified version using available metrics
        import math

        if loc <= 0:
            return 100.0

        score = 100.0
        
        # Penalize for high lines of code
        if loc > 200:
            score -= (loc - 200) * 0.1
        
        # Penalize for high cyclomatic complexity
        if cyclomatic > 10:
            score -= (cyclomatic - 10) * 2
        
        # Penalize for high cognitive complexity
        if cognitive > 15:
            score -= (cognitive - 15) * 0.5

        return max(0.0, min(100.0, score))

    def _determine_complexity_risk(self, cyclomatic: int, loc: int) -> RiskLevel:
        """Determine risk level based on complexity metrics"""
        # Both high cyclomatic complexity and high LOC increase risk
        complexity_risk_score = min(cyclomatic / 30.0, 1.0)  # Normalize to 0-1
        loc_risk_score = min(loc / 500.0, 1.0)  # Normalize to 0-1
        
        combined_score = (complexity_risk_score * 0.6) + (loc_risk_score * 0.4)

        if combined_score >= 0.8:
            return RiskLevel.CRITICAL
        elif combined_score >= 0.6:
            return RiskLevel.HIGH
        elif combined_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


class DummyComplexityAnalyzer:
    """Generates realistic dummy complexity metrics"""

    def __init__(self, cyclomatic_threshold: int = 10, loc_threshold: int = 200):
        self.cyclomatic_threshold = cyclomatic_threshold
        self.loc_threshold = loc_threshold

    def analyze_file(self, file_path: str) -> Optional[ComplexityMetrics]:
        """Generate dummy complexity metrics"""
        import random

        seed = hash(file_path) % 2**32
        random.seed(seed)

        cyclomatic = random.randint(2, 40) if random.random() > 0.3 else random.randint(5, 15)
        cognitive = random.randint(5, 50)
        loc = random.randint(50, 500) if random.random() > 0.4 else random.randint(100, 300)
        
        # Maintainability index (100 = best, 0 = worst)
        maintainability = 100 - (cyclomatic * 2) - (cognitive * 0.5) - (loc * 0.05)
        maintainability = max(10, min(100, maintainability))

        # Risk based on metrics
        if cyclomatic > 25 or loc > 400:
            risk_level = RiskLevel.CRITICAL
        elif cyclomatic > 15 or loc > 250:
            risk_level = RiskLevel.HIGH
        elif cyclomatic > 10 or loc > 150:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return ComplexityMetrics(
            file_path=file_path,
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            maintainability_index=maintainability,
            risk_level=risk_level
        )

    def analyze_directory(self, directory: str, ignore_patterns: List[str] = None) -> List[ComplexityMetrics]:
        """Generate dummy metrics for all files"""
        metrics = []
        ignore_patterns = ignore_patterns or []
        supported_extensions = ['.py', '.js', '.java', '.go', '.rb', '.php', '.ts', '.cpp', '.c']

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not any(p in d for p in ignore_patterns)]

            for file in files:
                file_path = os.path.join(root, file)
                
                if any(p in file_path for p in ignore_patterns):
                    continue

                _, ext = os.path.splitext(file_path)
                if ext.lower() in supported_extensions:
                    metric = self.analyze_file(file_path)
                    if metric:
                        metrics.append(metric)

        return metrics
