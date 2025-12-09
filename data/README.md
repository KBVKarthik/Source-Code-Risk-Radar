# Sample Analysis Data

This directory contains sample data and expected outputs from Risk Radar analysis.

## Sample Report Structure

The analysis generates reports with the following key metrics:

### Risk Scores

- **Overall Risk Score**: 0-100 (higher = more risk)
- **Complexity Risk**: Based on cyclomatic complexity and LOC
- **Security Risk**: Based on detected vulnerabilities
- **Churn Risk**: Based on code change frequency
- **Bus Factor Risk**: Based on author concentration (0-1)
- **Failure Probability**: ML-predicted likelihood (0-1)

### Risk Levels

- CRITICAL: 80-100 (Red) - Immediate action required
- HIGH: 60-79 (Orange) - Schedule refactoring
- MEDIUM: 40-59 (Yellow) - Plan improvements
- LOW: 0-39 (Green) - Monitor standards

## Expected Output Artifacts

After running analysis, expect:

1. `risk_dashboard_TIMESTAMP.html` - Interactive visualization
2. `risk_report_TIMESTAMP.json` - Detailed data export
3. `risk_report_TIMESTAMP.csv` - Spreadsheet format

## Sample Metrics

### File: `src/auth/service.py`

- Cyclomatic Complexity: 18 (High)
- Lines of Code: 245 (High)
- Cognitive Complexity: 22 (High)
- Maintainability Index: 35 (Low)
- Total Commits: 87
- Unique Authors: 2
- Bus Factor: 2 (Moderate risk)
- Churn Score: 0.65 (High)
- Last Modified: 5 days ago

### Security Issues Found

- Hardcoded API key at line 142
- Unsafe SQL query at line 156
- Debug mode enabled at line 45

### Failure Prediction

- Probability: 76%
- Risk Factors:
  - High code churn
  - High cyclomatic complexity
  - Limited author count

## Dependency Example

### Package: `django`

- Current Version: 2.2.8
- Latest Version: 4.2.7
- Is Outdated: Yes
- Known Vulnerabilities: 12
- Breaking Changes Risk: 0.8 (Major version gap)
- Upgrade Risk Score: 85/100

## Using Sample Data

The tool includes a `--use-dummy-data` flag for testing:

```bash
python main.py --use-dummy-data --output-format html
```

This generates realistic-looking analysis without needing actual code.

## Real Analysis Tips

For accurate analysis:

1. Ensure git history is available (clone with full history)
2. Place all code in supported directories
3. Update `config/config.json` for your project structure
4. Run from repository root for best results

See [EXAMPLES.md](../EXAMPLES.md) for sample outputs.
