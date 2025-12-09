"""Output formatting and reporting"""

import json
import os
from typing import Dict, List
from datetime import datetime
from pathlib import Path

from src.models import RiskReport, RiskLevel


class ReportFormatter:
    """Formats risk analysis reports in various formats"""

    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_json_report(self, report: RiskReport, filename: str = None) -> str:
        """Generate JSON report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"risk_report_{timestamp}.json"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w') as f:
            # Custom serialization for dataclasses and datetime
            data = self._prepare_report_data(report)
            json.dump(data, f, indent=2, default=str)

        return filepath

    def generate_csv_report(self, report: RiskReport, filename: str = None) -> str:
        """Generate CSV report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"risk_report_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        try:
            import csv
        except ImportError:
            print("CSV export requires csv module")
            return None

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            headers = [
                'File Path', 'Risk Score', 'Risk Level', 'Complexity Risk', 'Security Risk',
                'Churn Risk', 'Bus Factor Risk', 'Failure Probability', 'Critical Issues', 'Recommendations'
            ]
            writer.writerow(headers)

            # Data rows
            for module in report.modules:
                row = [
                    module.file_path,
                    f"{module.overall_risk_score:.1f}",
                    module.risk_level.value,
                    f"{module.complexity_risk:.1f}",
                    f"{module.security_risk:.1f}",
                    f"{module.churn_risk:.1f}",
                    f"{module.bus_factor_risk:.2f}",
                    f"{module.failure_probability:.2f}",
                    '; '.join(module.critical_issues),
                    '; '.join(module.recommendations)
                ]
                writer.writerow(row)

        return filepath

    def generate_html_dashboard(self, report: RiskReport, filename: str = None) -> str:
        """Generate interactive HTML dashboard"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"risk_dashboard_{timestamp}.html"

        filepath = os.path.join(self.output_dir, filename)

        html_content = self._build_html_dashboard(report)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filepath

    def print_console_report(self, report: RiskReport):
        """Print formatted report to console"""
        print("\n" + "=" * 70)
        print("SOURCE CODE RISK RADAR - ANALYSIS REPORT".center(70))
        print("=" * 70 + "\n")

        # Metadata
        print(f"Repository: {report.metadata.repository_path}")
        print(f"Analysis Time: {report.metadata.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {report.metadata.analysis_duration_seconds:.2f}s")
        print(f"Files Analyzed: {report.metadata.total_files_analyzed}")
        print(f"Total LOC: {report.metadata.total_lines_of_code:,}")
        print(f"Overall Risk Score: {report.overall_risk_score:.1f}/100")
        print(f"Overall Risk Level: {report.overall_risk_level.value}")
        print()

        # Critical modules
        critical = [m for m in report.modules if m.risk_level == RiskLevel.CRITICAL]
        if critical:
            print("🔴 CRITICAL ISSUES - IMMEDIATE ACTION REQUIRED:")
            print("-" * 70)
            for module in critical[:10]:
                print(f"\n  {module.file_path}")
                print(f"    Risk Score: {module.overall_risk_score:.1f}/100")
                print(f"    Issues: {', '.join(module.critical_issues) if module.critical_issues else 'None'}")
                for rec in module.recommendations[:2]:
                    print(f"    → {rec}")
            print()

        # High risk modules
        high = [m for m in report.modules if m.risk_level == RiskLevel.HIGH]
        if high:
            print("🟠 HIGH RISK MODULES:")
            print("-" * 70)
            for module in high[:10]:
                print(f"  {module.file_path} - Risk: {module.overall_risk_score:.1f}/100")
            print()

        # Failure predictions
        if report.failure_predictions:
            print("⚠️  LIKELY FAILURE POINTS (Next 3 months):")
            print("-" * 70)
            for pred in report.failure_predictions[:5]:
                prob = pred.get('failure_probability', 0) * 100
                print(f"  {pred.get('file_path')} - {prob:.0f}% probability")
                if pred.get('risk_factors'):
                    print(f"    Factors: {', '.join(pred['risk_factors'][:2])}")
            print()

        # Security issues
        if report.security_issues:
            critical_sec = [i for i in report.security_issues if i.severity == RiskLevel.CRITICAL]
            if critical_sec:
                print("🔐 CRITICAL SECURITY ISSUES:")
                print("-" * 70)
                for issue in critical_sec[:5]:
                    print(f"  {issue.file_path}:{issue.line_number} - {issue.issue_type}")
                    print(f"    {issue.description}")
                print()

        # Dependency risks
        if report.dependency_risks:
            high_risk_deps = [d for d in report.dependency_risks if d.upgrade_risk_score >= 60]
            if high_risk_deps:
                print("📦 HIGH-RISK DEPENDENCIES:")
                print("-" * 70)
                for dep in high_risk_deps[:10]:
                    print(f"  {dep.package_name}: {dep.current_version} → {dep.latest_version or 'unknown'}")
                    print(f"    Risk Score: {dep.upgrade_risk_score:.1f}/100")
                    if dep.known_vulnerabilities > 0:
                        print(f"    Known Vulnerabilities: {dep.known_vulnerabilities}")
                print()

        print("=" * 70)
        print(f"Report generated at: {report.metadata.analysis_timestamp}")
        print("=" * 70 + "\n")

    def _prepare_report_data(self, report: RiskReport) -> Dict:
        """Prepare report data for JSON serialization"""
        return {
            'metadata': {
                'repository_path': report.metadata.repository_path,
                'analysis_timestamp': report.metadata.analysis_timestamp.isoformat(),
                'analysis_duration_seconds': report.metadata.analysis_duration_seconds,
                'total_files_analyzed': report.metadata.total_files_analyzed,
                'total_lines_of_code': report.metadata.total_lines_of_code,
            },
            'summary': {
                'overall_risk_score': report.overall_risk_score,
                'overall_risk_level': report.overall_risk_level.value,
                'critical_modules_count': len([m for m in report.modules if m.risk_level == RiskLevel.CRITICAL]),
                'high_risk_modules_count': len([m for m in report.modules if m.risk_level == RiskLevel.HIGH]),
                'security_issues_count': len(report.security_issues),
                'dependency_risks_count': len(report.dependency_risks),
            },
            'modules': [
                {
                    'file_path': m.file_path,
                    'overall_risk_score': m.overall_risk_score,
                    'risk_level': m.risk_level.value,
                    'complexity_risk': m.complexity_risk,
                    'security_risk': m.security_risk,
                    'churn_risk': m.churn_risk,
                    'bus_factor_risk': m.bus_factor_risk,
                    'failure_probability': m.failure_probability,
                    'critical_issues': m.critical_issues,
                    'recommendations': m.recommendations,
                }
                for m in report.modules[:100]  # Limit to top 100
            ],
            'security_issues': [
                {
                    'file_path': i.file_path,
                    'line_number': i.line_number,
                    'issue_type': i.issue_type,
                    'severity': i.severity.value,
                    'description': i.description,
                    'recommendation': i.recommendation,
                }
                for i in report.security_issues[:50]  # Limit to top 50
            ],
            'dependency_risks': [
                {
                    'package_name': d.package_name,
                    'current_version': d.current_version,
                    'latest_version': d.latest_version,
                    'upgrade_risk_score': d.upgrade_risk_score,
                    'known_vulnerabilities': d.known_vulnerabilities,
                }
                for d in sorted(report.dependency_risks, key=lambda x: x.upgrade_risk_score, reverse=True)[:20]
            ],
            'failure_predictions': report.failure_predictions[:20],
        }

    def _build_html_dashboard(self, report: RiskReport) -> str:
        """Build interactive HTML dashboard"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        overall_risk_color = self._get_risk_color(report.overall_risk_level)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Risk Radar Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; padding: 30px; }}
        .summary-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .summary-card h3 {{ color: #333; margin-bottom: 10px; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .summary-card .label {{ color: #666; font-size: 0.9em; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .risk-score {{ font-size: 3em; font-weight: bold; margin-bottom: 10px; }}
        .risk-critical {{ color: #d32f2f; }}
        .risk-high {{ color: #f57c00; }}
        .risk-medium {{ color: #fbc02d; }}
        .risk-low {{ color: #388e3c; }}
        .section {{ background: white; padding: 30px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #333; margin-bottom: 20px; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f5f5f5; font-weight: bold; color: #333; }}
        tr:hover {{ background: #f9f9f9; }}
        .module-item {{ padding: 15px; margin: 10px 0; background: #f9f9f9; border-left: 4px solid #667eea; border-radius: 4px; }}
        .module-item.critical {{ border-left-color: #d32f2f; }}
        .module-item.high {{ border-left-color: #f57c00; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
        .chart-container {{ height: 400px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-label {{ color: #666; font-size: 0.9em; }}
        .metric-value {{ font-size: 1.8em; font-weight: bold; color: #667eea; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Source Code Risk Radar</h1>
        <p>Comprehensive Code Analysis Dashboard</p>
    </div>

    <div class="container">
        <!-- Summary Section -->
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Overall Risk Score</h3>
                <div class="risk-score {overall_risk_color}">{report.overall_risk_score:.1f}</div>
                <div class="label">Risk Level: {report.overall_risk_level.value}</div>
            </div>
            <div class="summary-card">
                <h3>Files Analyzed</h3>
                <div class="value">{report.metadata.total_files_analyzed}</div>
                <div class="label">Total Lines of Code: {report.metadata.total_lines_of_code:,}</div>
            </div>
            <div class="summary-card">
                <h3>Critical Issues</h3>
                <div class="value risk-critical">{len([m for m in report.modules if m.risk_level == RiskLevel.CRITICAL])}</div>
                <div class="label">Require Immediate Action</div>
            </div>
            <div class="summary-card">
                <h3>High Risk Modules</h3>
                <div class="value risk-high">{len([m for m in report.modules if m.risk_level == RiskLevel.HIGH])}</div>
                <div class="label">Schedule for Review</div>
            </div>
        </div>

        <!-- Critical Modules Section -->
        {self._build_critical_modules_html(report)}

        <!-- High Risk Modules Section -->
        {self._build_high_risk_modules_html(report)}

        <!-- Failure Predictions Section -->
        {self._build_failure_predictions_html(report)}

        <!-- Security Issues Section -->
        {self._build_security_issues_html(report)}

        <!-- Dependency Risks Section -->
        {self._build_dependency_risks_html(report)}
    </div>

    <div class="footer">
        <p>Risk Radar Analysis Report • Generated on {timestamp}</p>
        <p>Repository: {report.metadata.repository_path}</p>
    </div>
</body>
</html>"""
        return html

    def _build_critical_modules_html(self, report: RiskReport) -> str:
        """Build HTML for critical modules"""
        critical = [m for m in report.modules if m.risk_level == RiskLevel.CRITICAL]
        
        if not critical:
            return ""

        html = '<div class="section"><h2>🔴 Critical Modules - Immediate Action Required</h2><div>'
        
        for module in critical[:10]:
            rec_text = "<br>".join([f"• {r}" for r in module.recommendations[:2]])
            html += f"""
            <div class="module-item critical">
                <strong>{module.file_path}</strong><br>
                <div class="metric">
                    <div class="metric-label">Risk Score</div>
                    <div class="metric-value risk-critical">{module.overall_risk_score:.1f}</div>
                </div>
                <div style="margin-top: 10px; font-size: 0.9em;">{rec_text}</div>
            </div>"""
        
        html += '</div></div>'
        return html

    def _build_high_risk_modules_html(self, report: RiskReport) -> str:
        """Build HTML for high risk modules"""
        high = [m for m in report.modules if m.risk_level == RiskLevel.HIGH]
        
        if not high:
            return ""

        html = '<div class="section"><h2>🟠 High Risk Modules</h2><table>'
        html += '<tr><th>File</th><th>Risk Score</th><th>Complexity</th><th>Security</th><th>Churn</th></tr>'
        
        for module in high[:20]:
            html += f"""
            <tr>
                <td>{module.file_path}</td>
                <td><strong>{module.overall_risk_score:.1f}/100</strong></td>
                <td>{module.complexity_risk:.1f}</td>
                <td>{module.security_risk:.1f}</td>
                <td>{module.churn_risk:.1f}</td>
            </tr>"""
        
        html += '</table></div>'
        return html

    def _build_failure_predictions_html(self, report: RiskReport) -> str:
        """Build HTML for failure predictions"""
        if not report.failure_predictions:
            return ""

        html = '<div class="section"><h2>⚠️ Likely Failure Points (Next 3 Months)</h2><div>'
        
        for pred in report.failure_predictions[:10]:
            prob = pred.get('failure_probability', 0) * 100
            factors = "<br>".join([f"• {f}" for f in pred.get('risk_factors', [])[:3]])
            html += f"""
            <div class="module-item high">
                <strong>{pred.get('file_path')}</strong><br>
                <div class="metric">
                    <div class="metric-label">Failure Probability</div>
                    <div class="metric-value">{prob:.0f}%</div>
                </div>
                <div style="margin-top: 10px; font-size: 0.9em;">{factors}</div>
            </div>"""
        
        html += '</div></div>'
        return html

    def _build_security_issues_html(self, report: RiskReport) -> str:
        """Build HTML for security issues"""
        critical_sec = [i for i in report.security_issues if i.severity == RiskLevel.CRITICAL]
        
        if not critical_sec:
            return ""

        html = '<div class="section"><h2>🔐 Critical Security Issues</h2><table>'
        html += '<tr><th>File</th><th>Line</th><th>Issue Type</th><th>Recommendation</th></tr>'
        
        for issue in critical_sec[:15]:
            html += f"""
            <tr>
                <td>{issue.file_path}</td>
                <td>{issue.line_number}</td>
                <td><strong>{issue.issue_type}</strong></td>
                <td>{issue.recommendation}</td>
            </tr>"""
        
        html += '</table></div>'
        return html

    def _build_dependency_risks_html(self, report: RiskReport) -> str:
        """Build HTML for dependency risks"""
        high_deps = [d for d in report.dependency_risks if d.upgrade_risk_score >= 60]
        
        if not high_deps:
            return ""

        html = '<div class="section"><h2>📦 High-Risk Dependencies</h2><table>'
        html += '<tr><th>Package</th><th>Current</th><th>Latest</th><th>Risk Score</th><th>Vulnerabilities</th></tr>'
        
        for dep in high_deps[:15]:
            html += f"""
            <tr>
                <td><strong>{dep.package_name}</strong></td>
                <td>{dep.current_version}</td>
                <td>{dep.latest_version or 'N/A'}</td>
                <td>{dep.upgrade_risk_score:.1f}/100</td>
                <td>{dep.known_vulnerabilities}</td>
            </tr>"""
        
        html += '</table></div>'
        return html

    @staticmethod
    def _get_risk_color(risk_level: RiskLevel) -> str:
        """Get CSS class for risk color"""
        if risk_level == RiskLevel.CRITICAL:
            return "risk-critical"
        elif risk_level == RiskLevel.HIGH:
            return "risk-high"
        elif risk_level == RiskLevel.MEDIUM:
            return "risk-medium"
        else:
            return "risk-low"
