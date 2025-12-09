"""Test coverage analysis and insights"""

from dataclasses import dataclass
from typing import List, Dict
import os
import re
from pathlib import Path
from src.models import RiskReport


@dataclass
class CoverageGap:
    """Untested code area"""
    file_path: str
    risk_level: str
    lines_uncovered: int
    critical_functions: List[str]
    recommendation: str


@dataclass
class TestCoverageSummary:
    """Test coverage analysis results"""
    coverage_percentage: float
    files_with_tests: int
    files_without_tests: int
    critical_untested: int
    test_coverage_gaps: List[CoverageGap]
    testing_recommendations: List[str]
    test_debt_priority: str


class TestCoverageAnalyzer:
    """Analyzes test coverage and identifies gaps"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def analyze_coverage(self, report: RiskReport) -> TestCoverageSummary:
        """Analyze test coverage for analyzed modules"""
        
        # Find test files
        test_files = self._find_test_files()
        
        # Map test files to source files
        covered_files = self._map_test_coverage(test_files)
        
        # Identify gaps
        gaps = []
        critical_untested = 0
        
        for module in report.modules:
            if module.file_path not in covered_files:
                if module.risk_level.value in ['CRITICAL', 'HIGH']:
                    critical_untested += 1
                    
                    # Extract function names
                    functions = self._extract_function_names(module.file_path)
                    
                    gap = CoverageGap(
                        file_path=module.file_path,
                        risk_level=module.risk_level.value,
                        lines_uncovered=max(int(100), int(module.complexity_risk * 2)),
                        critical_functions=functions[:5],
                        recommendation=f"URGENT: Add tests for {module.risk_level.value} risk module. Start with: {', '.join(functions[:2])}"
                    )
                    gaps.append(gap)
        
        # Calculate coverage percentage
        total_modules = len(report.modules)
        covered_count = len(covered_files)
        coverage_pct = (covered_count / total_modules * 100) if total_modules > 0 else 0
        
        # Generate recommendations
        recs = self._generate_recommendations(coverage_pct, critical_untested, gaps)
        
        return TestCoverageSummary(
            coverage_percentage=coverage_pct,
            files_with_tests=covered_count,
            files_without_tests=total_modules - covered_count,
            critical_untested=critical_untested,
            test_coverage_gaps=gaps[:15],
            testing_recommendations=recs,
            test_debt_priority='CRITICAL' if critical_untested > 5 else 'HIGH' if critical_untested > 0 else 'MEDIUM'
        )

    def _find_test_files(self) -> List[str]:
        """Find all test files in repository"""
        test_files = []
        test_patterns = ['test_*.py', '*_test.py', 'test*.js', 'spec*.js']
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip node_modules and venv
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.venv', '__pycache__']]
            
            for file in files:
                for pattern in test_patterns:
                    if file.lower().endswith(pattern.replace('*', '')):
                        test_files.append(os.path.join(root, file))
        
        return test_files

    def _map_test_coverage(self, test_files: List[str]) -> set:
        """Map test files to covered source files"""
        covered = set()
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Extract import statements
                    imports = re.findall(r'(?:from|import)\s+[\w\.]+\s+(?:import\s+)?[\w\*]+', content)
                    
                    for imp in imports:
                        # Convert import to file path
                        if 'from' in imp:
                            module = imp.split('from')[1].split('import')[0].strip()
                        else:
                            module = imp.split('import')[1].strip()
                        
                        # Try to match with source files
                        module_path = module.replace('.', os.sep)
                        covered.add(module_path)
            except:
                pass
        
        return covered

    def _extract_function_names(self, file_path: str) -> List[str]:
        """Extract function names from file"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Find function definitions
                if file_path.endswith('.py'):
                    pattern = r'def\s+(\w+)\s*\('
                elif file_path.endswith('.js') or file_path.endswith('.ts'):
                    pattern = r'(?:function|const|let)\s+(\w+)\s*[=\(]'
                else:
                    pattern = r'(?:function|def|public)\s+(\w+)\s*\('
                
                matches = re.findall(pattern, content)
                functions = list(set(matches))[:10]  # Unique, limit to 10
        except:
            functions = ['main', 'process', 'handle', 'parse']
        
        return functions

    def _generate_recommendations(self, coverage: float, critical_untested: int, gaps: List[CoverageGap]) -> List[str]:
        """Generate testing recommendations"""
        recs = []
        
        if coverage < 50:
            recs.append("URGENT: Test coverage below 50%. Implement comprehensive test strategy immediately.")
        elif coverage < 70:
            recs.append(f"Test coverage at {coverage:.1f}%. Improve to 80%+ for production readiness.")
        else:
            recs.append(f"Good test coverage ({coverage:.1f}%). Focus on critical paths and edge cases.")
        
        if critical_untested > 0:
            recs.append(f"CRITICAL: {critical_untested} CRITICAL/HIGH risk modules have NO tests. This is unacceptable.")
            if critical_untested > 0 and gaps:
                recs.append(f"Start with: {gaps[0].file_path}")
        
        recs.append("Use pytest (Python) or Jest (JavaScript) for unit tests.")
        recs.append("Aim for 80%+ coverage on critical paths (security, payments, core logic).")
        
        return recs


class DummyTestCoverageAnalyzer:
    """Dummy test coverage analyzer for testing"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def analyze_coverage(self, report: RiskReport) -> TestCoverageSummary:
        """Generate realistic coverage analysis"""
        return TestCoverageSummary(
            coverage_percentage=62.5,
            files_with_tests=18,
            files_without_tests=11,
            critical_untested=3,
            test_coverage_gaps=[
                CoverageGap(
                    file_path="src/payments/processor.py",
                    risk_level="CRITICAL",
                    lines_uncovered=450,
                    critical_functions=["process_payment", "validate_card", "handle_error"],
                    recommendation="URGENT: Payment processor CRITICAL with no tests. Add comprehensive test suite immediately."
                ),
                CoverageGap(
                    file_path="src/auth/jwt_handler.py",
                    risk_level="CRITICAL",
                    lines_uncovered=280,
                    critical_functions=["verify_token", "decode_jwt", "validate_signature"],
                    recommendation="URGENT: Auth handler untested. Security risk. Add unit tests for all functions."
                ),
                CoverageGap(
                    file_path="src/database/migration.py",
                    risk_level="HIGH",
                    lines_uncovered=320,
                    critical_functions=["run_migration", "rollback", "validate_schema"],
                    recommendation="HIGH: Migration logic needs tests. Add integration tests before production deploys."
                ),
            ],
            testing_recommendations=[
                "Test coverage at 62.5%. Improve to 80%+ for production readiness.",
                "CRITICAL: 3 CRITICAL/HIGH risk modules have NO tests. This is unacceptable.",
                "Start with: src/payments/processor.py",
                "Use pytest (Python) or Jest (JavaScript) for unit tests.",
                "Aim for 80%+ coverage on critical paths (security, payments, core logic)."
            ],
            test_debt_priority="HIGH"
        )
