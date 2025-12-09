"""Team and organizational impact analysis"""

from dataclasses import dataclass
from typing import List, Dict
from src.models import RiskReport, RiskLevel


@dataclass
class DeveloperRiskProfile:
    """Developer's risk exposure"""
    name: str
    modules_owned: int
    critical_modules: int
    high_risk_modules: int
    total_risk_score: float
    knowledge_silo: bool
    collaboration_score: float  # 0-100, higher is better
    bus_factor_risk: bool


@dataclass
class TeamImpactAnalysis:
    """Team impact and dynamics analysis"""
    knowledge_distribution: Dict[str, int]
    critical_dependencies: List[str]  # People who are bottlenecks
    collaboration_gaps: List[str]
    team_risk_exposure: float
    recommended_actions: List[str]
    knowledge_transfer_priority: List[str]
    developer_profiles: List[DeveloperRiskProfile]


class TeamImpactAnalyzer:
    """Analyzes team impact of code risks"""

    def analyze_team_impact(self, report: RiskReport) -> TeamImpactAnalysis:
        """Analyze team impact from code metrics"""
        
        # Extract developer info from git metrics and comments
        dev_profiles = self._build_developer_profiles(report)
        
        # Identify knowledge silos
        critical_people = [d.name for d in dev_profiles if d.knowledge_silo]
        
        # Calculate collaboration gaps
        collab_gaps = self._identify_collaboration_gaps(dev_profiles)
        
        # Team risk exposure
        team_risk = sum(p.total_risk_score for p in dev_profiles) / max(len(dev_profiles), 1)
        
        # Generate recommendations
        recs = self._generate_team_recommendations(dev_profiles, collab_gaps)
        
        return TeamImpactAnalysis(
            knowledge_distribution={p.name: p.modules_owned for p in dev_profiles},
            critical_dependencies=critical_people,
            collaboration_gaps=collab_gaps,
            team_risk_exposure=team_risk,
            recommended_actions=recs,
            knowledge_transfer_priority=self._prioritize_knowledge_transfer(dev_profiles),
            developer_profiles=dev_profiles
        )

    def _build_developer_profiles(self, report: RiskReport) -> List[DeveloperRiskProfile]:
        """Build developer profiles from module data"""
        profiles = {}
        
        for module in report.modules:
            # Simulate developer ownership based on file characteristics
            # In real app, would come from git blame/history
            dev_name = self._infer_developer(module.file_path)
            
            if dev_name not in profiles:
                profiles[dev_name] = {
                    'modules': 0,
                    'critical': 0,
                    'high': 0,
                    'risk_total': 0.0,
                    'collab_score': 80.0
                }
            
            profiles[dev_name]['modules'] += 1
            profiles[dev_name]['risk_total'] += module.overall_risk_score
            
            if module.risk_level == RiskLevel.CRITICAL:
                profiles[dev_name]['critical'] += 1
            elif module.risk_level == RiskLevel.HIGH:
                profiles[dev_name]['high'] += 1
        
        # Convert to profiles
        result = []
        for name, data in profiles.items():
            critical_modules = data['critical']
            high_modules = data['high']
            total_modules = data['modules']
            
            # Bus factor = if they own >40% of critical code
            bus_factor = critical_modules > 2 or (critical_modules / max(total_modules, 1) > 0.3)
            
            # Collab score = based on how spread out their work is
            collab = 100 - min(90, (critical_modules * 15) + (data['risk_total'] / 10))
            
            profile = DeveloperRiskProfile(
                name=name,
                modules_owned=total_modules,
                critical_modules=critical_modules,
                high_risk_modules=high_modules,
                total_risk_score=data['risk_total'],
                knowledge_silo=bus_factor,
                collaboration_score=max(0, collab),
                bus_factor_risk=bus_factor
            )
            result.append(profile)
        
        # Sort by risk exposure
        result.sort(key=lambda p: p.total_risk_score, reverse=True)
        return result

    def _infer_developer(self, file_path: str) -> str:
        """Infer developer from file characteristics"""
        # This would normally come from git blame in real implementation
        # Simulate based on filename patterns
        
        if 'auth' in file_path.lower():
            return 'Alice (Security Lead)'
        elif 'api' in file_path.lower():
            return 'Bob (Backend)'
        elif 'database' in file_path.lower():
            return 'Charlie (DBA)'
        elif 'frontend' in file_path.lower() or 'ui' in file_path.lower():
            return 'Diana (Frontend)'
        elif 'payment' in file_path.lower() or 'transaction' in file_path.lower():
            return 'Eve (Payments)'
        else:
            return 'Frank (DevOps)'

    def _identify_collaboration_gaps(self, profiles: List[DeveloperRiskProfile]) -> List[str]:
        """Identify collaboration and communication gaps"""
        gaps = []
        
        # Find isolated developers
        isolated = [p for p in profiles if p.collaboration_score < 40]
        if isolated:
            gaps.append(f"Isolation Risk: {isolated[0].name} working in silo on high-risk code. Need pairing sessions.")
        
        # Find unbalanced load
        if profiles:
            avg_modules = sum(p.modules_owned for p in profiles) / len(profiles)
            overloaded = [p for p in profiles if p.modules_owned > avg_modules * 1.5]
            if overloaded:
                gaps.append(f"Load Imbalance: {overloaded[0].name} has {overloaded[0].modules_owned} modules vs team avg of {avg_modules:.0f}. Redistribute work.")
        
        # Find bus factor risks
        bus_factors = [p for p in profiles if p.bus_factor_risk]
        if bus_factors:
            gaps.append(f"Bus Factor: {bus_factors[0].name} is single point of failure for critical code. Document and cross-train immediately.")
        
        return gaps

    def _generate_team_recommendations(self, profiles: List[DeveloperRiskProfile], gaps: List[str]) -> List[str]:
        """Generate team recommendations"""
        recs = []
        
        if not profiles:
            return ["Need team member data to generate recommendations"]
        
        # Add gap-based recs
        recs.extend(gaps)
        
        # High risk developer
        high_risk_devs = [p for p in profiles if p.total_risk_score > 200]
        if high_risk_devs:
            recs.append(f"Code Review: {high_risk_devs[0].name} needs peer review on critical modules. Assign code review buddy.")
        
        # Balanced team
        if len(profiles) > 1:
            recs.append(f"Knowledge Sharing: Schedule pair programming sessions between {profiles[0].name} and {profiles[-1].name}.")
        
        recs.append("Team Training: Schedule security and complexity refactoring workshops.")
        recs.append("Mentoring: Pair junior devs with experienced ones on high-risk areas.")
        
        return recs

    def _prioritize_knowledge_transfer(self, profiles: List[DeveloperRiskProfile]) -> List[str]:
        """Prioritize knowledge transfer activities"""
        transfer = []
        
        # People with knowledge silos
        silo_people = [p for p in profiles if p.knowledge_silo]
        for person in silo_people:
            transfer.append(f"1. {person.name}: Document critical modules and conduct code walkthrough")
        
        # High-risk people
        high_risk = [p for p in profiles if p.total_risk_score > 150]
        for person in high_risk:
            transfer.append(f"2. {person.name}: Refactor high-risk modules with peer support")
        
        # Collaboration improvement
        low_collab = [p for p in profiles if p.collaboration_score < 50]
        for person in low_collab:
            transfer.append(f"3. {person.name}: Increase pair programming (2+ times/week)")
        
        return transfer if transfer else ["Team collaboration is healthy. Continue current practices."]


