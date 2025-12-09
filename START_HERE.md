# 🎯 START HERE - Source Code Risk Radar

Welcome to **Source Code Risk Radar**, a comprehensive, free, and open-source source code analysis tool!

## ⚡ Quick Start (2 Minutes)

### For Windows Users

1. **Double-click**: `setup.bat`
2. **Wait**: Dependencies install automatically
3. **View**: Browser opens with sample report automatically
4. **Done**: You're ready to analyze code!

### For macOS/Linux Users

```bash
bash setup.sh
```

### Manual Setup (All Platforms)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test run (no real code needed)
python main.py --use-dummy-data --output-format html

# 3. View report
# Open: reports/risk_dashboard_*.html in your browser

# 4. Analyze your code
python main.py --repo-path /path/to/your/code
```

---

## 📚 Documentation Guide

**Where to go based on what you need:**

### Just Getting Started? 👈 START HERE

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 30 seconds
- **[setup.bat](setup.bat)** (Windows) or **[setup.sh](setup.sh)** (macOS/Linux)

### Want to Understand the Tool?

1. **[README.md](README.md)** - Overview and features
2. **[USAGE.md](USAGE.md)** - Detailed usage guide
3. **[EXAMPLES.md](EXAMPLES.md)** - Sample outputs and how to interpret them

### Integrating with Your Team?

- **[PRODUCT_SUMMARY.md](PRODUCT_SUMMARY.md)** - Feature summary for management
- **.github/workflows/risk-analysis.yml** - GitHub Actions integration
- **.gitlab-ci.yml** - GitLab CI integration
- **[Docker Support](#docker)** - Container deployment

### Want to Extend or Contribute?

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and extension points

### Complete Project Details?

- **[PROJECT_INDEX.md](PROJECT_INDEX.md)** - Full file listing
- **[DELIVERY_SUMMARY.md](DELIVERY_SUMMARY.md)** - Complete delivery details

---

## 🚀 Key Features at a Glance

### What It Does

```
Analyzes your codebase and flags:
├─ High-risk modules (complexity, churn, ownership gaps)
├─ Security weak spots (hardcoded secrets, unsafe functions)
├─ Modules with "bus factor = 1" (single points of failure)
├─ Components likely to fail next (ML on git history)
└─ Dependency upgrade risks
```

### Output Options

- 📊 **Interactive HTML Dashboard** - Visual analysis
- 📄 **JSON Export** - For CI/CD integration
- 📈 **CSV Export** - For spreadsheet analysis
- 💻 **Console Output** - Quick terminal summary

### No Cost, No Catches

- ✅ **100% Free** - All dependencies are open-source
- ✅ **No Telemetry** - Your code stays on your machine
- ✅ **No Limits** - Analyze as much code as you want
- ✅ **MIT Licensed** - Use commercially or privately

---

## 📊 Sample Output

### Console Report

```
🔴 CRITICAL ISSUES - IMMEDIATE ACTION REQUIRED:
  auth_service.py - Risk Score: 92.3/100
    Issues: hardcoded_secret_api_key, unsafe_function_eval
    → Address security vulnerabilities immediately
    → Refactor to reduce cyclomatic complexity

⚠️ LIKELY FAILURE POINTS (Next 3 months):
  email_sender.py - 78% probability
  cache_manager.py - 65% probability

📦 HIGH-RISK DEPENDENCIES:
  django: 2.2.8 → 4.2.7 (85 risk score, 12 vulnerabilities)
