"""Integration tests for Risk Radar"""

import pytest
import tempfile
import os
from pathlib import Path

from src.risk_radar import RiskRadar
from src.models import RiskLevel


class TestRiskRadar:
    """Integration tests for the main analyzer"""

    def test_analyze_simple_repository(self, tmp_path):
        """Test analyzing a simple repository"""
        # Create sample files
        py_file = tmp_path / "example.py"
        py_file.write_text('''
def calculate(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        return 0
''')

        # Run analysis with dummy data to avoid git dependency
        radar = RiskRadar(str(tmp_path), use_dummy_data=True)
        report = radar.analyze()

        # Verify report structure
        assert report is not None
        assert report.metadata.total_files_analyzed > 0
        assert len(report.modules) > 0
        assert 0 <= report.overall_risk_score <= 100

    def test_report_contains_all_sections(self, tmp_path):
        """Test that report contains all required sections"""
        py_file = tmp_path / "test.py"
        py_file.write_text('x = 1')

        radar = RiskRadar(str(tmp_path), use_dummy_data=True)
        report = radar.analyze()

        # Check all sections are present
        assert report.metadata is not None
        assert report.modules is not None
        assert report.security_issues is not None
        assert report.dependency_risks is not None
        assert report.failure_predictions is not None

    def test_risk_level_determination(self, tmp_path):
        """Test correct risk level assignment"""
        radar = RiskRadar(str(tmp_path), use_dummy_data=True)
        report = radar.analyze()

        # Verify risk levels are correctly assigned
        for module in report.modules:
            if module.overall_risk_score >= 80:
                assert module.risk_level == RiskLevel.CRITICAL
            elif module.overall_risk_score >= 60:
                assert module.risk_level == RiskLevel.HIGH
            elif module.overall_risk_score >= 40:
                assert module.risk_level == RiskLevel.MEDIUM
            else:
                assert module.risk_level == RiskLevel.LOW


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
