"""Trend analysis and historical risk tracking"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from src.models import RiskReport, RiskLevel


@dataclass
class RiskSnapshot:
    """Historical risk snapshot"""
    timestamp: str
    overall_risk_score: float
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    total_files: int
    avg_complexity: float
    security_issues_count: int
    dependency_risks_count: int


@dataclass
class TrendAnalysis:
    """Trend analysis results"""
    risk_improving: bool
    risk_change_percentage: float
    trend_direction: str  # 'improving', 'degrading', 'stable'
    critical_change: int
    high_change: int
    days_until_critical: Optional[int]
    improvement_rate: float
    recommendations: List[str]


class TrendAnalyzer:
    """Analyzes risk trends over time"""

    def __init__(self, history_dir: str = "./risk_history"):
        self.history_dir = history_dir
        os.makedirs(history_dir, exist_ok=True)
        self.history_file = os.path.join(history_dir, "risk_snapshots.json")

    def save_snapshot(self, report: RiskReport) -> str:
        """Save current risk snapshot to history"""
        snapshot = RiskSnapshot(
            timestamp=datetime.now().isoformat(),
            overall_risk_score=report.overall_risk_score,
            critical_count=len([m for m in report.modules if m.risk_level == RiskLevel.CRITICAL]),
            high_count=len([m for m in report.modules if m.risk_level == RiskLevel.HIGH]),
            medium_count=len([m for m in report.modules if m.risk_level == RiskLevel.MEDIUM]),
            low_count=len([m for m in report.modules if m.risk_level == RiskLevel.LOW]),
            total_files=len(report.modules),
            avg_complexity=sum(m.complexity_risk for m in report.modules) / len(report.modules) if report.modules else 0,
            security_issues_count=len(report.security_issues),
            dependency_risks_count=len(report.dependency_risks)
        )

        # Load existing snapshots
        snapshots = self._load_snapshots()
        snapshots.append(asdict(snapshot))

        # Save back to file
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(snapshots, f, indent=2)

        return f"Snapshot saved: {snapshot.timestamp}"

    def get_trend_analysis(self, report: RiskReport, days_lookback: int = 30) -> TrendAnalysis:
        """Analyze risk trends"""
        snapshots = self._load_snapshots()
        
        if len(snapshots) < 2:
            return TrendAnalysis(
                risk_improving=False,
                risk_change_percentage=0.0,
                trend_direction='stable',
                critical_change=0,
                high_change=0,
                days_until_critical=None,
                improvement_rate=0.0,
                recommendations=["Insufficient historical data. Check again after next analysis run."]
            )

        # Get snapshots from last N days
        cutoff_date = datetime.now() - timedelta(days=days_lookback)
        recent_snapshots = [
            s for s in snapshots
            if datetime.fromisoformat(s['timestamp']) >= cutoff_date
        ]

        if len(recent_snapshots) < 2:
            recent_snapshots = snapshots[-5:] if len(snapshots) >= 5 else snapshots

        first = recent_snapshots[0]
        last = recent_snapshots[-1]

        # Calculate metrics
        risk_change = last['overall_risk_score'] - first['overall_risk_score']
        risk_change_pct = (risk_change / first['overall_risk_score'] * 100) if first['overall_risk_score'] > 0 else 0
        
        critical_change = last['critical_count'] - first['critical_count']
        high_change = last['high_count'] - first['high_count']
        
        improving = risk_change < 0
        
        # Determine trend
        if abs(risk_change_pct) < 5:
            trend = 'stable'
        elif improving:
            trend = 'improving'
        else:
            trend = 'degrading'

        # Calculate days until critical
        days_until_critical = None
        if trend == 'degrading' and last['overall_risk_score'] < 100:
            time_range = (datetime.fromisoformat(last['timestamp']) - 
                         datetime.fromisoformat(first['timestamp'])).days or 1
            daily_change = risk_change / time_range
            if daily_change > 0:
                days_left = (100 - last['overall_risk_score']) / daily_change
                days_until_critical = max(1, int(days_left))

        # Improvement rate
        if improving and len(recent_snapshots) > 2:
            improvements = sum(1 for i in range(1, len(recent_snapshots)) 
                             if recent_snapshots[i]['overall_risk_score'] < recent_snapshots[i-1]['overall_risk_score'])
            improvement_rate = (improvements / (len(recent_snapshots) - 1)) * 100
        else:
            improvement_rate = 0.0

        # Generate recommendations
        recs = []
        if trend == 'degrading':
            recs.append(f"⚠️ Risk score increasing by {abs(risk_change_pct):.1f}%. Urgent action needed!")
        elif trend == 'improving':
            recs.append(f"✓ Risk score improving! Maintaining {improvement_rate:.0f}% improvement rate.")
        else:
            recs.append("Risk score stable. Continue monitoring.")

        if critical_change > 0:
            recs.append(f"Alert: {critical_change} new CRITICAL issues detected!")
        elif critical_change < 0:
            recs.append(f"Great! Fixed {abs(critical_change)} CRITICAL issues.")

        if high_change > 0:
            recs.append(f"Added {high_change} HIGH risk modules. Prioritize refactoring.")

        return TrendAnalysis(
            risk_improving=improving,
            risk_change_percentage=risk_change_pct,
            trend_direction=trend,
            critical_change=critical_change,
            high_change=high_change,
            days_until_critical=days_until_critical,
            improvement_rate=improvement_rate,
            recommendations=recs
        )

    def _load_snapshots(self) -> List[Dict]:
        """Load historical snapshots"""
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []


class DummyTrendAnalyzer:
    """Dummy trend analyzer for testing"""

    def __init__(self, history_dir: str = "./risk_history"):
        self.history_dir = history_dir

    def save_snapshot(self, report: RiskReport) -> str:
        return f"[DEMO] Snapshot saved at {datetime.now().isoformat()}"

    def get_trend_analysis(self, report: RiskReport, days_lookback: int = 30) -> TrendAnalysis:
        """Generate realistic trend analysis"""
        return TrendAnalysis(
            risk_improving=True,
            risk_change_percentage=-8.5,
            trend_direction='improving',
            critical_change=-2,
            high_change=-1,
            days_until_critical=None,
            improvement_rate=67.0,
            recommendations=[
                "✓ Risk score improving! Maintaining 67% improvement rate.",
                "Great! Fixed 2 CRITICAL issues in recent updates.",
                "Keep up the momentum - 8.5% risk reduction this period!"
            ]
        )
