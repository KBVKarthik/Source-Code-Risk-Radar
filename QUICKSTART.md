# Quick Start Guide

## 30-Second Setup

```bash
# 1. Navigate to project
cd Source-Code-Risk-Radar

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run analysis with dummy data (no git required)
python main.py --use-dummy-data --output-format html

# 4. View results
# Open reports/risk_dashboard_*.html in your browser
```

## Analyze Your Own Code

```bash
# Analyze current directory
python main.py

# Analyze specific repository
python main.py --repo-path C:\path\to\your\repo --output-format html
```

## What You Get

✅ **Interactive HTML Dashboard** with:

- Overall risk score and metrics
- Critical modules highlighting
- High-risk modules table
- Security vulnerabilities list
- Failure predictions
- Dependency risks

✅ **Console Report** with:

- Summary statistics
- Critical issues
- High-risk modules
- Security warnings
- Failure points
- Dependency risks

✅ **JSON/CSV Exports** for:

- Integration with other tools
- Data analysis
- CI/CD pipelines
- Reporting systems

## Key Features

### 🔍 Code Analysis

- **Complexity Metrics**: Cyclomatic complexity, LOC, cognitive complexity
- **Code Churn**: Change frequency and stability metrics
- **Bus Factor**: Knowledge concentration analysis
- **Code Age**: File creation and modification history

### 🔐 Security Scanning

- Hardcoded secrets (API keys, passwords, tokens)
- Unsafe functions (eval, exec, pickle, os.system)
- SQL injection patterns
- Debug mode detection
- Sensitive data in logs

### 🤖 ML-Based Prediction

- Failure probability prediction
- Risk factor identification
- Next 3-month failure forecast
- Automated recommendations

### 📦 Dependency Analysis

- Outdated packages detection
- Known vulnerabilities
- Breaking change risk assessment
- Upgrade risk scoring

## Understanding Risk Levels

| Level       | Score  | Action               |
| ----------- | ------ | -------------------- |
| 🔴 CRITICAL | 80-100 | Fix immediately      |
| 🟠 HIGH     | 60-79  | Schedule refactoring |
| 🟡 MEDIUM   | 40-59  | Plan improvements    |
| 🟢 LOW      | 0-39   | Monitor standards    |

## Output Files

Reports are saved to `./reports/`:

- `risk_dashboard_TIMESTAMP.html` - Interactive dashboard
- `risk_report_TIMESTAMP.json` - Detailed JSON data
- `risk_report_TIMESTAMP.csv` - Spreadsheet export

## Common Commands

```bash
# Help
python main.py --help

# Console output
python main.py

# HTML dashboard
python main.py --output-format html

# JSON export
python main.py --output-format json

# CSV export
python main.py --output-format csv

# Analyze specific repo
python main.py --repo-path C:\my\repo

# Use dummy data (testing)
python main.py --use-dummy-data

# Custom config
python main.py --config custom_config.json

# Verbose output
python main.py --verbose
```

## Example Workflow

1. **Run initial analysis**

   ```bash
   python main.py --output-format html
   ```

2. **Review dashboard**

   - Open the HTML report in browser
   - Identify critical issues
   - Note high-risk modules

3. **Fix critical issues**

   - Address security vulnerabilities
   - Fix single points of failure
   - Refactor complex code

4. **Monitor progress**

   ```bash
   python main.py --output-format json > report.json
   # Track improvement over time
   ```

5. **Integrate with CI/CD**
   - Add to GitHub Actions / GitLab CI
   - Generate reports on each commit
   - Track metrics over time

## System Requirements

- **Python**: 3.9 or higher
- **OS**: Windows, macOS, or Linux
- **Disk**: ~100MB for dependencies
- **RAM**: 512MB minimum, 2GB recommended

## Troubleshooting

### "Git not found"

- Analysis uses dummy data automatically
- Or install Git: https://git-scm.com/download

### "Module not found"

- Run `pip install -r requirements.txt`
- Ensure Python 3.9+ is used

### Slow analysis

- Check repo size
- Configure ignore_patterns in config.json
- Analyze subdirectories separately

### Missing files in report

- Verify file extensions are supported
- Check ignore_patterns configuration
- Review analysis logs with --verbose

## Next Steps

- 📖 Read [USAGE.md](USAGE.md) for detailed guide
- 💡 Check [EXAMPLES.md](EXAMPLES.md) for sample outputs
- 🤝 See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- 📚 Review [README.md](README.md) for full documentation

## Features Overview

```
SOURCE CODE RISK RADAR
│
├─ Git Analysis
│  ├─ Code Churn
│  ├─ Bus Factor (Knowledge Concentration)
│  ├─ Author Distribution
│  └─ Modification Frequency
│
├─ Security Analysis
│  ├─ Hardcoded Secrets
│  ├─ Unsafe Functions
│  ├─ SQL Injection Patterns
│  └─ Debug Mode Detection
│
├─ Complexity Analysis
│  ├─ Cyclomatic Complexity
│  ├─ Cognitive Complexity
│  ├─ Lines of Code
│  └─ Maintainability Index
│
├─ ML-Based Prediction
│  ├─ Failure Point Prediction
│  ├─ Risk Factor Identification
│  └─ Automated Recommendations
│
├─ Dependency Analysis
│  ├─ Outdated Packages
│  ├─ Known Vulnerabilities
│  ├─ Breaking Changes Risk
│  └─ Upgrade Risk Score
│
└─ Reporting
   ├─ Interactive HTML Dashboard
   ├─ JSON Data Export
   ├─ CSV Spreadsheet Export
   └─ Console Summary
```

## Support

- 🐛 Report issues: GitHub Issues
- 💬 Ask questions: GitHub Discussions
- 📧 Email: Check repository for contact info

---

**Happy analyzing! 🎯**

Let me know if you have any questions or need help getting started!
