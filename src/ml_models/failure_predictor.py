"""Machine Learning-based failure point prediction"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import json

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class FailurePredictor:
    """
    Predicts which components are likely to fail in the next N months
    using Random Forest classifier trained on git history patterns
    """

    FEATURE_NAMES = [
        'churn_rate',  # How frequently the file changes
        'cyclomatic_complexity',  # Code complexity
        'file_age_months',  # How old the file is
        'commit_frequency',  # Commits per month
        'author_count',  # Number of different authors
        'bus_factor',  # Single point of failure
        'recent_changes',  # Changes in last 3 months
        'test_coverage_proxy',  # Estimated from naming patterns
    ]

    def __init__(self, prediction_horizon_months: int = 3):
        """
        Initialize the predictor
        
        Args:
            prediction_horizon_months: How many months ahead to predict (default 3)
        """
        self.prediction_horizon_months = prediction_horizon_months
        self.model = None
        self.scaler = None
        self._is_trained = False

    def train_on_dummy_data(self):
        """Train on synthetic historical data"""
        if not SKLEARN_AVAILABLE:
            return

        # Generate synthetic training data
        X, y = self._generate_synthetic_data(n_samples=100)
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestClassifier(
            n_estimators=50,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled, y)
        self._is_trained = True

    def predict_failures(self, file_metrics: List[Dict]) -> List[Dict]:
        """
        Predict which files are likely to fail
        
        Args:
            file_metrics: List of file metric dictionaries with required features
            
        Returns:
            List of predictions with failure probability
        """
        if not SKLEARN_AVAILABLE or not self._is_trained:
            return self._fallback_prediction(file_metrics)

        predictions = []

        for metrics in file_metrics:
            try:
                features = self._extract_features(metrics)
                X = np.array(features).reshape(1, -1)
                X_scaled = self.scaler.transform(X)
                
                # Get probability of failure class (1)
                prob = self.model.predict_proba(X_scaled)[0][1]
                
                predictions.append({
                    'file_path': metrics.get('file_path', 'unknown'),
                    'failure_probability': float(prob),
                    'risk_factors': self._identify_risk_factors(metrics),
                    'recommendation': self._get_recommendation(prob, metrics)
                })
            except Exception as e:
                print(f"Warning: Could not predict for {metrics.get('file_path')}: {e}")

        # Sort by failure probability (highest first)
        predictions.sort(key=lambda x: x['failure_probability'], reverse=True)
        return predictions

    def _extract_features(self, metrics: Dict) -> List[float]:
        """Extract feature vector from metrics"""
        features = []
        
        for feature_name in self.FEATURE_NAMES:
            if feature_name in metrics:
                features.append(float(metrics[feature_name]))
            else:
                # Default values for missing features
                features.append(0.0)
        
        return features

    def _generate_synthetic_data(self, n_samples: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data"""
        np.random.seed(42)
        
        X = np.random.rand(n_samples, len(self.FEATURE_NAMES))
        
        # Create labels based on heuristic rules
        # Files are more likely to fail if they have high churn, high complexity, or low test coverage
        y = np.zeros(n_samples, dtype=int)
        
        for i in range(n_samples):
            churn_rate = X[i, 0]
            complexity = X[i, 1]
            commit_freq = X[i, 3]
            author_count = X[i, 4]
            bus_factor = X[i, 5]
            recent_changes = X[i, 6]
            test_coverage = X[i, 7]
            
            # Failure factors
            failure_score = (churn_rate * 0.3) + (complexity * 0.2) + \
                          (commit_freq * 0.15) + (bus_factor * 0.2) + \
                          (recent_changes * 0.1) + ((1 - test_coverage) * 0.05)
            
            # Higher author count reduces failure probability
            failure_score *= (1 - author_count * 0.05)
            
            y[i] = 1 if failure_score > 0.5 else 0
        
        return X, y

    def _fallback_prediction(self, file_metrics: List[Dict]) -> List[Dict]:
        """Fallback prediction using heuristic rules"""
        predictions = []

        for metrics in file_metrics:
            # Calculate failure probability based on heuristics
            prob = self._calculate_failure_probability_heuristic(metrics)
            
            predictions.append({
                'file_path': metrics.get('file_path', 'unknown'),
                'failure_probability': prob,
                'risk_factors': self._identify_risk_factors(metrics),
                'recommendation': self._get_recommendation(prob, metrics)
            })

        predictions.sort(key=lambda x: x['failure_probability'], reverse=True)
        return predictions

    def _calculate_failure_probability_heuristic(self, metrics: Dict) -> float:
        """Calculate failure probability using heuristic rules"""
        prob = 0.0

        # High churn increases failure probability
        churn = metrics.get('churn_rate', 0.0)
        prob += churn * 0.3

        # High complexity increases failure probability
        complexity = metrics.get('cyclomatic_complexity', 0)
        prob += min(complexity / 30.0, 0.3)  # Cap at 0.3

        # High commit frequency (unstable file)
        commit_freq = metrics.get('commit_frequency', 0)
        prob += min(commit_freq / 10.0, 0.15)  # Cap at 0.15

        # Bus factor = 1 increases failure probability
        bus_factor = metrics.get('bus_factor', 0)
        if bus_factor == 1:
            prob += 0.2

        # Recent changes to complex code increase failure probability
        recent = metrics.get('recent_changes', 0)
        prob += min(recent / 20.0, 0.1)  # Cap at 0.1

        # Low test coverage (estimated) increases failure probability
        test_coverage = metrics.get('test_coverage_proxy', 0.5)
        prob += (1 - test_coverage) * 0.05

        # Normalize to 0-1
        prob = min(prob, 1.0)

        return prob

    def _identify_risk_factors(self, metrics: Dict) -> List[str]:
        """Identify key risk factors for a file"""
        risk_factors = []

        if metrics.get('churn_rate', 0) > 0.5:
            risk_factors.append('High code churn')

        if metrics.get('cyclomatic_complexity', 0) > 20:
            risk_factors.append('High cyclomatic complexity')

        if metrics.get('bus_factor', 0) == 1:
            risk_factors.append('Single point of failure (bus factor = 1)')

        if metrics.get('commit_frequency', 0) > 5:
            risk_factors.append('Unstable (frequent commits)')

        if metrics.get('author_count', 0) <= 1:
            risk_factors.append('Limited team knowledge')

        if metrics.get('lines_of_code', 0) > 300:
            risk_factors.append('High lines of code')

        return risk_factors

    def _get_recommendation(self, prob: float, metrics: Dict) -> str:
        """Get recommendations based on failure probability and metrics"""
        if prob >= 0.7:
            return 'CRITICAL: Prioritize refactoring and testing immediately'
        elif prob >= 0.5:
            return 'HIGH: Schedule refactoring and increase test coverage'
        elif prob >= 0.3:
            return 'MEDIUM: Plan improvements and document edge cases'
        else:
            return 'LOW: Monitor and maintain current quality standards'


