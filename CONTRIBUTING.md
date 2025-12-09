# Contributing to Source Code Risk Radar

Thank you for your interest in contributing to this project!

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- pip or conda

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/Source-Code-Risk-Radar.git
cd Source-Code-Risk-Radar

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with dev packages
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

## Project Structure

```
src/
├── analyzers/           # Core analysis modules
│   ├── git_analyzer.py
│   ├── security_analyzer.py
│   ├── complexity_analyzer.py
│   └── dependency_analyzer.py
├── ml_models/           # Machine learning components
│   └── failure_predictor.py
├── models.py            # Data models and types
├── risk_radar.py        # Main orchestrator
└── report_formatter.py  # Output formatting

tests/                   # Unit and integration tests
config/                  # Configuration files
data/                    # Sample data
main.py                  # CLI entry point
```

## Adding New Analyzers

### 1. Create Analyzer Class

```python
# src/analyzers/new_analyzer.py
from typing import List, Dict
from src.models import SomeModel

class NewAnalyzer:
    def __init__(self, config: Dict = None):
        self.config = config or {}

    def analyze(self, file_path: str) -> SomeModel:
        """Analyze a file and return results"""
        pass

    def analyze_directory(self, directory: str) -> List[SomeModel]:
        """Analyze all files in directory"""
        pass
```

### 2. Integrate into RiskRadar

```python
# src/risk_radar.py
from src.analyzers.new_analyzer import NewAnalyzer

class RiskRadar:
    def __init__(self, ...):
        self.new_analyzer = NewAnalyzer()

    def analyze(self) -> RiskReport:
        # Add to analysis pipeline
        new_results = self._analyze_new()
        # ...
```

### 3. Create Dummy Implementation

```python
class DummyNewAnalyzer:
    def analyze(self, file_path: str) -> SomeModel:
        """Generate realistic dummy results"""
        pass
```

## Code Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names

### Formatting

```bash
# Format code
black src/ main.py

# Check style
flake8 src/ main.py

# Type checking
mypy src/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_analyzers.py::test_complexity
```

### Writing Tests

```python
# tests/test_new_analyzer.py
import pytest
from src.analyzers.new_analyzer import NewAnalyzer

class TestNewAnalyzer:
    def setup_method(self):
        self.analyzer = NewAnalyzer()

    def test_analyze_simple_file(self, tmp_path):
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        # Test
        result = self.analyzer.analyze(str(test_file))
        assert result is not None
```

## Submitting Changes

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes and commit: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/my-feature`
4. Submit a pull request

## Reporting Bugs

Create an issue with:

- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python version, etc.)

## Feature Requests

Describe:

- Use case and motivation
- Proposed solution
- Alternative approaches considered

## Code Review Process

- All pull requests require review
- Must pass tests and style checks
- Meaningful commit messages required
- Discussions welcome!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Check existing issues/discussions
- Create a new discussion for questions
- Reach out to maintainers

Thank you for contributing! 🚀
