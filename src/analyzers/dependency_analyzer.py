"""Dependency analysis and upgrade risk assessment"""

import os
import re
import json
import subprocess
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from packaging import version as pkg_version

from src.models import DependencyRisk


class DependencyAnalyzer:
    """Analyzes project dependencies and their risks"""

    def __init__(self):
        # Known vulnerability database (simplified)
        self.known_vulnerabilities = {
            'django': {
                '<3.0.0': 5,  # version: number of vulnerabilities
                '<2.2.28': 8,
                '<3.2.15': 6,
            },
            'requests': {
                '<2.28.0': 2,
            },
            'flask': {
                '<2.0.0': 3,
            },
            'sqlalchemy': {
                '<1.4.0': 4,
            },
        }

    def analyze_requirements_file(self, requirements_path: str) -> List[DependencyRisk]:
        """Analyze a requirements.txt file for dependency risks"""
        if not os.path.exists(requirements_path):
            return []

        dependencies = self._parse_requirements(requirements_path)
        risks = []

        for package_name, current_version in dependencies:
            risk = self._assess_dependency(package_name, current_version)
            if risk:
                risks.append(risk)

        return risks

    def analyze_poetry_lock(self, poetry_lock_path: str) -> List[DependencyRisk]:
        """Analyze a poetry.lock file"""
        if not os.path.exists(poetry_lock_path):
            return []

        try:
            import toml
            with open(poetry_lock_path, 'r') as f:
                data = toml.load(f)

            risks = []
            for package_data in data.get('package', []):
                package_name = package_data.get('name', '')
                current_version = package_data.get('version', '')
                
                risk = self._assess_dependency(package_name, current_version)
                if risk:
                    risks.append(risk)

            return risks
        except:
            return []

    def analyze_package_json(self, package_json_path: str) -> List[DependencyRisk]:
        """Analyze a package.json file (Node.js)"""
        if not os.path.exists(package_json_path):
            return []

        try:
            with open(package_json_path, 'r') as f:
                data = json.load(f)

            dependencies = {}
            for dep_type in ['dependencies', 'devDependencies', 'peerDependencies']:
                dependencies.update(data.get(dep_type, {}))

            risks = []
            for package_name, version_spec in dependencies.items():
                # Extract version from spec (e.g., "^1.2.3" -> "1.2.3")
                clean_version = re.sub(r'^[\^~>=<]', '', version_spec).split(' ')[0]
                
                risk = self._assess_dependency(package_name, clean_version)
                if risk:
                    risks.append(risk)

            return risks
        except:
            return []

    def analyze_gemfile(self, gemfile_path: str) -> List[DependencyRisk]:
        """Analyze a Gemfile (Ruby)"""
        if not os.path.exists(gemfile_path):
            return []

        risks = []
        try:
            with open(gemfile_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse gem declarations
                    match = re.match(r"gem\s+['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?", line)
                    if match:
                        package_name = match.group(1)
                        version = match.group(2) or ''
                        
                        risk = self._assess_dependency(package_name, version)
                        if risk:
                            risks.append(risk)

            return risks
        except:
            return []

    def scan_directory(self, directory: str) -> List[DependencyRisk]:
        """Scan directory for all dependency files"""
        all_risks = []

        # Check common dependency files
        dependency_files = {
            'requirements.txt': self.analyze_requirements_file,
            'poetry.lock': self.analyze_poetry_lock,
            'package.json': self.analyze_package_json,
            'Gemfile': self.analyze_gemfile,
            'pom.xml': lambda x: [],  # TODO: Implement Maven support
            'build.gradle': lambda x: [],  # TODO: Implement Gradle support
        }

        for root, dirs, files in os.walk(directory):
            # Skip common non-dependency directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', 'venv', '__pycache__']]

            for file in files:
                file_path = os.path.join(root, file)
                
                if file in dependency_files:
                    try:
                        risks = dependency_files[file](file_path)
                        all_risks.extend(risks)
                    except Exception as e:
                        print(f"Warning: Could not analyze {file_path}: {e}")

        return all_risks

    def _parse_requirements(self, requirements_path: str) -> List[Tuple[str, str]]:
        """Parse requirements.txt format"""
        dependencies = []

        try:
            with open(requirements_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Skip -r, -f, etc. directives
                    if line.startswith('-'):
                        continue
                    
                    # Parse package==version format
                    match = re.match(r'^([a-zA-Z0-9_\-]+)(?:==|>=|<=|>|<|~=)(.+)$', line)
                    if match:
                        package_name = match.group(1)
                        version = match.group(2).split(';')[0].strip()  # Remove extras
                        dependencies.append((package_name, version))
                    else:
                        # Package without version
                        package_name = line.split('[')[0].strip()  # Remove extras
                        dependencies.append((package_name, ''))

        except Exception as e:
            print(f"Warning: Could not parse {requirements_path}: {e}")

        return dependencies

    def _assess_dependency(self, package_name: str, current_version: str) -> Optional[DependencyRisk]:
        """Assess risk for a single dependency"""
        try:
            latest_version = self._get_latest_version(package_name)
            is_outdated = self._is_outdated(current_version, latest_version)
            known_vulns = self._count_known_vulnerabilities(package_name, current_version)
            breaking_changes_risk = self._assess_breaking_changes(package_name, current_version, latest_version)
            upgrade_risk = self._calculate_upgrade_risk(
                is_outdated, known_vulns, breaking_changes_risk
            )

            return DependencyRisk(
                package_name=package_name,
                current_version=current_version,
                latest_version=latest_version,
                is_outdated=is_outdated,
                known_vulnerabilities=known_vulns,
                upgrade_risk_score=upgrade_risk,
                breaking_changes_risk=breaking_changes_risk
            )
        except Exception as e:
            print(f"Warning: Could not assess {package_name}: {e}")
            return None

    def _get_latest_version(self, package_name: str) -> Optional[str]:
        """Get latest version of a package (simplified)"""
        try:
            # Try pip API (for Python)
            import urllib.request
            url = f"https://pypi.org/pypi/{package_name}/json"
            with urllib.request.urlopen(url, timeout=2) as response:
                data = json.loads(response.read().decode())
                return data['info']['version']
        except:
            pass

        # Fallback - return dummy latest version
        return f"2.0.0"

    def _is_outdated(self, current: str, latest: Optional[str]) -> bool:
        """Check if current version is outdated"""
        if not latest or not current:
            return False

        try:
            return pkg_version.parse(current) < pkg_version.parse(latest)
        except:
            return False

    def _count_known_vulnerabilities(self, package_name: str, version: str) -> int:
        """Count known vulnerabilities for a package version"""
        package_lower = package_name.lower().replace('-', '_')
        
        if package_lower in self.known_vulnerabilities:
            vulns = self.known_vulnerabilities[package_lower]
            
            # Check which version ranges this version falls into
            total_vulns = 0
            for version_spec, count in vulns.items():
                if self._version_matches_spec(version, version_spec):
                    total_vulns += count
            
            return total_vulns

        return 0

    def _version_matches_spec(self, version: str, spec: str) -> bool:
        """Check if version matches a specification"""
        try:
            if '<' in spec:
                version_num = spec.replace('<', '').strip()
                return pkg_version.parse(version) < pkg_version.parse(version_num)
            elif '>' in spec:
                version_num = spec.replace('>', '').strip()
                return pkg_version.parse(version) > pkg_version.parse(version_num)
        except:
            pass
        return False

    def _assess_breaking_changes(self, package_name: str, current: str, latest: Optional[str]) -> float:
        """Assess risk of breaking changes (0-1)"""
        if not current or not latest:
            return 0.0

        try:
            curr_parts = current.split('.')
            latest_parts = latest.split('.')
            
            # Major version difference indicates high breaking change risk
            if len(curr_parts) > 0 and len(latest_parts) > 0:
                curr_major = int(curr_parts[0])
                latest_major = int(latest_parts[0])
                
                if latest_major > curr_major:
                    # Each major version jump increases risk
                    return min((latest_major - curr_major) * 0.3, 1.0)
        except:
            pass

        return 0.0

    def _calculate_upgrade_risk(self, is_outdated: bool, known_vulns: int, breaking_changes_risk: float) -> float:
        """Calculate overall upgrade risk score (0-100)"""
        risk_score = 0.0

        # Outdated packages have higher risk
        if is_outdated:
            risk_score += 20

        # Known vulnerabilities add significant risk
        risk_score += min(known_vulns * 10, 40)

        # Breaking changes add risk
        risk_score += breaking_changes_risk * 30

        return min(risk_score, 100.0)


class DummyDependencyAnalyzer:
    """Generates realistic dummy dependency risks"""

    def __init__(self):
        self.package_names = [
            'django', 'flask', 'requests', 'numpy', 'pandas', 'sqlalchemy',
            'celery', 'redis', 'mongoengine', 'psycopg2', 'pymongo',
            'cryptography', 'jwt', 'bcrypt', 'pillow', 'beautifulsoup4'
        ]

    def analyze_directory(self, directory: str) -> List[DependencyRisk]:
        """Generate dummy dependency risks"""
        import random

        risks = []
        
        # Generate risks for random packages
        num_packages = random.randint(5, 15)
        selected_packages = random.sample(self.package_names, min(num_packages, len(self.package_names)))

        for package_name in selected_packages:
            seed = hash(package_name) % 2**32
            random.seed(seed)

            current_version = f"{random.randint(1, 3)}.{random.randint(0, 20)}.{random.randint(0, 10)}"
            latest_version = f"{random.randint(1, 4)}.{random.randint(0, 20)}.{random.randint(0, 10)}"
            is_outdated = random.random() > 0.6
            known_vulns = random.randint(0, 8) if is_outdated else random.randint(0, 2)
            breaking_changes = random.random() * 0.7 if is_outdated else random.random() * 0.2
            upgrade_risk = min(is_outdated * 20 + known_vulns * 10 + breaking_changes * 30, 100.0)

            risks.append(DependencyRisk(
                package_name=package_name,
                current_version=current_version,
                latest_version=latest_version,
                is_outdated=is_outdated,
                known_vulnerabilities=known_vulns,
                upgrade_risk_score=upgrade_risk,
                breaking_changes_risk=breaking_changes
            ))

        risks.sort(key=lambda x: x.upgrade_risk_score, reverse=True)
        return risks

    def scan_directory(self, directory: str) -> List[DependencyRisk]:
        """Generate dummy risks for directory"""
        return self.analyze_directory(directory)

    def analyze_requirements_file(self, path: str) -> List[DependencyRisk]:
        """Generate dummy risks for requirements file"""
        return self.analyze_directory(os.path.dirname(path))