class DummyFailurePredictor:
    """Generates realistic dummy failure predictions"""

    def __init__(self, prediction_horizon_months: int = 3):
        self.prediction_horizon_months = prediction_horizon_months

    def predict_failures(self, file_metrics: List[Dict]) -> List[Dict]:
        """Generate realistic dummy failure predictions"""
        import random

        predictions = []

        for metrics in file_metrics:
            seed = hash(metrics.get('file_path', '')) % 2**32
            random.seed(seed)

            # Calculate probability based on metrics characteristics
            churn = metrics.get('churn_rate', random.random())
            complexity = metrics.get('cyclomatic_complexity', random.randint(5, 30))
            bus_factor = metrics.get('bus_factor', random.randint(1, 5))
            
            # Heuristic calculation
            prob = (churn * 0.3) + (min(complexity / 30, 0.3)) + \
                   (0.2 if bus_factor == 1 else 0.05)
            prob = min(prob, 1.0)

            predictions.append({
                'file_path': metrics.get('file_path', 'unknown'),
                'failure_probability': prob,
                'risk_factors': self._identify_risk_factors(metrics),
                'recommendation': self._get_recommendation(prob)
            })

        predictions.sort(key=lambda x: x['failure_probability'], reverse=True)
        return predictions

    def _identify_risk_factors(self, metrics: Dict) -> List[str]:
        """Identify risk factors"""
        factors = []
        
        if metrics.get('churn_rate', 0) > 0.5:
            factors.append('High code churn')
        if metrics.get('cyclomatic_complexity', 0) > 20:
            factors.append('High cyclomatic complexity')
        if metrics.get('bus_factor', 0) == 1:
            factors.append('Single point of failure')
        if metrics.get('commit_frequency', 0) > 5:
            factors.append('Unstable (frequent commits)')
        
        return factors

    def _get_recommendation(self, prob: float) -> str:
        """Get recommendation"""
        if prob >= 0.7:
            return 'CRITICAL: Prioritize refactoring and testing immediately'
        elif prob >= 0.5:
            return 'HIGH: Schedule refactoring and increase test coverage'
        elif prob >= 0.3:
            return 'MEDIUM: Plan improvements and document edge cases'
        else:
            return 'LOW: Monitor and maintain current quality standards'
