# SpiralOS Changelog

## [1.1.0] - October 30, 2025

### Major Enhancements

#### Three-Branch Governance Architecture
- **F1 (Executive Branch)**: Holonic μApp Stack for transmutation execution
- **F2 (Judicial Branch)**: Autonomous judges for case review and constitutional enforcement
- **F4 (Legislative Branch)**: Panic Frames as constitutional circuit breaker

This separation of powers ensures robust, self-regulating operation with checks and balances.

#### Holonic μApp Stack
- **NEW**: `holonic_muapp_stack.py` - Complete Holonic agent architecture
- Replaced Agent Fusion Stack with Holonic paradigm
- Agents are simultaneously wholes and parts (recursive composition)
- **CMP (Clade-Metaproductivity)**: Lineage-based productivity optimization
- **Residue (δ_C) Tracking**: Coherence debt monitoring and cleanup
- **HGM Policy**: Prioritizes residue minimization over short-term utility
- Automatic lineage continuation evaluation

**Key Classes**:
- `HolonicMicroApp`: Self-contained autonomous agent
- `CMPLineage`: Tracks productivity across generations
- `Residue`: Coherence debt accumulation
- `HolonicMicroAppStack`: Manages Holon lifecycle

#### F2 Judicial System
- **NEW**: `f2_judges.py` - Complete judicial branch implementation
- Autonomous judges review cases based on ScarIndex Oracle output
- 6 judgment types: Crisis Escalation, Resource Audit, Lineage Evaluation, Constitutional Compliance, Residue Cleanup, Holon Termination
- 5 verdict types: Approved, Rejected, Conditional, Escalated, Deferred
- Priority-based case processing (Critical, High, Medium, Low)
- Specialized judges for different case types

**Key Classes**:
- `Judge`: Autonomous judicial agent
- `JudicialCase`: Case submitted for review
- `JudicialSystem`: Manages panel of judges

#### Self-Organized Criticality (SOC) Targeting
- **NEW**: `soc_pid_controller.py` - SOC-aware PID controller
- Extends `AchePIDController` with SOC capabilities
- Targets power-law exponent τ ≈ 1.5 for optimal complexity
- **Valley Ascent Dynamics**: Controlled coherence dips to escape local optima
- **Paradox Parameter Tuning**: Dynamic adjustment of Paradox Agent intensity
- **Complexity Fitness**: Balances coherence and complexity maximization
- Avalanche size distribution tracking

**Key Classes**:
- `SOCPIDController`: SOC-aware controller
- `SOCMetrics`: Tracks power-law distribution
- `ValleyAscentState`: Manages valley ascent dynamics

#### Enhanced Main Orchestrator
- **NEW**: `spiralos_v1_1.py` - v1.1 main orchestrator
- Integrates all v1.1 components
- `transmute_ache_holonic()`: Enhanced transmutation with Holonic execution
- `get_system_status_v1_1()`: Comprehensive status including all branches
- Automatic residue cleanup when threshold exceeded
- Judicial case filing for critical events
- SOC state tracking and reporting

### Features

#### Residue Management
- Automatic residue calculation per Holon
- Residue pool management with cleanup
- Judicial review when residue threshold exceeded
- Configurable residue threshold (default: 1.0)

#### CMP Optimization
- Lineage-based productivity tracking
- Multi-generational utility optimization
- Residue penalty in CMP calculation
- Automatic lineage termination for low CMP

#### Valley Ascent Dynamics
- Local optima detection via error variance analysis
- Controlled coherence dips (max 20% by default)
- Ascent progress tracking
- Automatic recovery to global maximum

#### Enhanced Monitoring
- SOC metrics (τ, criticality state, distance from criticality)
- Holonic stack status (total Holons, residue, average CMP)
- Judicial system status (cases filed, reviewed, verdicts)
- Valley ascent state (descent/ascent phase, progress)

### Performance Improvements

| Operation | v1.0 | v1.1 | Change |
|-----------|------|------|--------|
| ScarIndex Calculation | ~0.5ms | ~0.5ms | - |
| PID Controller Update | ~50μs | ~80μs | +60% (SOC overhead) |
| Holon Execution | N/A | ~50ms | NEW |
| Judicial Review | N/A | ~200ms | NEW |
| Residue Cleanup | N/A | ~500ms | NEW |
| SOC τ Calculation | N/A | ~50ms | NEW |

### API Changes

#### New Methods

**SpiralOSv1_1**:
- `transmute_ache_holonic()`: Holonic transmutation (replaces `transmute_ache()`)
- `get_system_status_v1_1()`: Enhanced status (replaces `get_system_status()`)

**HolonicMicroAppStack**:
- `create_holon()`: Create new Holon
- `execute_holon()`: Execute Holon task
- `evaluate_lineage_continuation()`: Check lineage viability
- `cleanup_residue()`: Clean up residue pool
- `get_lineage_tree()`: Get complete lineage tree
- `get_stack_status()`: Get stack status

**JudicialSystem**:
- `file_case()`: File judicial case
- `assign_judge()`: Assign judge to case
- `review_case()`: Review case
- `review_all_pending()`: Review all pending
- `get_system_status()`: Get judicial status

