"""Technical debt quantification and analysis"""

from dataclasses import dataclass
from typing import List, Dict
from src.models import RiskReport, ModuleRisk, RiskLevel


@dataclass
class DebtItem:
    """Single technical debt item"""
    file_path: str
    debt_type: str  # 'complexity', 'security', 'churn', 'bus_factor'
    effort_hours: float
    priority: str  # 'critical', 'high', 'medium'
    description: str
    impact: str


@dataclass
class TechnicalDebtSummary:
    """Technical debt summary"""
    total_debt_hours: float
    critical_debt_hours: float
    high_debt_hours: float
    medium_debt_hours: float
    total_debt_items: int
    estimated_weeks: float
    estimated_cost_usd: float
    debt_by_type: Dict[str, float]
    top_debt_items: List[DebtItem]
    debt_percentage_of_total_time: float
    team_months_to_resolve: float


class TechnicalDebtCalculator:
    """Calculates and quantifies technical debt"""

    # Configuration
    BASE_COMPLEXITY_COST = 2.0  # hours per cyclomatic complexity point
    SECURITY_ISSUE_COST = 4.0  # hours per security issue
    HIGH_CHURN_COST = 8.0  # hours for high-churn modules
    BUS_FACTOR_COST = 12.0  # hours for single-owner risk
    HOURLY_RATE = 150  # USD per developer hour

    def calculate_debt(self, report: RiskReport) -> TechnicalDebtSummary:
        """Calculate technical debt across codebase"""
        debt_items = []
        debt_by_type = {
            'complexity': 0.0,
            'security': 0.0,
            'churn': 0.0,
            'bus_factor': 0.0,
            'dependencies': 0.0
        }

        # Calculate debt for each module
        for module in report.modules:
            if module.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                # Complexity debt
                if module.complexity_risk > 50:
                    effort = (module.complexity_risk / 100) * self.BASE_COMPLEXITY_COST
                    debt_items.append(DebtItem(
                        file_path=module.file_path,
                        debt_type='complexity',
                        effort_hours=effort,
                        priority=self._get_priority(module.risk_level),
                        description=f"High cyclomatic complexity ({module.complexity_risk:.1f}). Refactor into smaller functions.",
                        impact="Reduced maintainability, harder to test, more bugs"
                    ))
                    debt_by_type['complexity'] += effort

                # Security debt
                module_security_issues = len([i for i in report.security_issues if i.file_path == module.file_path])
                if module_security_issues > 0:
                    effort = module_security_issues * self.SECURITY_ISSUE_COST
                    debt_items.append(DebtItem(
                        file_path=module.file_path,
                        debt_type='security',
                        effort_hours=effort,
                        priority=self._get_priority(module.risk_level),
                        description=f"Security vulnerabilities detected ({module_security_issues} issues). Fix immediately.",
                        impact="System vulnerabilities, potential breach, compliance violations"
                    ))
                    debt_by_type['security'] += effort

                # Churn debt
                if module.churn_risk > 60:
                    effort = self.HIGH_CHURN_COST
                    debt_items.append(DebtItem(
                        file_path=module.file_path,
                        debt_type='churn',
                        effort_hours=effort,
                        priority='high',
                        description=f"File changed frequently ({module.churn_risk:.1f} churn). Needs stabilization.",
                        impact="Bug-prone due to constant modifications, test coverage gaps"
                    ))
                    debt_by_type['churn'] += effort

                # Bus factor debt
                if module.bus_factor_risk > 75:
                    effort = self.BUS_FACTOR_COST
                    debt_items.append(DebtItem(
                        file_path=module.file_path,
                        debt_type='bus_factor',
                        effort_hours=effort,
                        priority='critical',
                        description=f"Critical knowledge silo (1-person ownership). Document and distribute knowledge.",
                        impact="Project risk if developer leaves, bottleneck, slow development"
                    ))
                    debt_by_type['bus_factor'] += effort

        # Calculate dependency debt
        for dep in report.dependency_risks:
            if dep.upgrade_risk_score > 70:
                effort = 2.0
                debt_items.append(DebtItem(
                    file_path="dependencies",
                    debt_type='dependencies',
                    effort_hours=effort,
                    priority='high' if dep.known_vulnerabilities > 0 else 'medium',
                    description=f"Dependency {dep.package_name} needs major upgrade ({dep.current_version} -> {dep.latest_version or 'latest'})",
                    impact="Security vulnerabilities, incompatibilities, performance issues"
                ))
                debt_by_type['dependencies'] += effort

        # Sort by effort
        debt_items.sort(key=lambda x: x.effort_hours, reverse=True)

        # Calculate totals
        total_hours = sum(item.effort_hours for item in debt_items)
        critical_hours = sum(item.effort_hours for item in debt_items if item.priority == 'critical')
        high_hours = sum(item.effort_hours for item in debt_items if item.priority == 'high')
        medium_hours = sum(item.effort_hours for item in debt_items if item.priority == 'medium')

        total_loc = report.metadata.total_lines_of_code
        loc_per_hour = total_loc / max(total_hours, 1)
        debt_percentage = (total_hours / max(total_hours + (total_loc / 100), 1)) * 100

        # Team capacity assumptions
        hours_per_week = 40
        weeks_to_resolve = total_hours / hours_per_week
        months_with_2_devs = weeks_to_resolve / 4 / 2

        return TechnicalDebtSummary(
            total_debt_hours=total_hours,
            critical_debt_hours=critical_hours,
            high_debt_hours=high_hours,
            medium_debt_hours=medium_hours,
            total_debt_items=len(debt_items),
            estimated_weeks=weeks_to_resolve,
            estimated_cost_usd=total_hours * self.HOURLY_RATE,
            debt_by_type=debt_by_type,
            top_debt_items=debt_items[:20],
            debt_percentage_of_total_time=debt_percentage,
            team_months_to_resolve=months_with_2_devs
        )

    def _get_priority(self, risk_level: RiskLevel) -> str:
        """Map risk level to priority"""
        if risk_level == RiskLevel.CRITICAL:
            return 'critical'
        elif risk_level == RiskLevel.HIGH:
            return 'high'
        elif risk_level == RiskLevel.MEDIUM:
            return 'medium'
        return 'low'


