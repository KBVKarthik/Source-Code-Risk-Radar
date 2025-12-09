"""Security vulnerability pattern detection"""

import os
import re
from typing import List, Dict, Optional, Set
from pathlib import Path

from src.models import SecurityIssue, RiskLevel


class SecurityAnalyzer:
    """Analyzes code for security vulnerabilities and risky patterns"""

    # Patterns for detecting hardcoded secrets
    SECRET_PATTERNS = {
        'api_key': r"(?i)(api[_-]?key|apikey)\s*=\s*['\"]([a-zA-Z0-9_-]+)['\"]",
        'aws_key': r"(?i)(aws[_-]?access[_-]?key|aws[_-]?secret)\s*=\s*['\"]([A-Z0-9]+)['\"]",
        'password': r"(?i)(password|passwd)\s*=\s*['\"]([^'\"]+)['\"]",
        'token': r"(?i)(token|auth[_-]?token|refresh[_-]?token)\s*=\s*['\"]([a-zA-Z0-9._-]+)['\"]",
        'private_key': r"(?i)(private[_-]?key|pk|pem)\s*=\s*['\"]([a-zA-Z0-9+/=]+)['\"]",
        'connection_string': r"(?i)(connection[_-]?string|db[_-]?url)\s*=\s*['\"]([^'\"]+)['\"]",
        'jwt': r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
    }

    # Unsafe functions that should be flagged
    UNSAFE_FUNCTIONS = {
        'eval': {'severity': RiskLevel.CRITICAL, 'description': 'eval() can execute arbitrary code'},
        'exec': {'severity': RiskLevel.CRITICAL, 'description': 'exec() can execute arbitrary code'},
        'compile': {'severity': RiskLevel.HIGH, 'description': 'compile() combined with eval is dangerous'},
        '__import__': {'severity': RiskLevel.HIGH, 'description': 'Dynamic imports can be exploited'},
        'pickle.loads': {'severity': RiskLevel.CRITICAL, 'description': 'pickle.loads() can execute arbitrary code'},
        'pickle.load': {'severity': RiskLevel.CRITICAL, 'description': 'pickle.load() can execute arbitrary code'},
        'yaml.load': {'severity': RiskLevel.HIGH, 'description': 'YAML unsafe load can execute code'},
        'shelve': {'severity': RiskLevel.CRITICAL, 'description': 'shelve uses pickle and is unsafe'},
        'subprocess.call': {'severity': RiskLevel.HIGH, 'description': 'subprocess.call() with shell=True is dangerous'},
        'subprocess.Popen': {'severity': RiskLevel.MEDIUM, 'description': 'subprocess.Popen() can be vulnerable if shell=True'},
        'os.system': {'severity': RiskLevel.CRITICAL, 'description': 'os.system() is vulnerable to shell injection'},
        'os.popen': {'severity': RiskLevel.CRITICAL, 'description': 'os.popen() is vulnerable to shell injection'},
        'globals': {'severity': RiskLevel.HIGH, 'description': 'Using globals() can be exploited'},
        'locals': {'severity': RiskLevel.HIGH, 'description': 'Using locals() can be exploited'},
    }

    # SQL/NoSQL injection patterns
    SQL_PATTERNS = {
        'sql_injection': r"(?i)(execute|query)\s*\(\s*['\"].*\{.*\}",
        'mongodb_injection': r"(?i)(find|findOne|update|insert)\s*\(\s*\{.*\$.*\}",
    }

    # Other vulnerability patterns
    VULNERABILITY_PATTERNS = {
        'hardcoded_ip': r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
        'debug_mode_enabled': r"(?i)(debug\s*=\s*true|debug_mode|DEBUG)",
        'logging_sensitive_data': r"(?i)(log|print)\s*\(\s*['\"].*(?:password|token|key|secret|credit)",
    }

    EXCLUDED_PATTERNS = {
        'comments': r"^\s*#",
        'docstring': r'^\s*["\']',
    }

    def __init__(self, extensions: List[str] = None):
        """
        Initialize analyzer
        
        Args:
            extensions: File extensions to analyze (default: .py, .js, .java, .go, .rb, .php, .ts)
        """
        self.extensions = extensions or ['.py', '.js', '.java', '.go', '.rb', '.php', '.ts', '.cpp', '.c']

    def analyze_file(self, file_path: str) -> List[SecurityIssue]:
        """Analyze a single file for security issues"""
        issues = []

        if not self._should_analyze(file_path):
            return issues

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return issues

        for line_num, line in enumerate(lines, 1):
            # Skip comments and empty lines
            if self._is_excluded_line(line):
                continue

            # Check for hardcoded secrets
            secret_issues = self._check_secrets(file_path, line, line_num)
            issues.extend(secret_issues)

            # Check for unsafe functions
            unsafe_issues = self._check_unsafe_functions(file_path, line, line_num)
            issues.extend(unsafe_issues)

            # Check for SQL injection patterns
            sql_issues = self._check_sql_injection(file_path, line, line_num)
            issues.extend(sql_issues)

            # Check for other vulnerabilities
            vuln_issues = self._check_vulnerabilities(file_path, line, line_num)
            issues.extend(vuln_issues)

        return issues

    def analyze_directory(self, directory: str, ignore_patterns: List[str] = None) -> List[SecurityIssue]:
        """Recursively analyze all files in a directory"""
        all_issues = []
        ignore_patterns = ignore_patterns or []

        for root, dirs, files in os.walk(directory):
            # Filter directories
            dirs[:] = [d for d in dirs if not any(p in d for p in ignore_patterns)]

            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip ignored patterns
                if any(p in file_path for p in ignore_patterns):
                    continue

                if self._should_analyze(file_path):
                    issues = self.analyze_file(file_path)
                    all_issues.extend(issues)

        return all_issues

    def _should_analyze(self, file_path: str) -> bool:
        """Check if file should be analyzed"""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.extensions

    def _is_excluded_line(self, line: str) -> bool:
        """Check if line should be excluded from analysis"""
        stripped = line.strip()
        if not stripped:
            return True
        for pattern in self.EXCLUDED_PATTERNS.values():
            if re.match(pattern, stripped):
                return True
        return False

    def _check_secrets(self, file_path: str, line: str, line_num: int) -> List[SecurityIssue]:
        """Check for hardcoded secrets"""
        issues = []
        for secret_type, pattern in self.SECRET_PATTERNS.items():
            matches = re.finditer(pattern, line)
            for match in matches:
                issue = SecurityIssue(
                    file_path=file_path,
                    line_number=line_num,
                    issue_type=f'hardcoded_secret_{secret_type}',
                    severity=RiskLevel.CRITICAL,
                    description=f'Hardcoded {secret_type.replace("_", " ")} detected',
                    snippet=line.strip()[:100],
                    recommendation=f'Remove hardcoded {secret_type.replace("_", " ")} and use environment variables or secrets management'
                )
                issues.append(issue)
        return issues

    def _check_unsafe_functions(self, file_path: str, line: str, line_num: int) -> List[SecurityIssue]:
        """Check for usage of unsafe functions"""
        issues = []
        for func_name, info in self.UNSAFE_FUNCTIONS.items():
            # Use word boundary to avoid false positives
            pattern = r'\b' + re.escape(func_name) + r'\s*\('
            if re.search(pattern, line, re.IGNORECASE):
                issue = SecurityIssue(
                    file_path=file_path,
                    line_number=line_num,
                    issue_type=f'unsafe_function_{func_name}',
                    severity=info['severity'],
                    description=info['description'],
                    snippet=line.strip()[:100],
                    recommendation=f'Avoid using {func_name}(). Use safer alternatives.'
                )
                issues.append(issue)
        return issues

    def _check_sql_injection(self, file_path: str, line: str, line_num: int) -> List[SecurityIssue]:
        """Check for SQL injection vulnerabilities"""
        issues = []
        for vuln_type, pattern in self.SQL_PATTERNS.items():
            if re.search(pattern, line):
                issue = SecurityIssue(
                    file_path=file_path,
                    line_number=line_num,
                    issue_type=vuln_type,
                    severity=RiskLevel.CRITICAL,
                    description=f'Potential {vuln_type.replace("_", " ")} detected',
                    snippet=line.strip()[:100],
                    recommendation='Use parameterized queries or ORM to prevent injection attacks'
                )
                issues.append(issue)
        return issues

    def _check_vulnerabilities(self, file_path: str, line: str, line_num: int) -> List[SecurityIssue]:
        """Check for other security issues"""
        issues = []
        
        # Check for debug mode
        if re.search(self.VULNERABILITY_PATTERNS['debug_mode_enabled'], line):
            issue = SecurityIssue(
                file_path=file_path,
                line_number=line_num,
                issue_type='debug_mode_enabled',
                severity=RiskLevel.HIGH,
                description='Debug mode appears to be enabled',
                snippet=line.strip()[:100],
                recommendation='Disable debug mode in production'
            )
            issues.append(issue)

        # Check for logging sensitive data
        if re.search(self.VULNERABILITY_PATTERNS['logging_sensitive_data'], line):
            issue = SecurityIssue(
                file_path=file_path,
                line_number=line_num,
                issue_type='logging_sensitive_data',
                severity=RiskLevel.HIGH,
                description='Potential sensitive data being logged',
                snippet=line.strip()[:100],
                recommendation='Do not log passwords, tokens, keys, or credit card information'
            )
            issues.append(issue)

        return issues


