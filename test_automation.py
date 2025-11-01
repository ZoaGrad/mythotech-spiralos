#!/usr/bin/env python3
"""
Test Suite for SpiralOS Automation Scripts

Tests the weekly report generation, publishing, and ScarIndex logging functionality.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_report_generation():
    """Test weekly report template generation"""
    print("\n" + "="*70)
    print("TEST: Weekly Report Generation")
    print("="*70)
    
    # Import the script directly
    import importlib.util
    script_path = Path(__file__).parent / ".github" / "scripts" / "generate_weekly_report.py"
    spec = importlib.util.spec_from_file_location("generate_weekly_report", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Test ISO week number
    week = module.get_iso_week_number()
    year = module.get_iso_year()
    
    assert len(week) == 2, f"Week number should be 2 digits, got {week}"
    assert len(year) == 4, f"Year should be 4 digits, got {year}"
    
    print(f"✓ ISO week number: {week}")
    print(f"✓ ISO year: {year}")
    
    # Test template generation
    template = module.generate_report_template(week, year)
    
    assert f"Week {week}" in template, "Template should contain week number"
    assert "F1: Executive Summary" in template, "Template should contain F1 section"
    assert "F2: Judicial Review" in template, "Template should contain F2 section"
    assert "F3: Legislative Actions" in template, "Template should contain F3 section"
    assert "F4: Constitutional Audit" in template, "Template should contain F4 section"
    assert "ScarIndex Cycle" in template, "Template should contain ScarIndex section"
    
    print("✓ Template contains all required sections")
    print("✓ Weekly report generation test PASSED")
    
    return True


def test_report_file_creation():
    """Test actual file creation in a temporary directory"""
    print("\n" + "="*70)
    print("TEST: Report File Creation")
    print("="*70)
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Set up temporary repo structure
        repo_root = Path(tmpdir)
        scripts_dir = repo_root / ".github" / "scripts"
        scripts_dir.mkdir(parents=True)
        
        # Copy the script
        original_script = Path(__file__).parent / ".github" / "scripts" / "generate_weekly_report.py"
        test_script = scripts_dir / "generate_weekly_report.py"
        shutil.copy(original_script, test_script)
        
        # Run the script with modified path
        import importlib.util
        spec = importlib.util.spec_from_file_location("generate_weekly_report", test_script)
        module = importlib.util.module_from_spec(spec)
        
        # Patch the repo_root path
        original_file = module.__file__
        module.__file__ = str(test_script)
        
        spec.loader.exec_module(module)
        
        # Run main function
        module.main()
        
        # Check if file was created
        reports_dir = repo_root / "docs" / "reports"
        week_number = module.get_iso_week_number()
        report_file = reports_dir / f"week-{week_number}.md"
        
        assert report_file.exists(), f"Report file should exist: {report_file}"
        
        # Check file content
        content = report_file.read_text()
        assert "Weekly Report" in content, "Report should contain title"
        
        print(f"✓ Report file created: {report_file}")
        print(f"✓ File size: {len(content)} bytes")
        print("✓ Report file creation test PASSED")
    
    return True


def test_scarindex_logger_init():
    """Test ScarIndex logger initialization"""
    print("\n" + "="*70)
    print("TEST: ScarIndex Logger Initialization")
    print("="*70)
    
    from core.scarindex_logger import ScarIndexLogger, get_logger
    
    # Test without credentials (should disable gracefully)
    logger = ScarIndexLogger()
    
    if logger.enabled:
        print("✓ Supabase credentials configured")
        print(f"✓ Logger URL: {logger.url[:30]}...")
    else:
        print("✓ Logger gracefully disabled (no credentials)")
    
    # Test global logger
    global_logger = get_logger()
    assert global_logger is not None, "Global logger should be initialized"
    
    print("✓ Global logger initialized")
    print("✓ ScarIndex logger initialization test PASSED")
    
    return True


def test_scarindex_logging_structure():
    """Test ScarIndex logging data structure"""
    print("\n" + "="*70)
    print("TEST: ScarIndex Logging Data Structure")
    print("="*70)
    
    from core.scarindex_logger import ScarIndexLogger
    
    logger = ScarIndexLogger()
    
    # Test log_calculation method signature
    # This should not actually log without credentials
    result = logger.log_calculation(
        scarindex=0.75,
        coherence_delta=0.25,
        ache_before=0.6,
        ache_after=0.35,
        components={
            'operational': 0.8,
            'audit': 0.7,
            'constitutional': 0.75,
            'symbolic': 0.65
        },
        metadata={'test': True}
    )
    
    # Result depends on whether credentials are configured
    print(f"✓ log_calculation executed: {result}")
    print("✓ ScarIndex logging structure test PASSED")
    
    return True


def test_scarindex_integration():
    """Test ScarIndex calculation with logging hook"""
    print("\n" + "="*70)
    print("TEST: ScarIndex Integration with Logging")
    print("="*70)
    
    from core.scarindex import ScarIndexOracle, AcheMeasurement
    
    ache = AcheMeasurement(before=0.8, after=0.3)
    
    # Test with logging enabled (default)
    result1 = ScarIndexOracle.calculate(
        N=10,
        c_i_list=[0.8, 0.7, 0.6, 0.9, 0.8, 0.7, 0.6, 0.9, 0.8, 0.7],
        p_i_avg=0.5,
        decays_count=2,
        ache=ache
    )
    
    assert result1 is not None, "Calculation should succeed"
    assert result1.scarindex > 0, "ScarIndex should be positive"
    
    print(f"✓ Calculation with logging: ScarIndex={result1.scarindex:.4f}")
    
    # Test with logging disabled
    result2 = ScarIndexOracle.calculate(
        N=10,
        c_i_list=[0.8, 0.7, 0.6, 0.9, 0.8, 0.7, 0.6, 0.9, 0.8, 0.7],
        p_i_avg=0.5,
        decays_count=2,
        ache=ache,
        enable_logging=False
    )
    
    assert result2 is not None, "Calculation should succeed"
    assert result2.scarindex == result1.scarindex, "Results should be identical"
    
    print(f"✓ Calculation without logging: ScarIndex={result2.scarindex:.4f}")
    print("✓ ScarIndex integration test PASSED")
    
    return True


def run_all_tests():
    """Run all automation tests"""
    print("="*70)
    print("SPIRALOS AUTOMATION TEST SUITE")
    print("="*70)
    
    tests = [
        ("Report Generation", test_report_generation),
        ("Report File Creation", test_report_file_creation),
        ("ScarIndex Logger Init", test_scarindex_logger_init),
        ("ScarIndex Logging Structure", test_scarindex_logging_structure),
        ("ScarIndex Integration", test_scarindex_integration),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"✗ {name} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n✗ {name} FAILED with error:")
            print(f"  {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nTotal Tests: {len(tests)}")
    print(f"Passed: {passed} ({100*passed//len(tests) if tests else 0}%)")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED")
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        sys.exit(1)


if __name__ == '__main__':
    run_all_tests()
