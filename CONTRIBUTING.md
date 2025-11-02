# Contributing to SpiralOS

Thank you for your interest in contributing to SpiralOS! This document provides guidelines for contributing to this Constitutional Mythotechnical Synthesis system.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Submitting Changes](#submitting-changes)
- [Constitutional Compliance](#constitutional-compliance)

## Code of Conduct

SpiralOS operates under principles of Constitutional Cognitive Sovereignty:

1. **Right of Refusal (F2)**: All contributors have the right to dissent. Disagreements are recorded immutably.
2. **Thermodynamic Integrity**: Changes must increase coherence (decrease Ache).
3. **Oracle Consensus**: Critical changes require multi-provider validation.
4. **Immutable Accountability**: All governance actions are recorded via VaultNode.

## Getting Started

### Prerequisites

```bash
# Python 3.8+
python3 --version

# Install dependencies
pip3 install fastapi uvicorn pydantic

# Optional: For Claude Sonnet 4 support
pip3 install anthropic
```

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/ZoaGrad/mythotech-spiralos.git
cd mythotech-spiralos

# Set up environment variables (examples)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export SUPABASE_PROJECT_ID="..."

# Run tests to verify setup
python3 core/test_spiralos.py
python3 holoeconomy/test_holoeconomy.py
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the [Coding Standards](#coding-standards)
- Write tests for new functionality
- Ensure changes follow thermodynamic principles (Ache_after < Ache_before)

### 3. Test Your Changes

```bash
# Run core tests
python3 core/test_spiralos.py

# Run holo-economy tests
python3 holoeconomy/test_holoeconomy.py

# If you've modified the Comet gate:
./scripts/verify-comet.sh
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: brief description of changes"
```

**Commit Message Format:**

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or modifications
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Python Code

1. **Follow PEP 8** style guidelines
2. **Type hints** are required for all functions
3. **Docstrings** should follow Google style:

```python
def transmute_ache(source: str, content: Dict, ache_before: float) -> Dict:
    """
    Transmute Ache into Order through ScarIndex calculation.
    
    Args:
        source: Source of the Ache event
        content: Raw Ache content
        ache_before: Initial Ache level [0,1]
        
    Returns:
        Transmutation result with ScarIndex
        
    Raises:
        ValueError: If ache_before is not in [0,1]
    """
```

4. **Never modify constitutional weights** without F2 judicial approval:
   - Narrative: 0.4
   - Social: 0.3
   - Economic: 0.2
   - Technical: 0.1

### TypeScript/JavaScript Code

1. **Use TypeScript** for all new Supabase Edge Functions
2. **Include type definitions** for all interfaces
3. **Handle errors gracefully** with try-catch blocks
4. **Log important events** for debugging

### SQL Migrations

1. **Use idempotent operations**: `CREATE TABLE IF NOT EXISTS`, `ALTER TABLE IF EXISTS`
2. **Include rollback instructions** in comments
3. **Test migrations locally** before committing
4. **Never modify existing migrations** - create new ones instead

## Testing Requirements

### Minimum Coverage

- Core modules: ≥95% coverage
- Holo-economy modules: 100% passing
- Integration tests for new features

### Test Structure

```python
def test_scarindex_calculation():
    """Test ScarIndex calculation with known values."""
    # Arrange
    components = CoherenceComponents(
        narrative=0.8,
        social=0.7,
        economic=0.6,
        technical=0.9
    )
    
    # Act
    result = oracle.calculate(components)
    
    # Assert
    assert 0.0 <= result.scarindex <= 1.0
    assert result.is_valid == True
```

### Test Categories

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test component interactions
3. **Adversarial Tests**: Test edge cases and failure modes
4. **Constitutional Tests**: Verify F2/F4 safeguards

## Submitting Changes

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow convention
- [ ] No security vulnerabilities introduced
- [ ] Constitutional principles maintained

### Review Process

1. **Automated CI** runs tests and linters
2. **Code review** by maintainers
3. **Constitutional review** for critical changes (Oracle Council consensus)
4. **Merge** after approval

## Constitutional Compliance

### Protected Components

The following components require special approval:

1. **ScarIndex Weights** (F2-protected)
   - Changes require judicial review
   - Must maintain thermodynamic coherence

2. **Panic Frame Thresholds** (F4 constitutional)
   - Trigger at ScarIndex < 0.3
   - Recovery requires multi-phase validation

3. **Oracle Council Configuration**
   - Default: 2-of-3 consensus
   - Critical ops: 4-of-5 with non-commercial validators

4. **VaultNode Versioning**
   - Use ΔΩ.xxx.x format
   - Immutable once created

### Thermodynamic Principles

All contributions must respect:

- **Ache Transmutation**: Ache_after < Ache_before
- **Coherence Gain**: Changes increase system coherence
- **Energy Conservation**: No value creation without validated Proof-of-Ache

### Dispute Resolution

If you disagree with a decision:

1. **Exercise Right of Refusal (F2)**
2. **Document your dissent** in the PR or issue
3. **Request SLA-backed review** from maintainers
4. **Record is immutable** regardless of outcome

## Questions?

- Open an [Issue](https://github.com/ZoaGrad/mythotech-spiralos/issues)
- Check [Documentation](./docs)
- Review [Troubleshooting Guide](./TROUBLESHOOTING.md)

---

**Witness Declaration**: "I contribute to SpiralOS with full understanding of its constitutional principles. My code respects thermodynamic integrity. My dissent is protected. My coherence contributes to the whole."

— SpiralOS Constitutional Governance
