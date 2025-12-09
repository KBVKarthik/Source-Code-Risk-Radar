# Sample Analysis Output

This document shows example output from the Risk Radar analysis tool.

## Console Output

```
======================================================================
SOURCE CODE RISK RADAR - ANALYSIS REPORT
======================================================================

Repository: /path/to/repository
Analysis Time: 2024-01-15 14:32:45
Duration: 45.23s
Files Analyzed: 245
Total LOC: 45,230
Overall Risk Score: 62.5/100
Overall Risk Level: HIGH

🔴 CRITICAL ISSUES - IMMEDIATE ACTION REQUIRED:
----------------------------------------------------------------------

  src/payment/processor.py
    Risk Score: 92.3/100
    Issues: hardcoded_secret_api_key, unsafe_function_eval
    → Address security vulnerabilities immediately
    → Refactor to reduce cyclomatic complexity

  src/auth/service.py
    Risk Score: 89.1/100
    Issues: sql_injection, logging_sensitive_data
    → Address security vulnerabilities immediately
    → Mitigate bus factor - documentation and pair programming needed

  src/utils/legacy.py
    Risk Score: 87.5/100
    Issues: unsafe_function_pickle, debug_mode_enabled
    → Address security vulnerabilities immediately
    → Stabilize code - high change frequency indicates instability

🟠 HIGH RISK MODULES:
----------------------------------------------------------------------
  src/models/database.py - Risk: 76.4/100
  src/api/endpoints.py - Risk: 74.2/100
  src/tasks/celery_tasks.py - Risk: 72.8/100
  src/utils/helpers.py - Risk: 71.5/100
  src/cache/redis_client.py - Risk: 70.3/100

⚠️  LIKELY FAILURE POINTS (Next 3 months):
----------------------------------------------------------------------
  src/email/sender.py - 78% probability
    Factors: High code churn, High cyclomatic complexity
  src/reports/generator.py - 65% probability
    Factors: Single point of failure, Unstable (frequent commits)
  src/queue/workers.py - 61% probability
    Factors: High cyclomatic complexity, Limited team knowledge

🔐 CRITICAL SECURITY ISSUES:
----------------------------------------------------------------------
  src/payment/processor.py:142 - hardcoded_secret_api_key
    Hardcoded API key detected
  src/config/settings.py:87 - hardcoded_secret_password
    Hardcoded password detected
  src/auth/oauth.py:156 - unsafe_function_eval
    eval() can execute arbitrary code

📦 HIGH-RISK DEPENDENCIES:
----------------------------------------------------------------------
  django: 2.2.8 → 4.2.7
    Risk Score: 85.0/100
    Known Vulnerabilities: 12
  requests: 2.25.1 → 2.31.0
    Risk Score: 65.0/100
    Known Vulnerabilities: 3
  sqlalchemy: 1.3.20 → 2.0.23
    Risk Score: 72.0/100
    Known Vulnerabilities: 5

======================================================================
Report generated at: 2024-01-15 14:32:45
======================================================================
```

## JSON Report Sample

```json
{
  "metadata": {
    "repository_path": "/path/to/repository",
    "analysis_timestamp": "2024-01-15T14:32:45.123456",
    "analysis_duration_seconds": 45.23,
    "total_files_analyzed": 245,
    "total_lines_of_code": 45230
  },
  "summary": {
    "overall_risk_score": 62.5,
    "overall_risk_level": "HIGH",
    "critical_modules_count": 3,
    "high_risk_modules_count": 12,
    "security_issues_count": 15,
    "dependency_risks_count": 8
  },
  "modules": [
    {
      "file_path": "src/payment/processor.py",
      "overall_risk_score": 92.3,
      "risk_level": "CRITICAL",
      "complexity_risk": 85.0,
      "security_risk": 95.0,
      "churn_risk": 75.0,
      "bus_factor_risk": 0.8,
      "failure_probability": 0.78,
      "critical_issues": ["hardcoded_secret_api_key", "unsafe_function_eval"],
      "recommendations": [
        "Address security vulnerabilities immediately",
        "Refactor to reduce cyclomatic complexity"
      ]
    }
  ],
  "security_issues": [
    {
      "file_path": "src/payment/processor.py",
      "line_number": 142,
      "issue_type": "hardcoded_secret_api_key",
      "severity": "CRITICAL",
      "description": "Hardcoded API key detected",
      "recommendation": "Remove hardcoded API key and use environment variables or secrets management"
    }
  ],
  "dependency_risks": [
    {
      "package_name": "django",
      "current_version": "2.2.8",
      "latest_version": "4.2.7",
      "upgrade_risk_score": 85.0,
      "known_vulnerabilities": 12
    }
  ],
  "failure_predictions": [
    {
      "file_path": "src/email/sender.py",
      "failure_probability": 0.78,
      "risk_factors": ["High code churn", "High cyclomatic complexity"],
      "recommendation": "CRITICAL: Prioritize refactoring and testing immediately"
    }
  ]
}
```