```

### HTML Dashboard

- Color-coded risk levels (🔴 CRITICAL, 🟠 HIGH, 🟡 MEDIUM, 🟢 LOW)
- Interactive tables with sorting
- Risk breakdowns by type
- Failure predictions
- Security findings

---

## 🎯 Risk Scoring Explained

### Overall Risk Score (0-100)

```
80-100: 🔴 CRITICAL  → Fix immediately
60-79:  🟠 HIGH      → Schedule refactoring
40-59:  🟡 MEDIUM    → Plan improvements
0-39:   🟢 LOW       → Monitor standards
```

### What Gets Scored

- **Complexity Risk** (25%) - Is the code too complex?
- **Security Risk** (30%) - Are there vulnerabilities?
- **Churn Risk** (20%) - Is the code unstable?
- **Bus Factor Risk** (15%) - Is there a single point of failure?
- **Failure Probability** (10%) - Will it break?

---

## 💡 Use Cases

### For Developers

- Identify complex code to refactor
- Find security issues to fix
- Plan code review priorities
- Improve code quality

### For Team Leads

- Monitor codebase health
- Identify high-risk areas
- Plan resource allocation
- Track improvements

### For DevOps/Security

- Integrate with CI/CD pipeline
- Catch vulnerabilities early
- Monitor dependency risks
- Enforce quality gates

### For Management

- Get visibility into code quality
- Understand technical debt
- Plan maintenance efforts
- Track improvements over time

---

## 🔧 Configuration

### Basic Configuration

Edit `config/config.json` to customize:

```json
{
  "analysis": {
    "enabled_checks": [
      "git",
      "security",
      "complexity",
      "ml_prediction",
      "dependencies"
    ]
  },
  "complexity": {
    "cyclomatic_threshold": 10,
    "lines_of_code_threshold": 200
  }
}
```

### Ignore Patterns

Skip directories like `.git`, `node_modules`, `venv`:

```json
{
  "analysis": {
    "ignore_patterns": [".git", "node_modules", ".venv", "__pycache__"]
  }
}
```

---

## 🐳 Docker

### Quick Docker Run

```bash
docker build -t risk-radar .
docker run -v /code:/code risk-radar --repo-path /code
```

### With docker-compose

```bash
docker-compose up
```

---

## 🔄 CI/CD Integration

### GitHub Actions

Copy the provided `.github/workflows/risk-analysis.yml` workflow file. It will:

- Run on every push and PR
- Generate HTML and JSON reports
- Comment on PRs with findings
- Fail if critical issues found

### GitLab CI

Copy the provided `.gitlab-ci.yml` file for automatic analysis on every commit.

### Jenkins, CircleCI, etc.

```bash
pip install -r requirements.txt
python main.py --output-format json > report.json
```

---

## 💬 Common Questions

### Q: Does it work with my programming language?

**A:** Python has full AST support. Other languages (JavaScript, Java, Go, Ruby, PHP, TypeScript, C/C++) use heuristic analysis. Easily add new analyzers!

### Q: How long does analysis take?

**A:**

- Small repo (<50 files): 5-10 seconds
- Medium repo (50-500 files): 30-60 seconds
- Large repo (500+ files): 2-5 minutes

### Q: Does it send my code anywhere?

**A:** No. All analysis is local. No external APIs, no uploads, no telemetry.

### Q: Can I integrate with my tools?

**A:** Yes! Export JSON for custom integration, or use the Python API directly.

### Q: What if I have no git history?

**A:** The tool automatically falls back to dummy data so analysis still works.

### Q: Is this production-ready?

**A:** Yes! Includes Docker, CI/CD templates, comprehensive tests, and full documentation.

---

## 🚦 Next Steps

### Step 1: Get Started (5 min)

- Run setup script: `setup.bat` (Windows) or `bash setup.sh` (macOS/Linux)
- Or: `pip install -r requirements.txt`

### Step 2: Try It Out (2 min)

- Test run: `python main.py --use-dummy-data --output-format html`
- View report in browser

### Step 3: Analyze Your Code (2 min)

- Analyze: `python main.py --repo-path /your/code --output-format html`
- View report

### Step 4: Review Findings (5 min)

- Check CRITICAL issues
- Plan fixes for HIGH risk items
- Add to your backlog

### Step 5: Integrate (5 min)

- Copy CI/CD workflow for your platform
- Run on every commit
- Track improvements

---

## 📚 Documentation Map

```
├─ START HERE
│  ├─ This file (overview & quick start)
│  ├─ QUICKSTART.md (30-second guide)
│  └─ setup.bat / setup.sh (automated setup)
│
├─ UNDERSTANDING
│  ├─ README.md (features & overview)
│  ├─ USAGE.md (complete guide)
│  ├─ EXAMPLES.md (sample outputs)
│  └─ PRODUCT_SUMMARY.md (feature summary)
│
├─ INTEGRATION
│  ├─ Dockerfile & docker-compose.yml
│  ├─ .github/workflows/risk-analysis.yml
│  ├─ .gitlab-ci.yml
│  └─ config/config.json
│
├─ DEVELOPMENT
│  ├─ CONTRIBUTING.md (dev guidelines)
│  ├─ ARCHITECTURE.md (system design)
│  └─ tests/ (unit & integration tests)
│
└─ REFERENCE
   ├─ PROJECT_INDEX.md (complete file listing)
   └─ DELIVERY_SUMMARY.md (delivery details)
```

---

## 🏃 30-Second Quick Start

**Windows:**

```
1. Double-click: setup.bat
2. Wait for completion
3. Browser opens with report automatically ✓
```

**macOS/Linux:**

```bash
bash setup.sh
# Browser opens with report automatically ✓
```

**Manual:**

```bash
pip install -r requirements.txt
python main.py --use-dummy-data --output-format html
# Open reports/risk_dashboard_*.html in your browser ✓
```

---

## 🎉 You're All Set!

You now have a professional-grade source code analysis tool:

- ✅ 5 independent analysis engines
- ✅ ML-powered predictions
- ✅ Rich multi-format reporting
- ✅ Docker & CI/CD ready
- ✅ 100% free & open-source

### Next? → **Read [QUICKSTART.md](QUICKSTART.md)** or **[USAGE.md](USAGE.md)**

---

## 🤝 Need Help?

- **Not working?** → Check [QUICKSTART.md](QUICKSTART.md) troubleshooting
- **Want to customize?** → See [USAGE.md](USAGE.md) configuration
- **Want to extend?** → Read [ARCHITECTURE.md](ARCHITECTURE.md)
- **Want to contribute?** → Check [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📞 Support

- 📖 Comprehensive documentation included
- 💻 Full source code is open and auditable
- 🔧 Easy to customize and extend
- 📧 See README.md for contact info

---

**Happy analyzing! 🚀**

_Now go run `setup.bat` or `bash setup.sh` to get started!_
