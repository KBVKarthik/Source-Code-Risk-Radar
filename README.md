# Source Code Risk Radar

A comprehensive tool that analyzes a company's entire codebase and automatically flags high-risk modules, security weaknesses, bus factor issues, failure-prone components, and dependency upgrade risks.

## Features

- **High-Risk Module Detection**: Identifies modules based on complexity, code churn, and ownership gaps
- **Security Analysis**: Detects hardcoded secrets, unsafe function patterns, and common vulnerabilities
- **Bus Factor Analysis**: Finds components with "bus factor = 1" (single point of failure)
- **Failure Prediction**: Uses ML on git history to identify components likely to fail next
- **Dependency Risk Assessment**: Analyzes dependency upgrade risks and outdated packages
- **Code Complexity Metrics**: Measures cyclomatic complexity, cognitive complexity, and LOC metrics

## Tech Stack

- **Language**: Python 3.9+
- **Git Analysis**: GitPython
- **Static Analysis**: AST analysis, regex patterns
- **ML Libraries**: scikit-learn, NumPy, Pandas
- **Web Dashboard**: Flask + Plotly
- **Security**: semgrep patterns (simulated via regex)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Analysis

```bash
python main.py --repo-path /path/to/repo --output-format html
```

### Specific Analysis Types

```bash
python main.py --repo-path /path/to/repo --analysis security,complexity,churn
```

### Configuration

Edit `config/config.json` to customize analysis parameters.

## Output

Generates:

- Interactive HTML dashboard
- JSON report with detailed metrics
- CSV exports for further analysis
- Console summary with risk scores

## Architecture

```
src/
├── analyzers/           # Core analysis modules
│   ├── git_analyzer.py     # Git history analysis
│   ├── security_analyzer.py # Security pattern detection
│   ├── complexity_analyzer.py # Code metrics
│   └── dependency_analyzer.py # Dependency analysis
├── ml_models/           # Machine learning components
│   └── failure_predictor.py  # Failure point prediction
├── dashboard/           # Web interface
│   ├── app.py
│   └── templates/
├── utils/              # Utility functions
├── models/             # Data models
└── main.py            # Entry point
```

## Risk Scoring

Each component receives:

- **Complexity Risk** (0-100): Based on cyclomatic complexity
- **Churn Risk** (0-100): Based on change frequency
- **Security Risk** (0-100): Based on detected vulnerabilities
- **Bus Factor** (0-1): Concentration of knowledge
- **Failure Probability** (0-1): ML-predicted likelihood
- **Dependency Risk** (0-100): Upgrade and security status

## Example Output

```
╔════════════════════════════════════════════════════════════════╗
║                    RISK RADAR REPORT                           ║
╠════════════════════════════════════════════════════════════════╣
║ Repository: /path/to/repo                                      ║
║ Analyzed Files: 245 | Total LOC: 45,230                       ║
║ Risk Grade: B | Overall Risk: 62/100                          ║
╠════════════════════════════════════════════════════════════════╣
║ CRITICAL ISSUES (3):                                           ║
║  • auth_service.py - Bus Factor: 1 (Owner: alice@company.com) ║
║  • payment.py - Hardcoded API key detected                    ║
║  • utils/legacy.py - Cyclomatic Complexity: 48 (Critical)    ║
╠════════════════════════════════════════════════════════════════╣
║ HIGH RISK MODULES:                                             ║
║  1. payment_processor.py - Risk: 89/100 (High Churn + Owner)  ║
║  2. user_auth.py - Risk: 78/100 (Security Issues)             ║
║  3. data_pipeline.py - Risk: 76/100 (Complex + Unstable)      ║
╠════════════════════════════════════════════════════════════════╣
║ LIKELY FAILURE POINTS (Next 3 months):                        ║
║  • notification_service.py - 78% probability                  ║
║  • cache_manager.py - 65% probability                         ║
║  • email_handler.py - 61% probability                         ║
╚════════════════════════════════════════════════════════════════╝
```

## Docker (Optional)

```bash
docker build -t risk-radar .
docker run -v /path/to/repo:/code risk-radar --repo-path /code
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.