class DummySecurityAnalyzer:
    """Generates realistic dummy security issues for testing"""

    ISSUE_TYPES = [
        'hardcoded_secret_api_key',
        'unsafe_function_eval',
        'unsafe_function_pickle',
        'sql_injection',
        'debug_mode_enabled',
        'logging_sensitive_data',
    ]

    def __init__(self, extensions: List[str] = None):
        self.extensions = extensions or ['.py', '.js', '.java', '.go', '.rb', '.php', '.ts']

    def analyze_file(self, file_path: str) -> List[SecurityIssue]:
        """Generate dummy security issues for a file"""
        import random
        
        issues = []
        
        # Use file hash for reproducibility
        seed = hash(file_path) % 2**32
        random.seed(seed)

        # 30% of files have security issues
        if random.random() > 0.7:
            num_issues = random.randint(1, 3)
            for _ in range(num_issues):
                issue_type = random.choice(self.ISSUE_TYPES)
                
                severity_map = {
                    'hardcoded_secret_api_key': RiskLevel.CRITICAL,
                    'unsafe_function_eval': RiskLevel.CRITICAL,
                    'unsafe_function_pickle': RiskLevel.CRITICAL,
                    'sql_injection': RiskLevel.CRITICAL,
                    'debug_mode_enabled': RiskLevel.HIGH,
                    'logging_sensitive_data': RiskLevel.HIGH,
                }

                issue = SecurityIssue(
                    file_path=file_path,
                    line_number=random.randint(5, 150),
                    issue_type=issue_type,
                    severity=severity_map.get(issue_type, RiskLevel.MEDIUM),
                    description=f'{issue_type.replace("_", " ")} detected',
                    snippet=f"Sample code snippet from {file_path}",
                    recommendation='Review and fix this security issue'
                )
                issues.append(issue)

        return issues

    def analyze_directory(self, directory: str, ignore_patterns: List[str] = None) -> List[SecurityIssue]:
        """Generate dummy security issues for all files"""
        all_issues = []
        ignore_patterns = ignore_patterns or []

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not any(p in d for p in ignore_patterns)]

            for file in files:
                file_path = os.path.join(root, file)
                if any(p in file_path for p in ignore_patterns):
                    continue

                _, ext = os.path.splitext(file_path)
                if ext.lower() in self.extensions:
                    issues = self.analyze_file(file_path)
                    all_issues.extend(issues)

        return all_issues
