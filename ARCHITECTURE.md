# Project Architecture Guide

## System Overview

Source Code Risk Radar is a comprehensive code quality and risk analysis tool that combines multiple analysis techniques to provide actionable insights into code health, security risks, and maintainability.

## Architecture Layers

### 1. Data Layer (models.py)

**Responsibility**: Define all data structures and types

- `RiskLevel`: Enum for risk classification
- `SecurityIssue`: Security vulnerability findings
- `ComplexityMetrics`: Code complexity measurements
- `GitMetrics`: Git-based metrics
- `DependencyRisk`: Package risk assessment
- `ModuleRisk`: Aggregated risk for a file
- `RiskReport`: Complete analysis report
- `AnalysisMetadata`: Analysis session information

### 2. Analyzer Layer

**Responsibility**: Extract and analyze specific code properties

#### Git Analyzer (`analyzers/git_analyzer.py`)

- Analyzes git commit history
- Calculates code churn (change frequency)
- Determines bus factor (knowledge concentration)
- Measures author distribution
- Provides historical trends

```
Input: File path
Process: Parse git log, analyze authors and commits
Output: GitMetrics (commits, authors, churn, bus factor)
```

#### Security Analyzer (`analyzers/security_analyzer.py`)

- Pattern-based vulnerability detection
- Hardcoded secrets detection
- Unsafe function usage identification
- SQL injection pattern matching
- Debug mode and logging issues

```
Input: File content
Process: Regex matching against known patterns
Output: SecurityIssue list (type, severity, location)
```

#### Complexity Analyzer (`analyzers/complexity_analyzer.py`)

- AST (Abstract Syntax Tree) analysis for Python
- Cyclomatic complexity calculation
- Cognitive complexity estimation
- Lines of code (LOC) counting
- Maintainability index calculation

```
Input: Source code
Process: Parse AST, traverse control flow nodes
Output: ComplexityMetrics (complexity scores, LOC, index)
```

#### Dependency Analyzer (`analyzers/dependency_analyzer.py`)

- Parses dependency files (requirements.txt, package.json, etc.)
- Detects outdated packages
- Assesses upgrade risk
- Identifies known vulnerabilities
- Calculates breaking change risk

```
Input: Dependency files (multiple formats)
Process: Parse versions, compare with latest
Output: DependencyRisk list (outdated, vulns, risk score)
```

### 3. ML Model Layer (`ml_models/`)

#### Failure Predictor (`ml_models/failure_predictor.py`)

- Trains on synthetic historical data
- Uses Random Forest classifier
- Features: churn, complexity, age, frequency, authors, bus factor
- Predicts failure probability for next N months
- Provides risk factors and recommendations

```
Features:
├─ churn_rate (0-1)
├─ cyclomatic_complexity (int)
├─ file_age_months (float)
├─ commit_frequency (float)
├─ author_count (int)
├─ bus_factor (int)
├─ recent_changes (int)
└─ test_coverage_proxy (0-1)

Training: Synthetic data with heuristic labels
Prediction: Binary classifier (will_fail: yes/no)
Output: Probability score (0-1)
```

### 4. Orchestration Layer (`risk_radar.py`)

**RiskRadar Class**: Main coordinator

- Initializes all analyzers
- Coordinates analysis pipeline
- Aggregates results
- Computes overall risk scores
- Manages configuration

```
Pipeline:
1. Get files to analyze
2. Run git analysis (parallel)
3. Run security analysis (parallel)
4. Run complexity analysis (parallel)
5. Run dependency analysis
6. Prepare ML features
7. Run failure prediction
8. Aggregate metrics
9. Calculate risk scores
10. Generate report
```

### 5. Output Layer (`report_formatter.py`)

**ReportFormatter Class**: Format and export results

- HTML Dashboard: Interactive visualization
- JSON Export: Structured data
- CSV Export: Spreadsheet format
- Console Output: Terminal summary

### 6. CLI Layer (`main.py`)

**Entry Point**: Command-line interface

- Argument parsing
- Configuration loading
- Analysis execution
- Output formatting
- Error handling

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI (main.py)                            │
│            Parse args, load config, start analysis          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                RiskRadar Orchestrator                       │
│              Coordinate all analyses                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐    │
│  │ Git Analyzer│  │Security      │  │ Complexity     │    │
│  │             │  │ Analyzer     │  │ Analyzer       │    │
│  └─────────────┘  └──────────────┘  └────────────────┘    │
│        ↓                ↓                    ↓               │
│    GitMetrics     SecurityIssue      ComplexityMetrics    │
│                                                             │
│  ┌────────────────┐  ┌──────────────────────────────┐    │
│  │  Dependency    │  │   ML Failure Predictor        │    │
│  │  Analyzer      │  │   (Feature aggregation)       │    │
│  └────────────────┘  └──────────────────────────────┘    │
│        ↓                         ↓                        │
│    DependencyRisk         FailurePredictions              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Results Aggregator                             │
│        Combine metrics into ModuleRisk scores               │
│           Calculate overall metrics                         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  RiskReport                                 │
│         Complete analysis result object                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Report Formatter                               │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐   │
│    │   HTML   │  │   JSON   │  │   CSV    │  │Console │   │
│    │Dashboard │  │  Export  │  │ Export   │  │Report  │   │
│    └──────────┘  └──────────┘  └──────────┘  └────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Risk Score Calculation

