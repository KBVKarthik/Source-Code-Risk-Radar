"""Git history analysis for churn, ownership, and bus factor"""

import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import subprocess
import json

from src.models import GitMetrics


class GitAnalyzer:
    """Analyzes git history to extract metrics"""

    def __init__(self, repo_path: str, months_to_analyze: int = 12, min_commits: int = 5):
        self.repo_path = repo_path
        self.months_to_analyze = months_to_analyze
        self.min_commits = min_commits
        self.git_log_cache = {}

    def get_git_metrics(self, file_path: str) -> Optional[GitMetrics]:
        """Extract git metrics for a file"""
        try:
            # Get commit count
            commits = self._get_commits_for_file(file_path)
            if len(commits) < self.min_commits:
                return None

            unique_authors = len(set(commit['author'] for commit in commits))
            bus_factor = self._calculate_bus_factor(commits)
            churn_score = self._calculate_churn_score(commits)
            
            last_commit = commits[0]  # Most recent
            last_modified_date = datetime.fromisoformat(last_commit['timestamp'])
            last_modified_days = (datetime.now() - last_modified_date).days
            
            creation_date = commits[-1]['timestamp']  # Oldest
            creation_datetime = datetime.fromisoformat(creation_date)
            
            # Commits per month
            time_span_months = max((datetime.now() - creation_datetime).days / 30, 1)
            modification_frequency = len(commits) / time_span_months

            return GitMetrics(
                file_path=file_path,
                total_commits=len(commits),
                unique_authors=unique_authors,
                bus_factor=bus_factor,
                churn_score=churn_score,
                last_modified_days_ago=last_modified_days,
                creation_date=creation_datetime,
                modification_frequency=modification_frequency
            )
        except Exception as e:
            print(f"Warning: Could not analyze git history for {file_path}: {e}")
            return None

    def _get_commits_for_file(self, file_path: str) -> List[Dict]:
        """Get all commits for a file"""
        if file_path in self.git_log_cache:
            return self.git_log_cache[file_path]

        try:
            # Build git log command
            cmd = [
                'git', '-C', self.repo_path, 'log',
                '--follow',
                '--format=%H|%an|%ae|%aI|%s',
                '--',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                parts = line.split('|')
                if len(parts) >= 4:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'timestamp': parts[3],
                        'message': parts[4] if len(parts) > 4 else ''
                    })

            self.git_log_cache[file_path] = commits
            return commits
        except Exception as e:
            print(f"Warning: git log failed for {file_path}: {e}")
            return []

    def _calculate_bus_factor(self, commits: List[Dict]) -> int:
        """
        Calculate bus factor (minimum number of people needed to understand code)
        Returns the minimum number of developers who together authored most commits
        """
        if not commits:
            return 0
        
        # Get author commit counts
        author_commits = Counter(commit['author'] for commit in commits)
        total_commits = len(commits)
        
        # Sort by commit count
        sorted_authors = sorted(author_commits.items(), key=lambda x: x[1], reverse=True)
        
        # Find minimum number of people needed for 70% of commits
        cumulative = 0
        for count, (author, num_commits) in enumerate(sorted_authors, 1):
            cumulative += num_commits
            if cumulative >= (total_commits * 0.7):
                return count
        
        return max(1, len(sorted_authors))

    def _calculate_churn_score(self, commits: List[Dict]) -> float:
        """
        Calculate churn score (0-1) based on commit frequency
        Higher = more unstable/changing
        """
        if len(commits) < 2:
            return 0.0
        
        # Get commits in last 3 months
        three_months_ago = datetime.now() - timedelta(days=90)
        recent_commits = [
            c for c in commits 
            if datetime.fromisoformat(c['timestamp']) > three_months_ago
        ]
        
        # Normalize by expected rate (assuming ~2-3 commits per month per file is normal)
        recent_rate = len(recent_commits) / 3.0
        
        # Cap at 1.0 and return
        return min(recent_rate, 1.0)

    def get_repository_stats(self) -> Dict:
        """Get overall repository statistics"""
        try:
            # Total commits
            cmd = ['git', '-C', self.repo_path, 'rev-list', '--count', 'HEAD']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            total_commits = int(result.stdout.strip()) if result.returncode == 0 else 0

            # Total contributors
            cmd = ['git', '-C', self.repo_path, 'log', '--format=%an', 'HEAD']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            unique_contributors = len(set(result.stdout.strip().split('\n'))) if result.returncode == 0 else 0

            # Repository age
            cmd = ['git', '-C', self.repo_path, 'log', '--follow', '--format=%aI', 'HEAD', '|', 'tail', '-1']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=True)
            try:
                oldest_commit = datetime.fromisoformat(result.stdout.strip().split('\n')[-1])
                repo_age_days = (datetime.now() - oldest_commit).days
            except:
                repo_age_days = 0

            return {
                'total_commits': total_commits,
                'unique_contributors': unique_contributors,
                'repository_age_days': repo_age_days
            }
        except Exception as e:
            print(f"Warning: Could not get repository stats: {e}")
            return {
                'total_commits': 0,
                'unique_contributors': 0,
                'repository_age_days': 0
            }


class DummyGitAnalyzer:
    """Fallback analyzer that generates realistic dummy data when git is unavailable"""

    def __init__(self, repo_path: str = ".", months_to_analyze: int = 12, min_commits: int = 5):
        self.repo_path = repo_path
        self.months_to_analyze = months_to_analyze
        self.min_commits = min_commits
        # Seed for reproducibility
        import random
        random.seed(hash(repo_path) % 2**32)

    def get_git_metrics(self, file_path: str) -> Optional[GitMetrics]:
        """Generate realistic dummy git metrics"""
        import random
        
        # Ensure different files get different but consistent metrics
        seed = hash(file_path) % 2**32
        random.seed(seed)

        total_commits = random.randint(5, 150)
        unique_authors = random.randint(1, min(8, total_commits // 3))
        
        # Bus factor calculation
        bus_factor = random.randint(1, max(2, unique_authors // 2))
        
        # Churn score (more active files tend to be riskier)
        churn_score = random.random() * 0.8 if random.random() > 0.4 else random.random() * 0.3
        
        last_modified_days = random.randint(0, 365)
        modification_frequency = random.uniform(0.5, 8.0)
        
        creation_date = datetime.now() - timedelta(days=random.randint(90, 1095))

        return GitMetrics(
            file_path=file_path,
            total_commits=total_commits,
            unique_authors=unique_authors,
            bus_factor=bus_factor,
            churn_score=churn_score,
            last_modified_days_ago=last_modified_days,
            creation_date=creation_date,
            modification_frequency=modification_frequency
        )

    def get_repository_stats(self) -> Dict:
        """Generate dummy repository statistics"""
        import random
        return {
            'total_commits': random.randint(500, 5000),
            'unique_contributors': random.randint(3, 25),
            'repository_age_days': random.randint(180, 1800)
        }
