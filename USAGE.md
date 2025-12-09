# Usage Guide - Source Code Risk Radar

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd Source-Code-Risk-Radar

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Analysis

Analyze your current repository:

```bash
python main.py
```

Analyze a specific repository:

```bash
python main.py --repo-path /path/to/your/repo
```

### 3. Output Formats

Generate an interactive HTML dashboard:

```bash
python main.py --repo-path /path/to/repo --output-format html
```

Generate a JSON report:

```bash
python main.py --repo-path /path/to/repo --output-format json
```

Generate a CSV export:

```bash
python main.py --repo-path /path/to/repo --output-format csv
```

## Key Features

### 1. High-Risk Module Detection

The tool identifies modules at risk based on:

- **Cyclomatic Complexity**: Measures code complexity (higher = riskier)
- **Code Churn**: How frequently the file changes (high = instability)
- **Ownership Concentration**: Bus factor analysis (1 owner = critical risk)

**Risk Factors:**

- Complexity Risk: 0-100 (higher = more complex)
- Churn Risk: 0-100 (higher = more unstable)
- Bus Factor: 1-N (1 = single point of failure)

### 2. Security Vulnerability Detection

Detects common security issues:

**Hardcoded Secrets:**

- API keys and tokens
- Database credentials
- AWS keys
- JWT tokens
- Private keys

**Unsafe Function Usage:**

- `eval()`, `exec()` - Code execution
- `pickle.load()` - Unsafe deserialization
- `os.system()` - Shell injection
- `subprocess.call(shell=True)` - Shell injection
- `yaml.load()` - Code execution

**SQL/NoSQL Injection Patterns:**

- Dynamic query construction
- MongoDB injection
- String concatenation in queries

**Other Issues:**

- Debug mode enabled in production
- Sensitive data in logs

### 3. Bus Factor Analysis

Identifies components with a "bus factor" of 1:

- Only one person understands the code
- Knowledge concentrated in one developer
- High risk if that person leaves

**Output:**

```
Bus Factor Risk: 1.0 = CRITICAL (Single person dependency)
Bus Factor Risk: 0.5 = HIGH (2 people required)
Bus Factor Risk: 0.2 = MEDIUM (5+ people aware)
```

### 4. ML-Based Failure Prediction

Predicts which components are likely to fail in the next 3 months based on:

- Historical change patterns
- Code complexity metrics
- Author diversity
- Recent modification frequency
- Bus factor

**Probability ranges:**

- 70%+ : CRITICAL - Immediate action required
- 50-70%: HIGH - Schedule refactoring
- 30-50%: MEDIUM - Plan improvements
- <30%: LOW - Monitor standards

### 5. Dependency Risk Assessment

Analyzes project dependencies for:

- **Outdated Packages**: Current version vs. latest
- **Known Vulnerabilities**: Published CVEs
- **Breaking Changes Risk**: Major version gaps
- **Upgrade Risk Score**: 0-100 combined metric

## Configuration

Edit `config/config.json` to customize analysis:

```json
{
  "analysis": {
    "enabled_checks": [
      "git",
      "security",
      "complexity",
      "ml_prediction",
      "dependencies"
    ],
    "ignore_patterns": [".git", "node_modules", ".venv", "__pycache__"]
  },
  "security": {
    "detect_hardcoded_secrets": true,
    "unsafe_functions": ["eval", "exec", "pickle.loads", "os.system"]
  },
  "complexity": {
    "cyclomatic_threshold": 10,
    "lines_of_code_threshold": 200
  },
  "ml": {
    "prediction_horizon_months": 3
  },
  "output": {
    "formats": ["html", "json", "csv"],
    "output_dir": "./reports"
  }
}
```

## Understanding Risk Scores

### Overall Risk Score (0-100)

Components are scored by combining:

- **Complexity Risk** (25%): Code complexity and maintainability
- **Security Risk** (30%): Detected vulnerabilities and unsafe patterns
- **Churn Risk** (20%): Change frequency and instability
- **Bus Factor Risk** (15%): Knowledge concentration
- **Failure Risk** (10%): ML-predicted failure probability

### Risk Levels

| Score  | Level    | Action                          |
| ------ | -------- | ------------------------------- |
| 80-100 | CRITICAL | Immediate action required       |
| 60-79  | HIGH     | Schedule for review/refactoring |
| 40-59  | MEDIUM   | Plan improvements               |
| 0-39   | LOW      | Monitor and maintain            |

## Report Interpretation

### Example Critical Finding

```
auth_service.py
  Risk Score: 92/100 (CRITICAL)

  Risk Factors:
  ├─ Cyclomatic Complexity: 35 (Critical)
  ├─ Bus Factor: 1 (Single author - alice@company.com)
  ├─ Code Churn: High (15 commits last 3 months)
  ├─ Hardcoded API Key detected (Line 45)
  └─ Failure Probability: 78%

  Recommendations:
  ├─ Refactor to reduce complexity (target < 10)
  ├─ Distribute knowledge - pair programming recommended
  ├─ Remove hardcoded credentials - use environment variables
  └─ Increase test coverage
```

## Advanced Usage

### Using Dummy Data (Testing/Demo)

```bash
python main.py --use-dummy-data --output-format html
```

This generates realistic-looking analysis results for testing without needing a real repository.

### Custom Configuration

```bash
python main.py --repo-path /path/to/repo --config ./custom_config.json
```

### Verbose Output

```bash
python main.py --repo-path /path/to/repo --verbose
```

## Common Issues

### Git Not Available

If git analysis fails (git not installed or repo not initialized):

- Tool automatically falls back to dummy data
- Use `--use-dummy-data` flag to force dummy data
- Install git for full analysis

### Large Repositories

For very large repositories:

- Analysis may take several minutes
- Configure `ignore_patterns` to skip non-essential directories
- Consider analyzing subdirectories separately

### Memory Issues

For memory-constrained environments:

- Analyze subdirectories separately
- Reduce max_file_size_mb in config
- Use `--analysis git` for specific analysis types

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Code Risk Analysis

on: [push, pull_request]

jobs:
  risk-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python main.py --output-format json
      - uses: actions/upload-artifact@v2
        with:
          name: risk-report
          path: reports/
```

### GitLab CI Example

```yaml
risk-analysis:
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - python main.py --output-format html
  artifacts:
    paths:
      - reports/
    expire_in: 30 days
```

## Troubleshooting

### Analysis too slow

1. Add more directories to `ignore_patterns`
2. Analyze smaller subdirectories separately
3. Disable specific checks in configuration

### Inaccurate results

1. Ensure git history is available (clone with full history)
2. Verify configuration matches your project structure
3. Check that all supported file extensions are configured

### Missing dependencies detected

1. Verify dependency files are in the repository
2. Check supported formats: requirements.txt, package.json, Gemfile, poetry.lock
3. For other package managers, add manual analysis

## Performance Metrics

- Small repo (<50 files): ~5-10 seconds
- Medium repo (50-500 files): ~30-60 seconds
- Large repo (500+ files): ~2-5 minutes

## Next Steps

1. Review the HTML dashboard for visual analysis
2. Fix CRITICAL issues immediately
3. Schedule HIGH-risk items for refactoring
4. Document MEDIUM-risk findings
5. Monitor LOW-risk modules

For more information, see the main README.md file.