class DummyTeamImpactAnalyzer:
    """Dummy team analyzer for testing"""

    def analyze_team_impact(self, report: RiskReport) -> TeamImpactAnalysis:
        """Generate realistic team analysis"""
        return TeamImpactAnalysis(
            knowledge_distribution={
                "Alice (Security Lead)": 8,
                "Bob (Backend)": 12,
                "Charlie (DBA)": 6,
                "Diana (Frontend)": 9,
                "Eve (Payments)": 5
            },
            critical_dependencies=[
                "Alice (Security Lead) - owns all auth/security modules",
                "Bob (Backend) - single owner of payment processor",
                "Eve (Payments) - only person familiar with transaction system"
            ],
            collaboration_gaps=[
                "Isolation Risk: Alice working in silo on high-risk auth code. Need pairing sessions.",
                "Bus Factor: Bob is single point of failure for critical payment module. Document immediately.",
                "Load Imbalance: Bob has 12 modules vs team avg of 8. Redistribute work."
            ],
            team_risk_exposure=145.3,
            recommended_actions=[
                "Isolation Risk: Alice working in silo on high-risk auth code. Need pairing sessions.",
                "Bus Factor: Bob is single point of failure for critical payment module. Document immediately.",
                "Load Imbalance: Bob has 12 modules vs team avg of 8. Redistribute work.",
                "Code Review: Bob needs peer review on critical modules. Assign code review buddy.",
                "Knowledge Sharing: Schedule pair programming between Alice and Diana.",
                "Team Training: Schedule security and complexity refactoring workshops.",
                "Mentoring: Pair junior devs with Bob on high-risk payment areas."
            ],
            knowledge_transfer_priority=[
                "1. Alice: Document critical auth modules and conduct code walkthrough",
                "2. Bob: Refactor payment processor with peer support",
                "3. Charlie: Increase pair programming on database changes (2+ times/week)",
                "4. Eve: Document payment flow and transaction handling for team"
            ],
            developer_profiles=[
                DeveloperRiskProfile(
                    name="Bob (Backend)",
                    modules_owned=12,
                    critical_modules=3,
                    high_risk_modules=4,
                    total_risk_score=285.5,
                    knowledge_silo=True,
                    collaboration_score=35.0,
                    bus_factor_risk=True
                ),
                DeveloperRiskProfile(
                    name="Alice (Security Lead)",
                    modules_owned=8,
                    critical_modules=2,
                    high_risk_modules=3,
                    total_risk_score=198.3,
                    knowledge_silo=True,
                    collaboration_score=42.0,
                    bus_factor_risk=True
                ),
            ]
        )
