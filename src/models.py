"""Data models for Risk Radar analysis results"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class RiskLevel(Enum):
    """Risk classification levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class SecurityIssue:
    """Security vulnerability or pattern found"""
    file_path: str
    line_number: int
    issue_type: str  # hardcoded_secret, unsafe_function, sql_injection, etc.
    severity: RiskLevel
    description: str
    snippet: str
    recommendation: str


@dataclass
class ComplexityMetrics:
    """Code complexity measurements"""
    file_path: str
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    maintainability_index: float
    risk_level: RiskLevel


@dataclass
class GitMetrics:
    """Git-based metrics for a file"""
    file_path: str
    total_commits: int
    unique_authors: int
    bus_factor: int  # Number of people who know this code
    churn_score: float  # 0-1, higher = more changes
    last_modified_days_ago: int
    creation_date: datetime
    modification_frequency: float  # commits per month


@dataclass
class DependencyRisk:
    """Dependency upgrade and security information"""
    package_name: str
    current_version: str
    latest_version: Optional[str]
    is_outdated: bool
    known_vulnerabilities: int
    upgrade_risk_score: float  # 0-100
    breaking_changes_risk: float  # 0-1


@dataclass
class ModuleRisk:
    """Overall risk assessment for a module/file"""
    file_path: str
    complexity_risk: float  # 0-100
    security_risk: float  # 0-100
    churn_risk: float  # 0-100
    bus_factor_risk: float  # 0-1
    failure_probability: float  # 0-1 (ML prediction)
    dependency_risk: float  # 0-100
    overall_risk_score: float  # 0-100 (weighted average)
    risk_level: RiskLevel
    primary_owners: List[str]
    critical_issues: List[str]
    recommendations: List[str]


@dataclass
class AnalysisMetadata:
    """Metadata about the analysis run"""
    repository_path: str
    analysis_timestamp: datetime
    total_files_analyzed: int
    total_lines_of_code: int
    analysis_duration_seconds: float
    git_commits_analyzed: int
    python_version: str
    analysis_type: str  # full, security_only, etc.


@dataclass
class RiskReport:
    """Complete risk analysis report"""
    metadata: AnalysisMetadata
    modules: List[ModuleRisk]
    security_issues: List[SecurityIssue] = field(default_factory=list)
    complexity_metrics: List[ComplexityMetrics] = field(default_factory=list)
    git_metrics: List[GitMetrics] = field(default_factory=list)
    dependency_risks: List[DependencyRisk] = field(default_factory=list)
    high_risk_modules: List[ModuleRisk] = field(default_factory=list)
    critical_modules: List[ModuleRisk] = field(default_factory=list)
    failure_predictions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Value-add fields (populated after core analysis)
    trend_analysis: Optional[Any] = None
    technical_debt: Optional[Any] = None
    test_coverage: Optional[Any] = None
    team_impact: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'metadata': asdict(self.metadata),
            'modules': [asdict(m) for m in self.modules],
            'security_issues': [asdict(s) for s in self.security_issues],
            'complexity_metrics': [asdict(c) for c in self.complexity_metrics],
            'git_metrics': [asdict(g) for g in self.git_metrics],
            'dependency_risks': [asdict(d) for d in self.dependency_risks],
            'high_risk_modules': [asdict(m) for m in self.high_risk_modules],
            'critical_modules': [asdict(m) for m in self.critical_modules],
            'failure_predictions': self.failure_predictions
        }

    @property
    def overall_risk_score(self) -> float:
        """Calculate repository-wide risk score"""
        if not self.modules:
            return 0.0
        return sum(m.overall_risk_score for m in self.modules) / len(self.modules)

    @property
    def overall_risk_level(self) -> RiskLevel:
        """Determine overall risk level"""
        score = self.overall_risk_score
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