class DummyTechnicalDebtCalculator:
    """Dummy debt calculator for testing"""

    def calculate_debt(self, report: RiskReport) -> TechnicalDebtSummary:
        """Generate realistic technical debt summary"""
        return TechnicalDebtSummary(
            total_debt_hours=312.5,
            critical_debt_hours=48.0,
            high_debt_hours=124.0,
            medium_debt_hours=140.5,
            total_debt_items=28,
            estimated_weeks=7.8,
            estimated_cost_usd=46875.0,
            debt_by_type={
                'complexity': 68.0,
                'security': 32.0,
                'churn': 64.0,
                'bus_factor': 84.0,
                'dependencies': 64.5
            },
            top_debt_items=[
                DebtItem(
                    file_path="src/core/engine.py",
                    debt_type="bus_factor",
                    effort_hours=12.0,
                    priority="critical",
                    description="Single developer owns critical payment engine. No backup.",
                    impact="Project risk if developer leaves, major bottleneck"
                ),
                DebtItem(
                    file_path="src/api/auth.py",
                    debt_type="security",
                    effort_hours=8.0,
                    priority="critical",
                    description="Multiple security vulnerabilities: hardcoded secrets, weak auth",
                    impact="System can be easily compromised, data breach risk"
                ),
                DebtItem(
                    file_path="src/utils/parser.py",
                    debt_type="complexity",
                    effort_hours=6.0,
                    priority="high",
                    description="Parser has cyclomatic complexity of 68. Needs refactoring.",
                    impact="Hard to understand, test coverage weak, bugs likely"
                ),
            ],
            debt_percentage_of_total_time=28.5,
            team_months_to_resolve=3.9
        )
