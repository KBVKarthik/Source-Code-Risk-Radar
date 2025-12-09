"""Main analysis orchestrator"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from src.models import (
    RiskReport, ModuleRisk, RiskLevel, AnalysisMetadata,
    SecurityIssue, ComplexityMetrics, GitMetrics, DependencyRisk
)
from src.analyzers.git_analyzer import GitAnalyzer, DummyGitAnalyzer
from src.analyzers.security_analyzer import SecurityAnalyzer, DummySecurityAnalyzer
from src.analyzers.complexity_analyzer import ComplexityAnalyzer, DummyComplexityAnalyzer
from src.analyzers.dependency_analyzer import DependencyAnalyzer, DummyDependencyAnalyzer
from src.ml_models.failure_predictor import FailurePredictor, DummyFailurePredictor


class RiskRadar:
    """Main orchestrator for risk analysis"""

    def __init__(self, repo_path: str, config: Dict = None, use_dummy_data: bool = False):
        self.repo_path = repo_path
        self.config = config or self._default_config()
        self.use_dummy_data = use_dummy_data
        self.use_git = self._check_git_available() and not use_dummy_data

        # Initialize analyzers
        if use_dummy_data or not self.use_git:
            self.git_analyzer = DummyGitAnalyzer(repo_path)
        else:
            self.git_analyzer = GitAnalyzer(repo_path)

        self.security_analyzer = SecurityAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        
        if use_dummy_data:
            self.dependency_analyzer = DummyDependencyAnalyzer()
            self.failure_predictor = DummyFailurePredictor()
        else:
            self.dependency_analyzer = DependencyAnalyzer()
            self.failure_predictor = FailurePredictor()
            self.failure_predictor.train_on_dummy_data()

    def analyze(self) -> RiskReport:
        """Execute complete risk analysis"""
        start_time = datetime.now()

        # Collect all files to analyze
        files_to_analyze = self._get_files_to_analyze()
        print(f"Found {len(files_to_analyze)} files to analyze")

        # Run analyzers
        all_modules = {}

        # 1. Git analysis
        print("Running git analysis...")
        git_metrics_list = self._analyze_git(files_to_analyze)
        git_metrics_dict = {m.file_path: m for m in git_metrics_list}

        # 2. Security analysis
        print("Running security analysis...")
        security_issues = self._analyze_security(files_to_analyze)

        # 3. Complexity analysis
        print("Running complexity analysis...")
        complexity_metrics = self._analyze_complexity(files_to_analyze)
        complexity_dict = {m.file_path: m for m in complexity_metrics}

        # 4. Dependency analysis
        print("Running dependency analysis...")
        dependency_risks = self._analyze_dependencies()

        # 5. ML failure prediction
        print("Running failure prediction...")
        file_metrics_for_ml = self._prepare_ml_features(
            git_metrics_dict, complexity_dict, security_issues
        )
        failure_predictions = self.failure_predictor.predict_failures(file_metrics_for_ml)

        # 6. Aggregate results
        print("Aggregating results...")
        modules = self._aggregate_module_risks(
            git_metrics_dict, complexity_dict, security_issues, failure_predictions
        )

        # Create metadata
        metadata = AnalysisMetadata(
            repository_path=self.repo_path,
            analysis_timestamp=datetime.now(),
            total_files_analyzed=len(files_to_analyze),
            total_lines_of_code=sum(m.lines_of_code for m in complexity_metrics),
            analysis_duration_seconds=(datetime.now() - start_time).total_seconds(),
            git_commits_analyzed=len(git_metrics_dict),
            python_version=self._get_python_version(),
            analysis_type='full'
        )

        # Create report
        report = RiskReport(
            metadata=metadata,
            modules=modules,
            security_issues=security_issues,
            complexity_metrics=complexity_metrics,
            git_metrics=git_metrics_list,
            dependency_risks=dependency_risks,
            high_risk_modules=[m for m in modules if m.overall_risk_score >= 60],
            critical_modules=[m for m in modules if m.overall_risk_score >= 80],
            failure_predictions=failure_predictions
        )

        return report

    def _get_files_to_analyze(self) -> List[str]:
        """Get all files to analyze"""
        files = []
        supported_extensions = ['.py', '.js', '.java', '.go', '.rb', '.php', '.ts', '.cpp', '.c']
        ignore_patterns = self.config['analysis'].get('ignore_patterns', [])

        for root, dirs, file_list in os.walk(self.repo_path):
            # Filter directories
            dirs[:] = [d for d in dirs if not any(p in d for p in ignore_patterns)]

            for file in file_list:
                file_path = os.path.join(root, file)
                
                # Skip ignored paths
                if any(p in file_path for p in ignore_patterns):
                    continue

                _, ext = os.path.splitext(file)
                if ext.lower() in supported_extensions:
                    files.append(file_path)

        return files

    def _analyze_git(self, files: List[str]) -> List[GitMetrics]:
        """Analyze git metrics for files"""
        metrics = []
        for i, file_path in enumerate(files):
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(files)} files")
            
            metric = self.git_analyzer.get_git_metrics(file_path)
            if metric:
                metrics.append(metric)

        return metrics

    def _analyze_security(self, files: List[str]) -> List[SecurityIssue]:
        """Analyze security issues"""
        all_issues = []
        for i, file_path in enumerate(files):
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(files)} files")
            
            issues = self.security_analyzer.analyze_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def _analyze_complexity(self, files: List[str]) -> List[ComplexityMetrics]:
        """Analyze code complexity"""
        metrics = []
        for i, file_path in enumerate(files):
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(files)} files")
            
            metric = self.complexity_analyzer.analyze_file(file_path)
            if metric:
                metrics.append(metric)

        return metrics

    def _analyze_dependencies(self) -> List[DependencyRisk]:
        """Analyze dependencies"""
        return self.dependency_analyzer.scan_directory(self.repo_path)

    def _prepare_ml_features(self, git_dict, complexity_dict, security_issues) -> List[Dict]:
        """Prepare features for ML prediction"""
        features_list = []

        # Count security issues by file
        security_by_file = {}
        for issue in security_issues:
            if issue.file_path not in security_by_file:
                security_by_file[issue.file_path] = 0
            security_by_file[issue.file_path] += 1

        # Combine metrics
        all_files = set(git_dict.keys()) | set(complexity_dict.keys())

        for file_path in all_files:
            features = {
                'file_path': file_path,
                'churn_rate': git_dict[file_path].churn_score if file_path in git_dict else 0.0,
                'cyclomatic_complexity': complexity_dict[file_path].cyclomatic_complexity if file_path in complexity_dict else 5,
                'file_age_months': (datetime.now() - git_dict[file_path].creation_date).days / 30 if file_path in git_dict else 6,
                'commit_frequency': git_dict[file_path].modification_frequency if file_path in git_dict else 2.0,
                'author_count': git_dict[file_path].unique_authors if file_path in git_dict else 1,
                'bus_factor': git_dict[file_path].bus_factor if file_path in git_dict else 1,
                'recent_changes': git_dict[file_path].total_commits if file_path in git_dict else 0,
                'test_coverage_proxy': 0.5,  # Default assumption
                'lines_of_code': complexity_dict[file_path].lines_of_code if file_path in complexity_dict else 100,
            }
            features_list.append(features)

        return features_list

    def _aggregate_module_risks(self, git_dict, complexity_dict, security_issues, failure_predictions) -> List[ModuleRisk]:
        """Aggregate all metrics into module risk scores"""
        modules = []

        # Count issues by file
        issues_by_file = {}
        for issue in security_issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)

        # Create failure dict for quick lookup
        failure_dict = {p['file_path']: p for p in failure_predictions}

        # Process all files
        all_files = set(git_dict.keys()) | set(complexity_dict.keys()) | set(issues_by_file.keys())

        for file_path in all_files:
            git_m = git_dict.get(file_path)
            comp_m = complexity_dict.get(file_path)
            sec_issues = issues_by_file.get(file_path, [])
            failure = failure_dict.get(file_path, {})

            # Calculate risk scores
            complexity_risk = (comp_m.cyclomatic_complexity / 30.0) * 100 if comp_m else 0
            security_risk = len(sec_issues) * 20  # Each issue adds risk
            churn_risk = (git_m.churn_score * 100) if git_m else 0
            bus_factor_risk = 1.0 if (git_m and git_m.bus_factor == 1) else 0.0
            failure_prob = failure.get('failure_probability', 0.0)
            dependency_risk = 0.0  # Will add more if file is a dependency

            # Cap scores at 100
            complexity_risk = min(complexity_risk, 100)
            security_risk = min(security_risk, 100)
            churn_risk = min(churn_risk, 100)

            # Calculate weighted overall risk
            overall_risk = (
                complexity_risk * 0.25 +
                security_risk * 0.30 +
                churn_risk * 0.20 +
                bus_factor_risk * 25 +
                failure_prob * 100 * 0.25 +
                dependency_risk * 0.05
            )
            overall_risk = min(overall_risk, 100)

            # Determine risk level
            if overall_risk >= 80:
                risk_level = RiskLevel.CRITICAL
            elif overall_risk >= 60:
                risk_level = RiskLevel.HIGH
            elif overall_risk >= 40:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW

            # Get recommendations
            recommendations = self._get_recommendations(
                complexity_risk, security_risk, churn_risk, bus_factor_risk, failure_prob
            )

            # Get owners
            owners = []
            if git_m:
                owners = [f"Author count: {git_m.unique_authors}"]

            module = ModuleRisk(
                file_path=file_path,
                complexity_risk=complexity_risk,
                security_risk=security_risk,
                churn_risk=churn_risk,
                bus_factor_risk=bus_factor_risk,
                failure_probability=failure_prob,
                dependency_risk=dependency_risk,
                overall_risk_score=overall_risk,
                risk_level=risk_level,
                primary_owners=owners,
                critical_issues=[f"{i.issue_type}" for i in sec_issues],
                recommendations=recommendations
            )
            modules.append(module)

        # Sort by risk score
        modules.sort(key=lambda m: m.overall_risk_score, reverse=True)
        return modules

    def _get_recommendations(self, complexity_risk, security_risk, churn_risk, bus_factor_risk, failure_prob) -> List[str]:
        """Generate recommendations based on risk scores"""
        recommendations = []

        if security_risk > 50:
            recommendations.append("Address security vulnerabilities immediately")

        if complexity_risk > 70:
            recommendations.append("Refactor to reduce cyclomatic complexity")

        if churn_risk > 60:
            recommendations.append("Stabilize code - high change frequency indicates instability")

        if bus_factor_risk > 0.5:
            recommendations.append("Mitigate bus factor - documentation and pair programming needed")

        if failure_prob > 0.6:
            recommendations.append("High failure probability - prioritize testing and refactoring")

        if not recommendations:
            recommendations.append("Monitor and maintain current quality standards")

        return recommendations

    def _check_git_available(self) -> bool:
        """Check if git is available and repo is valid"""
        try:
            result = os.system("git --version > NUL 2>&1")
            return result == 0
        except:
            return False

    def _get_python_version(self) -> str:
        """Get Python version"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    @staticmethod
    def _default_config() -> Dict:
        """Get default configuration"""
        return {
            "analysis": {
                "enabled_checks": ["git", "security", "complexity", "ml_prediction", "dependencies"],
                "max_file_size_mb": 5,
                "ignore_patterns": [".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"]
            },
            "git": {
                "churn_threshold": 20,
                "bus_factor_threshold": 1,
                "months_to_analyze": 12,
                "min_commits_for_analysis": 5
            },
            "security": {
                "detect_hardcoded_secrets": True,
            },
            "complexity": {
                "cyclomatic_threshold": 10,
                "lines_of_code_threshold": 200
            },
            "output": {
                "formats": ["json", "html"],
                "output_dir": "./reports",
            }
        }