### Module-Level Risk Score

```
Overall Risk = (
    Complexity Risk    × 0.25 +
    Security Risk      × 0.30 +
    Churn Risk         × 0.20 +
    Bus Factor Risk    × 0.25 +
    Failure Prob × 100 × 0.25 +
    Dependency Risk    × 0.05
)

Normalized to: 0-100
```

### Risk Level Assignment

```
Score Range    → Level    → Action
[80, 100]      → CRITICAL → Fix immediately
[60, 79]       → HIGH     → Schedule refactoring
[40, 59]       → MEDIUM   → Plan improvements
[0, 39]        → LOW      → Monitor standards
```

## Analyzer Details

### Git Analyzer

**Features Calculated**:

1. **Total Commits**: Absolute count
2. **Unique Authors**: Number of contributors
3. **Bus Factor**: Minimum developers for 70% commits
4. **Churn Score**: Recent commit frequency (0-1)
5. **Modification Frequency**: Commits per month
6. **Last Modified**: Days since last change
7. **Creation Date**: File age

**Fallback**: DummyGitAnalyzer provides consistent test data

### Security Analyzer

**Detection Patterns**:

1. **Hardcoded Secrets**:

   - API keys: `api_key = "..."`
   - AWS keys: `aws_key = "..."`
   - Passwords: `password = "..."`
   - Tokens: `token = "..."`
   - JWT tokens: Base64 JWT pattern
   - Connection strings

2. **Unsafe Functions**:

   - `eval()`, `exec()` - Code execution
   - `pickle.load()` - Deserialization
   - `os.system()`, `os.popen()` - Shell execution
   - `subprocess.call(shell=True)` - Command injection
   - `yaml.load()` - Code execution
   - `__import__()` - Dynamic imports

3. **SQL Injection**:

   - Dynamic query construction
   - String concatenation in queries
   - NoSQL injection patterns

4. **Other Issues**:
   - Debug mode enabled
   - Sensitive data in logs

### Complexity Analyzer

**Cyclomatic Complexity**:

- Counts decision points
- Incremented for: if, for, while, except, with, and, or
- Base complexity: 1

**Cognitive Complexity**:

- Nesting depth factor
- Decision point nesting
- Higher values = harder to understand

**Maintainability Index**:

```
MI = max(0, min(100,
    100 -
    (LOC / 200) * 0.1 -
    (Cyclomatic / 30) * 2 -
    (Cognitive / 15) * 0.5
))
```

### Failure Predictor

**Training Strategy**:

- Synthetic data generation
- Heuristic failure labels
- Random Forest classifier
- Feature standardization

**Prediction Logic**:

1. Extract 8 features from file metrics
2. Standardize features (zero mean, unit variance)
3. Pass through trained classifier
4. Output probability (0-1)
5. Identify contributing risk factors
6. Generate recommendations

**Fallback**: Heuristic calculation when sklearn unavailable

## Extension Points

### Adding New Analyzers

1. Create class inheriting analysis pattern
2. Implement `analyze_file()` and `analyze_directory()`
3. Return typed result objects
4. Add to RiskRadar orchestrator
5. Create dummy version for testing

### Adding New Risk Factors

1. Define metric in data model
2. Implement calculation in analyzer
3. Update risk score formula
4. Add visualization in report formatter
5. Document in configuration

### Adding New Output Formats

1. Implement in ReportFormatter
2. Add format option to CLI
3. Test with sample reports
4. Update documentation

## Configuration Management

The system uses hierarchical configuration:

1. **Default Config**: Hard-coded in `RiskRadar._default_config()`
2. **File Config**: Loaded from `config/config.json`
3. **CLI Arguments**: Override file config
4. **Environment Variables**: Final overrides

## Performance Considerations

- **File Analysis**: Parallel-ready (implement in future)
- **Git Operations**: Cached per session
- **AST Parsing**: Only for Python files
- **ML Prediction**: Single prediction per file
- **Memory**: Stores results in memory (suitable for <1000 files)

## Testing Strategy

- **Unit Tests**: Individual analyzer logic
- **Integration Tests**: Full pipeline
- **Dummy Analyzers**: Realistic test data without dependencies

See `tests/` directory for test implementation.

## Future Enhancements

1. **Parallel Analysis**: Process files concurrently
2. **More Analyzers**: Test coverage, documentation, design patterns
3. **Trend Analysis**: Track metrics over time
4. **Baseline Comparison**: Compare against projects
5. **IDE Integration**: VS Code / IDE plugins
6. **Web Dashboard**: Real-time server with REST API
7. **ML Improvements**: Use real historical data
8. **Performance**: Stream processing for large codebases
