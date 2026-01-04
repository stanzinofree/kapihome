"""
System Test - Verifica funzionamento completo del sistema
"""
import os
import json
from pathlib import Path
from database import KapiHomeDB
from cache_manager import CacheManager


def test_database():
    """Test database initialization and operations"""
    print("\n" + "="*60)
    print("Testing Database...")
    print("="*60)
    
    try:
        db = KapiHomeDB(db_path="/app/data/kapihome_test.db")
        print("✓ Database initialized")
        
        # Test saving RTM stats
        test_stats = {
            'total_tasks': 45,
            'active_tasks': 12,
            'completed_this_week': 8,
            'completed_this_month': 23,
            'overdue_tasks': 3,
            'due_today': 2,
            'due_this_week': 5
        }
        
        db.save_rtm_stats(test_stats)
        print("✓ RTM stats saved")
        
        # Test retrieving history
        history = db.get_rtm_stats_history(days=30)
        print(f"✓ Retrieved {len(history)} historical records")
        
        # Cleanup test db
        Path("/app/data/kapihome_test.db").unlink(missing_ok=True)
        print("✓ Database test passed")
        return True
    
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_cache_manager():
    """Test cache manager"""
    print("\n" + "="*60)
    print("Testing Cache Manager...")
    print("="*60)
    
    try:
        # Create test data
        test_data = {
            "stats": {"total_tasks": 10},
            "active_tasks": [],
            "extracted_at": "2026-01-03T14:00:00Z"
        }
        
        # Write to data_tmp
        test_file = Path("/app/data_tmp/test.json")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        print("✓ Test data created in data_tmp")
        
        # Test cache manager
        manager = CacheManager()
        manager.sync_source('test')
        
        # Check if synced to data
        cache_file = Path("/app/data/test.json")
        if cache_file.exists():
            print("✓ Data synced to cache")
        else:
            print("✗ Cache sync failed")
            return False
        
        # Cleanup
        test_file.unlink(missing_ok=True)
        cache_file.unlink(missing_ok=True)
        
        print("✓ Cache manager test passed")
        return True
    
    except Exception as e:
        print(f"✗ Cache manager test failed: {e}")
        return False


def test_directory_structure():
    """Test that all required directories exist"""
    print("\n" + "="*60)
    print("Testing Directory Structure...")
    print("="*60)
    
    required_dirs = [
        "/app/data",
        "/app/data_tmp"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path} exists")
        else:
            print(f"✗ {dir_path} missing")
            all_exist = False
    
    return all_exist


def test_environment():
    """Test environment variables"""
    print("\n" + "="*60)
    print("Testing Environment Variables...")
    print("="*60)
    
    rtm_key = os.getenv('RTM_API_KEY')
    rtm_secret = os.getenv('RTM_API_SECRET')
    
    if rtm_key:
        print(f"✓ RTM_API_KEY set ({rtm_key[:10]}...)")
    else:
        print("⚠ RTM_API_KEY not set (RTM scraper will be disabled)")
    
    if rtm_secret:
        print(f"✓ RTM_API_SECRET set ({rtm_secret[:10]}...)")
    else:
        print("⚠ RTM_API_SECRET not set (RTM scraper will be disabled)")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("   KapiHome Scraper System Test")
    print("="*60)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Environment Variables", test_environment),
        ("Database", test_database),
        ("Cache Manager", test_cache_manager)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "="*60)
    print("Test Results:")
    print("="*60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(r for _, r in results)
    
    print("="*60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
