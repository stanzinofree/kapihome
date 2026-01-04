"""
Cache Manager - Syncs data from data_tmp/ to data/ and database
Monitors data_tmp/ for changes and automatically updates the cache
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from database import KapiHomeDB


class CacheManager:
    def __init__(self, 
                 data_tmp_dir: str = "/app/data_tmp",
                 data_dir: str = "/app/data",
                 db: Optional[KapiHomeDB] = None):
        self.data_tmp_dir = Path(data_tmp_dir)
        self.data_dir = Path(data_dir)
        self.db = db or KapiHomeDB()
        
        # Ensure directories exist
        self.data_tmp_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Track last modification times
        self.last_modified = {}
    
    def sync_all(self):
        """Sync all JSON files from data_tmp to data and update database"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Starting cache sync...")
        
        sources = ['rtm', 'linkedin', 'github', 'exercism', 'udemy']
        
        for source in sources:
            self.sync_source(source)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ Cache sync completed")
    
    def sync_source(self, source: str):
        """Sync a specific data source"""
        tmp_file = self.data_tmp_dir / f"{source}.json"
        cache_file = self.data_dir / f"{source}.json"
        
        # Check if temp file exists
        if not tmp_file.exists():
            print(f"  ⊘ {source}.json not found in data_tmp, skipping...")
            return
        
        # Check if file was modified
        current_mtime = tmp_file.stat().st_mtime
        last_mtime = self.last_modified.get(source, 0)
        
        if current_mtime <= last_mtime:
            # File hasn't changed, skip
            return
        
        try:
            # Read data from temp
            with open(tmp_file, 'r') as f:
                data = json.load(f)
            
            # Copy to cache
            shutil.copy2(tmp_file, cache_file)
            print(f"  ✓ Synced {source}.json to cache")
            
            # Save to database for historical tracking
            self.save_to_database(source, data)
            
            # Update last modified time
            self.last_modified[source] = current_mtime
            
        except json.JSONDecodeError as e:
            print(f"  ✗ Error parsing {source}.json: {e}")
        except Exception as e:
            print(f"  ✗ Error syncing {source}: {e}")
    
    def save_to_database(self, source: str, data: Dict[str, Any]):
        """Save data snapshot to database for historical tracking"""
        try:
            if source == 'rtm':
                stats = data.get('stats', {})
                self.db.save_rtm_stats(stats)
                
                # Save all tasks
                all_tasks = []
                all_tasks.extend(data.get('active_tasks', []))
                all_tasks.extend(data.get('upcoming_tasks', []))
                all_tasks.extend(data.get('overdue_tasks', []))
                
                if all_tasks:
                    self.db.save_rtm_tasks(all_tasks)
                
                print(f"    → Saved RTM stats to database ({stats.get('total_tasks', 0)} tasks)")
            
            elif source == 'linkedin':
                stats = data.get('stats', {})
                self.db.save_linkedin_stats(stats)
                print(f"    → Saved LinkedIn stats to database ({stats.get('followers', 0)} followers)")
            
            elif source == 'github':
                stats = data.get('stats', {})
                self.db.save_github_stats(stats)
                print(f"    → Saved GitHub stats to database ({stats.get('public_repos', 0)} repos)")
            
            elif source == 'exercism':
                stats = data.get('stats', {})
                self.db.save_exercism_stats(stats)
                print(f"    → Saved Exercism stats to database ({stats.get('reputation', 0)} reputation)")
            
            elif source == 'udemy':
                student = data.get('student', {})
                self.db.save_udemy_stats(student)
                print(f"    → Saved Udemy stats to database ({student.get('total_courses', 0)} courses)")
        
        except Exception as e:
            print(f"    ✗ Error saving {source} to database: {e}")
    
    def get_file_age(self, source: str) -> Optional[str]:
        """Get age of cached file"""
        cache_file = self.data_dir / f"{source}.json"
        
        if not cache_file.exists():
            return None
        
        mtime = cache_file.stat().st_mtime
        age_seconds = datetime.now().timestamp() - mtime
        
        if age_seconds < 60:
            return f"{int(age_seconds)}s ago"
        elif age_seconds < 3600:
            return f"{int(age_seconds / 60)}m ago"
        elif age_seconds < 86400:
            return f"{int(age_seconds / 3600)}h ago"
        else:
            return f"{int(age_seconds / 86400)}d ago"
    
    def force_sync(self, source: str):
        """Force sync a specific source regardless of modification time"""
        tmp_file = self.data_tmp_dir / f"{source}.json"
        cache_file = self.data_dir / f"{source}.json"
        
        if not tmp_file.exists():
            print(f"  ✗ {source}.json not found in data_tmp")
            return False
        
        try:
            with open(tmp_file, 'r') as f:
                data = json.load(f)
            
            shutil.copy2(tmp_file, cache_file)
            self.save_to_database(source, data)
            self.last_modified[source] = tmp_file.stat().st_mtime
            
            print(f"  ✓ Force synced {source}.json")
            return True
        
        except Exception as e:
            print(f"  ✗ Error force syncing {source}: {e}")
            return False
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get status of all cached files"""
        status = {}
        sources = ['rtm', 'linkedin', 'github', 'exercism', 'udemy']
        
        for source in sources:
            cache_file = self.data_dir / f"{source}.json"
            tmp_file = self.data_tmp_dir / f"{source}.json"
            
            status[source] = {
                'cached': cache_file.exists(),
                'cached_age': self.get_file_age(source),
                'tmp_available': tmp_file.exists(),
                'last_sync': self.last_modified.get(source, 0)
            }
        
        return status


if __name__ == "__main__":
    # Test cache manager
    manager = CacheManager()
    print("Cache Manager Test")
    print("=" * 50)
    
    # Show current status
    status = manager.get_cache_status()
    for source, info in status.items():
        print(f"{source}: cached={info['cached']}, age={info['cached_age']}, tmp={info['tmp_available']}")
    
    print("\nRunning sync...")
    manager.sync_all()
    
    print("\nCache status after sync:")
    status = manager.get_cache_status()
    for source, info in status.items():
        print(f"{source}: cached={info['cached']}, age={info['cached_age']}")
