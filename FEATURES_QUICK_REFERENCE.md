# 📊 Risk Radar Enhanced Features - Quick Reference

## What's New?

We've added 4 powerful features that generate real business value:

| Feature            | What It Shows                         | Business Value                          |
| ------------------ | ------------------------------------- | --------------------------------------- |
| **Trend Analysis** | Risk improving/degrading over time    | Track progress, forecast CRITICAL risk  |
| **Technical Debt** | Debt in hours/weeks/dollars           | Budget justification, sprint planning   |
| **Test Coverage**  | Which critical code is untested       | Risk mitigation, quality prioritization |
| **Team Impact**    | Developer ownership & knowledge silos | Prevent bottlenecks, manage risk        |

---

## 🎯 Key Metrics Now Available

### Trend Analysis

```
Risk Score: 55.2 → 50.5 (improving -8.5%)
Critical Issues: 3 → 1 (down 2)
Improvement Rate: 67%
Days Until Critical: Never (improving)
```

### Technical Debt

```
Total: 312.5 hours ($46,875)
Time: 7.8 weeks (2 developers)
Breakdown:
  - Complexity: 68 hours
  - Security: 32 hours (HIGHEST PRIORITY)
  - Churn: 64 hours
  - Bus Factor: 84 hours (CRITICAL)
  - Dependencies: 64.5 hours
```

### Test Coverage

```
Overall: 62.5%
With Tests: 18 files
Without Tests: 11 files
Critical Untested: 3 modules ⚠️
Recommendation: URGENT - Add tests for payment processor
```

### Team Impact

```
Team Risk: 145.3/100
Developers: 5
Bus Factors: 3 (Bob, Alice, Eve at risk)
Knowledge Gaps: 2 (isolated devs)
Actions: 7 recommended
```

---

## 📈 How to Use These Features

### 1. **View the Dashboard**

```bash
python main.py --use-dummy-data --output-format html
# Opens risk_dashboard_YYYYMMDD_HHMMSS.html
```

**Look for these sections:**

- 📈 Risk Trends & Historical Comparison
- 💰 Technical Debt Analysis
- 🧪 Test Coverage Analysis
- 👥 Team Impact & Knowledge Distribution

### 2. **Get Raw Data (JSON)**

```bash
python main.py --output-format json
# risk_report_YYYYMMDD_HHMMSS.json
```

Contains all features plus detailed item lists.

### 3. **Export to Spreadsheet**

```bash
python main.py --output-format csv
# risk_report_YYYYMMDD_HHMMSS.csv
```

Rows include: file path, scores, recommendations.

---

## 💡 Use Cases

### **For Engineering Leaders**

- Review **Technical Debt** section
- Prioritize work based on cost/benefit
- Justify hiring for tech debt reduction
- Track progress over time with **Trends**

### **For Project Managers**

- Use **Technical Debt** estimates for sprint planning
- Reference **Team Impact** for resource allocation
- Track **Trends** for velocity forecasting
- Show progress to stakeholders

### **For Security Teams**

- Focus on security debt items (highest priority)
- Use **Test Coverage** to identify gaps
- Review **Team Impact** for knowledge risks
- Track improvements with **Trends**

### **For Dev Teams**

- See **Test Coverage** gaps (write tests here first)
- Understand **Team Impact** bottlenecks
- Use debt items as refactoring tasks
- Monitor **Trends** for improvement

### **For Executives**

- See business cost of debt (\$46k)
- Understand timeline (7-8 weeks)
- Know organizational risks (bus factors)
- Track progress (trend improvements)

---

## 📊 Understanding Each Feature

### Trend Analysis

**Shows:** How code health changes over time

**Key Numbers:**

- **Risk Change %**: -8.5% = improving ✓ | +5% = degrading ⚠️
- **Improvement Rate**: 67% = strong positive momentum
- **Days Until Critical**: If degrading, when you hit 80/100
- **Critical/High Changes**: How many new risky modules

**Action:**

- If improving: celebrate & maintain momentum
- If degrading: urgent review needed
- If stable: continue current practices

---

### Technical Debt

**Shows:** What fixing the code will cost (time + money)

**Key Numbers:**

- **Total Hours**: Full effort needed (all changes)
- **Estimated Cost**: Hours × \$150/hr developer rate
- **Estimated Weeks**: Hours / 40 hour work week
- **Team Months**: How long for 2 devs working full-time

**By Type Priority:**

1. **Bus Factor Risk** (84h) - Knowledge silos
2. **Churn** (64h) - High-change files
3. **Complexity** (68h) - Hard to understand
4. **Security** (32h) - Vulnerabilities
5. **Dependencies** (64.5h) - Upgrade risks

**Top Items:** Specific files ranked by effort

**Action:**

- Take to leadership with cost/timeline
- Break into sprints (chunks of 20-40h)
- Track progress (hours completed)
- Measure ROI (bugs prevented, velocity gained)

---

### Test Coverage

**Shows:** What code is untested + where to focus

**Key Numbers:**

