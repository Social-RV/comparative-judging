#!/usr/bin/env python3
"""
Quick test script to verify the Node.js wrapper is working correctly.

This script creates minimal test data and runs the comparative judging system
to ensure everything is properly connected.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from comparative_judging import (
    SessionFile,
    Target,
    perform_comparative_judging,
    ComparativeJudgingError,
)


def test_wrapper():
    """Test that the Node.js wrapper is working."""
    print("🧪 Testing Node.js wrapper...")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Please set it in your .env file or environment")
        return False
    
    print("✅ OpenAI API key found")
    
    # Create minimal test data (using placeholder URLs - won't actually be downloaded in this test)
    print("\n📝 Creating test data...")
    
    session_files = [
        SessionFile(
            url="https://example.com/session1.jpg",
            mime_type="image/jpeg",
            file_name="session1.jpg"
        )
    ]
    
    current_target = Target(
        id="target-1",
        description="A red apple on a white plate",
        url="https://example.com/target1.jpg"
    )
    
    historical_targets = [
        Target(id=f"decoy-{i}", description=f"Decoy target {i}", url=f"https://example.com/decoy{i}.jpg")
        for i in range(1, 10)
    ]
    
    print(f"   Session files: {len(session_files)}")
    print(f"   Targets: 1 correct + {len(historical_targets)} decoys")
    
    # Try to run comparative judging
    print("\n🧠 Running comparative judging...")
    print("   (This will make real API calls to OpenAI)")
    
    try:
        result = perform_comparative_judging(
            session_files=session_files,
            current_target=current_target,
            historical_targets=historical_targets
        )
        
        print("\n✅ Comparative judging completed successfully!")
        print(f"\n📊 Results:")
        print(f"   Correct target rank: {result.correct_target_rank}")
        print(f"   Total targets ranked: {result.total_targets_ranked}")
        print(f"   Top 3 matches:")
        for match in result.top_matches[:3]:
            marker = "🎯" if match.target_id == current_target.id else "  "
            print(f"   {marker} Rank {match.rank}: {match.target_id}")
        
        return True
        
    except ComparativeJudgingError as e:
        print(f"\n❌ Comparative judging failed: {e}")
        print(f"   Error code: {e.code}")
        if e.details:
            print(f"   Details: {e.details}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Comparative Judging Wrapper Test")
    print("=" * 60)
    print()
    
    success = test_wrapper()
    
    print()
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
        print("\nYou can now use the comparative judging system.")
        print("Try running: jupyter notebook notebooks/03_run_judging.ipynb")
    else:
        print("❌ Tests failed")
        print("\nTroubleshooting:")
        print("1. Make sure Node.js dependencies are installed:")
        print("   cd nodejs_wrapper && npm install")
        print("2. Make sure OPENAI_API_KEY is set in your .env file")
        print("3. Check that tsx is available: npx tsx --version")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

