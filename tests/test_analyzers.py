"""Unit tests for analyzers"""

import pytest
import tempfile
import os
from pathlib import Path

from src.analyzers.security_analyzer import SecurityAnalyzer
from src.analyzers.complexity_analyzer import ComplexityAnalyzer
from src.models import RiskLevel


class TestSecurityAnalyzer:
    """Test security vulnerability detection"""

    def setup_method(self):
        self.analyzer = SecurityAnalyzer()

    def test_detect_hardcoded_api_key(self, tmp_path):
        """Test detection of hardcoded API key"""
        test_file = tmp_path / "test.py"
        test_file.write_text('api_key = "sk_live_123456789abc"')

        issues = self.analyzer.analyze_file(str(test_file))
        
        assert len(issues) > 0
        assert any('secret' in i.issue_type.lower() or 'key' in i.issue_type.lower() for i in issues)

    def test_detect_unsafe_eval(self, tmp_path):
        """Test detection of eval() usage"""
        test_file = tmp_path / "test.py"
        test_file.write_text('result = eval(user_input)')

        issues = self.analyzer.analyze_file(str(test_file))
        
        assert len(issues) > 0
        assert any('eval' in i.issue_type.lower() for i in issues)

    def test_no_issues_in_clean_code(self, tmp_path):
        """Test clean code doesn't trigger false positives"""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
def greet(name):
    """Return a greeting"""
    return f"Hello, {name}!"

message = greet("World")
print(message)
''')

        issues = self.analyzer.analyze_file(str(test_file))
        assert len(issues) == 0


class TestComplexityAnalyzer:
    """Test code complexity analysis"""

    def setup_method(self):
        self.analyzer = ComplexityAnalyzer()

    def test_simple_function_low_complexity(self, tmp_path):
        """Test simple function has low complexity"""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
def add(a, b):
    return a + b
''')

        metrics = self.analyzer.analyze_file(str(test_file))
        
        assert metrics is not None
        assert metrics.cyclomatic_complexity <= 3

    def test_complex_function_high_complexity(self, tmp_path):
        """Test complex function has high complexity"""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
            elif z < 0:
                return x + y - z
            else:
                return x + y
        elif y < 0:
            return x - y
        else:
            return x
    elif x < 0:
        return -x
    else:
        return 0
''')

        metrics = self.analyzer.analyze_file(str(test_file))
        
        assert metrics is not None
        assert metrics.cyclomatic_complexity > 5

    def test_high_loc_detected(self, tmp_path):
        """Test detection of high lines of code"""
        test_file = tmp_path / "test.py"
        
        # Create a file with many lines
        lines = ["x = 1"] * 250
        test_file.write_text('\n'.join(lines))

        metrics = self.analyzer.analyze_file(str(test_file))
        
        assert metrics is not None
        assert metrics.lines_of_code > 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