- **Coverage %**: 62.5% = below optimal (target: 80%+)
- **Files with/without Tests**: Ratio of tested code
- **Critical Untested**: HIGH/CRITICAL risk code with NO tests
- **Priority**: CRITICAL/HIGH/MEDIUM/LOW

**Coverage Gaps:** Listed by risk level + untested functions

**Recommendations:**

- Focus on critical/high-risk modules first
- Use pytest (Python), Jest (JavaScript)
- Pair programming on complex code
- CI/CD should block coverage regression

**Action:**

- Use list as testing sprint backlog
- Fix critical gaps ASAP
- Aim for 80%+ on critical paths
- Monitor coverage % in CI/CD

---

### Team Impact

**Shows:** Who knows what, and organizational risks

**Key Numbers:**

- **Team Risk Exposure**: 145.3 = high (average module risk score)
- **Knowledge Distribution**: Who owns what
- **Bus Factors**: 1-person critical dependencies
- **Collaboration Gaps**: Isolated devs & load imbalance

**Critical Dependencies:** People at risk if they leave

- Payment System: Only Bob knows it
- Auth System: Only Alice knows it
- Transactions: Only Eve knows it

**Recommended Actions:**

- Document critical modules immediately
- Schedule pair programming (Alice↔Diana 3x/week)
- Redistribute overloaded developer work
- Cross-train on high-risk areas

**Action:**

- Schedule 1:1s with critical-path people
- Create pairing/mentoring plan
- Document key systems
- Start knowledge transfer this sprint

---

## 🎯 Dashboard Sections (HTML)

When you open the HTML dashboard, you'll see:

1. **Overall Risk Score** (top card)

   - Main metric: 0-100 scale
   - Color: Red (CRITICAL) → Yellow → Green (LOW)

2. **📈 Risk Trends** (new)

   - Improving/degrading indicator
   - % change, improvement rate
   - Days until critical (if degrading)

3. **💰 Technical Debt** (new)

   - Total hours, cost, timeline
   - Debt by type breakdown
   - Top 10 debt items ranked

4. **🧪 Test Coverage** (new)

   - Coverage percentage bar
   - Files with/without tests
   - Critical untested modules
   - Testing recommendations

5. **👥 Team Impact** (new)

   - Knowledge distribution chart
   - Bus factors list
   - Recommended actions

6. **Existing sections:**
   - Critical modules
   - High-risk modules
   - Security issues
   - Failure predictions
   - Dependencies

---

## 🚀 Getting Value Quick

### Week 1: Understand

- Read the dashboard sections (20 min)
- Review technical debt top 10 (10 min)
- Check test coverage critical gaps (10 min)
- List bus factors on your team (5 min)

### Week 2-4: Act

- Schedule knowledge transfer sessions
- Start with highest-priority debt items
- Add tests for critical untested code
- Document critical systems

### Monthly: Track

- Rerun analysis
- Compare with previous months
- Check trend improvements
- Celebrate progress

---

## 📋 Checklists

### For Your First Analysis

- [ ] Run `python main.py --use-dummy-data --output-format html`
- [ ] Open the HTML dashboard
- [ ] Read all 4 new sections
- [ ] Note top 3 action items
- [ ] Share with team

### For Technical Debt

- [ ] Review the cost (\$\$\$)
- [ ] Review the timeline (weeks)
- [ ] Identify top 3 items to fix
- [ ] Schedule sprint planning
- [ ] Assign ownership

### For Test Coverage

- [ ] Identify critical untested code
- [ ] Create testing tasks
- [ ] Assign to developers
- [ ] Add to CI/CD checks
- [ ] Track coverage % over time

### For Team Impact

- [ ] Identify bus factors (people at risk)
- [ ] Schedule pairing sessions
- [ ] Create documentation tasks
- [ ] Plan knowledge transfer
- [ ] Monitor team health

---

## 🔄 Continuous Improvement

**Monthly Cycle:**

1. Run analysis (5 min)
2. Compare with last month
3. Check trend direction (improving? ✓)
4. Review progress on action items
5. Update priorities for next sprint
6. Share results with team/leadership

**Quarterly:**

- Present trend data to executives
- Showcase debt reduction progress
- Highlight team resilience improvements
- Plan next quarter's focus areas

---

## FAQ

**Q: How accurate are these numbers?**
A: Based on real code metrics + statistical models. Dummy data for demo, real data for actual repos.

**Q: Can I customize the effort estimates?**
A: Yes - edit the rates in `src/technical_debt_calculator.py` (BASE_COMPLEXITY_COST, SECURITY_ISSUE_COST, etc.)

**Q: How often should I run analysis?**
A: Weekly to monitor trends, monthly for leadership reports, before major releases.

**Q: What if bus factors can't be fixed?**
A: Start with documentation, then pair programming, then gradual knowledge transfer.

**Q: How do I improve test coverage fast?**
A: Focus on CRITICAL modules first, use auto-generated tests as a start, aim for incremental improvement.

---

## Need Help?

See these documents:

- **USAGE.md** - Detailed usage guide
- **ARCHITECTURE.md** - How everything works
- **EXAMPLES.md** - Sample outputs
- **FEATURES_NEW.md** - Deep dive on new features