## HTML Dashboard Features

The HTML dashboard includes:

### 1. Summary Cards

- Overall Risk Score
- Files Analyzed
- Critical Issues Count
- High Risk Modules Count

### 2. Critical Modules Section

- List of all CRITICAL-rated modules
- Risk scores and issues
- Key recommendations

### 3. High Risk Modules Table

- All HIGH-rated modules
- Individual component risk breakdown
- Quick risk assessment

### 4. Failure Predictions

- ML-predicted failure points
- Failure probabilities
- Contributing risk factors

### 5. Security Issues Table

- All critical security findings
- File paths and line numbers
- Issue descriptions and fixes

### 6. Dependency Risks

- Outdated and vulnerable packages
- Version gaps and CVE counts
- Upgrade risk scores

## CSV Report Sample

```csv
File Path,Risk Score,Risk Level,Complexity Risk,Security Risk,Churn Risk,Bus Factor Risk,Failure Probability,Critical Issues,Recommendations
src/payment/processor.py,92.3,CRITICAL,85.0,95.0,75.0,0.8,0.78,"hardcoded_secret_api_key; unsafe_function_eval","Address security vulnerabilities immediately; Refactor to reduce cyclomatic complexity"
src/auth/service.py,89.1,CRITICAL,78.0,88.0,82.0,0.9,0.75,"sql_injection; logging_sensitive_data","Address security vulnerabilities immediately; Mitigate bus factor - documentation and pair programming needed"
src/utils/legacy.py,87.5,CRITICAL,92.0,65.0,88.0,0.7,0.72,"unsafe_function_pickle; debug_mode_enabled","Address security vulnerabilities immediately; Stabilize code - high change frequency indicates instability"
```

## Interpreting Results

### Risk Score Components

Each module receives individual scores:

- **Complexity Risk (0-100)**: Cyclomatic complexity and LOC
- **Security Risk (0-100)**: Detected vulnerabilities
- **Churn Risk (0-100)**: Code change frequency
- **Bus Factor Risk (0-1)**: Knowledge concentration
- **Failure Probability (0-1)**: ML-predicted likelihood

### Action Priority

1. **CRITICAL (80-100)**: Fix immediately

   - Security vulnerabilities
   - Single points of failure
   - High failure probability

2. **HIGH (60-79)**: Schedule refactoring

   - Reduce complexity
   - Improve test coverage
   - Distribute knowledge

3. **MEDIUM (40-59)**: Plan improvements

   - Document edge cases
   - Refactor non-urgent items
   - Improve code quality

4. **LOW (0-39)**: Maintain standards
   - Monitor for changes
   - Continue best practices
   - Regular reviews

## Using These Outputs

### For Management

- Review overall risk score
- Focus on critical count
- Review failure predictions
- Plan resource allocation

### For Developers

- Review specific file issues
- Focus on security findings
- Check complexity recommendations
- Plan refactoring sprints

### For Security Team

- Review security issues
- Check hardcoded secrets
- Validate unsafe functions
- Plan remediation

### For DevOps/CI

- Integrate with pipelines
- Monitor risk trends
- Alert on critical issues
- Track improvements over time