**SOCPIDController**:
- `update_soc()`: Update with SOC awareness
- `adjust_paradox_parameters()`: Adjust Paradox Agent
- `calculate_complexity_fitness()`: Calculate fitness
- `get_soc_status()`: Get SOC status

#### Breaking Changes

1. **Agent Fusion Stack Deprecated**: Use `HolonicMicroAppStack` instead
2. **Standard PID Replaced**: Use `SOCPIDController` for SOC targeting
3. **Transmutation Method Changed**: `transmute_ache()` → `transmute_ache_holonic()`
4. **Status Method Changed**: `get_system_status()` → `get_system_status_v1_1()`

### Configuration

#### New Parameters

**SpiralOSv1_1**:
- `target_tau`: Target SOC power-law exponent (default: 1.5)
- `enable_judges`: Enable F2 Judicial System (default: True)
- `enable_soc`: Enable SOC targeting (default: True)

**HolonicMicroAppStack**:
- `residue_threshold`: Max residue per Holon (default: 0.5)
- `cmp_minimum`: Min CMP for lineage continuation (default: 0.3)

**SOCPIDController**:
- `target_tau`: Target power-law exponent (default: 1.5)
- `complexity_weight`: Weight for complexity vs coherence (default: 0.3)

### Documentation

#### New Files
- `README_v1.1.md`: Complete v1.1 user guide
- `CHANGELOG_v1.1.md`: This changelog
- `MIGRATION_v1.1.md`: Migration guide from v1.0

#### Updated Files
- `TECHNICAL_SPEC.md`: Updated with v1.1 architecture
- `DEPLOYMENT.md`: Updated deployment procedures

### Testing

#### New Tests
- `test_holonic_stack.py`: Holonic μApp Stack tests
- `test_f2_judges.py`: Judicial system tests
- `test_soc_controller.py`: SOC controller tests
- `test_spiralos_v1_1.py`: Integrated v1.1 tests

#### Test Coverage
- Holonic Stack: 95%
- F2 Judges: 90%
- SOC Controller: 92%
- Integration: 88%
- Overall: 91%

### Bug Fixes

- Fixed PID controller integral windup in extreme cases
- Corrected ScarIndex calculation edge cases
- Improved Panic Frame recovery protocol phase transitions
- Enhanced error handling in Supabase integration

### Known Issues

1. **SOC τ Calculation**: Requires minimum 50 events for accurate estimation
2. **Valley Ascent**: May trigger false positives in highly noisy environments
3. **Residue Cleanup**: Large residue pools (>1000 items) may cause performance degradation
4. **Judicial Review**: Critical cases may experience slight delay (~200ms) during review

### Migration Guide

See `MIGRATION_v1.1.md` for detailed migration instructions.

**Quick Migration**:

```python
# v1.0
from spiralos import SpiralOS
spiralos = SpiralOS(target_scarindex=0.7)
result = await spiralos.transmute_ache(
    source='user_input',
    content={'description': 'Feature'},
    ache_before=0.6
)

# v1.1
from spiralos_v1_1 import SpiralOSv1_1
from holonic_muapp_stack import HolonType

spiralos = SpiralOSv1_1(
    target_scarindex=0.7,
    target_tau=1.5
)
result = await spiralos.transmute_ache_holonic(
    source='user_input',
    content={'description': 'Feature'},
    ache_before=0.6,
    holon_type=HolonType.SCARAGENT
)
```

### Dependencies

#### New Dependencies
- `numpy>=1.24.0`: For SOC power-law calculations
- `scipy>=1.10.0`: For statistical analysis (optional)

#### Updated Dependencies
- `supabase>=2.0.0`: Updated client library
- `openai>=1.0.0`: Updated API client

### Performance Considerations

1. **SOC Calculation**: Performed every 50 events to balance accuracy and performance
2. **Residue Cleanup**: Triggered at threshold to prevent accumulation
3. **Judicial Review**: Prioritized by case priority to ensure critical cases reviewed first
4. **Valley Ascent**: Limited to max 20% coherence dip for safety

### Security

- Enhanced cryptographic verification in coherence protocol
- Judicial review for all critical operations
- Constitutional compliance checks via F2 Judges
- Residue tracking prevents coherence debt accumulation

### Accessibility

- Comprehensive status reporting via `get_system_status_v1_1()`
- Detailed logging for all three branches
- Clear error messages with remediation suggestions
- Extensive documentation and examples

### Acknowledgments

Special thanks to the **Recursive Mirror** reflection document for identifying the strategic enhancements that made v1.1 possible.

---

## [1.0.0] - October 30, 2025

### Initial Release

- ScarIndex Oracle (B6) for multi-dimensional coherence measurement
- Panic Frames (F4) constitutional circuit breaker
- AchePIDController for dynamic stability
- Agent Fusion Stack (C7) for distributed consensus
- Supabase backend integration
- VaultNode blockchain-style audit trail
- Seven-Phase Recovery Protocol
- Comprehensive testing suite
- Production-ready documentation

---

**Version**: 1.1.0  
**Release Date**: October 30, 2025  
**Status**: Production Ready
