"""
File-based Scraper - Imports data from data_tmp/ when files are updated
Works with manual Tampermonkey extractions
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from database import KapiHomeDB


class FileScraperBase:
    def __init__(self, source_name: str, db: Optional[KapiHomeDB] = None):
        self.source_name = source_name
        self.db = db or KapiHomeDB()
        self.data_tmp_dir = Path("/app/data_tmp")
        self.state_file = Path(f"/app/data/.{source_name}_last_import")
        
        # Track last imported file timestamp
        self.last_import_time = self._load_last_import_time()
    
    def _load_last_import_time(self) -> float:
        """Load timestamp of last imported file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return float(f.read().strip())
            except:
                return 0
        return 0
    
    def _save_last_import_time(self, timestamp: float):
        """Save timestamp of imported file"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            f.write(str(timestamp))
        self.last_import_time = timestamp
    
    def has_new_data(self) -> bool:
        """Check if there's a newer file in data_tmp"""
        source_file = self.data_tmp_dir / f"{self.source_name}.json"
        
        if not source_file.exists():
            return False
        
        file_mtime = source_file.stat().st_mtime
        return file_mtime > self.last_import_time
    
    def import_data(self) -> bool:
        """Import data from data_tmp if newer than last import"""
        source_file = self.data_tmp_dir / f"{self.source_name}.json"
        
        if not source_file.exists():
            print(f"  ⊘ {self.source_name}.json not found in data_tmp")
            return False
        
        file_mtime = source_file.stat().st_mtime
        
        # Check if file is newer
        if file_mtime <= self.last_import_time:
            print(f"  → {self.source_name}.json unchanged (last import: {self._format_time(self.last_import_time)})")
            return False
        
        try:
            # Read data
            with open(source_file, 'r') as f:
                data = json.load(f)
            
            # Save to database (implemented by subclass)
            self.save_to_database(data)
            
            # Update last import timestamp
            self._save_last_import_time(file_mtime)
            
            print(f"  ✓ Imported {self.source_name}.json (modified: {self._format_time(file_mtime)})")
            return True
        
        except json.JSONDecodeError as e:
            print(f"  ✗ Error parsing {self.source_name}.json: {e}")
            return False
        except Exception as e:
            print(f"  ✗ Error importing {self.source_name}: {e}")
            return False
    
    def save_to_database(self, data: Dict[str, Any]):
        """Save data to database - must be implemented by subclass"""
        raise NotImplementedError("Subclass must implement save_to_database()")
    
    def _format_time(self, timestamp: float) -> str:
        """Format timestamp for display"""
        if timestamp == 0:
            return "never"
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class LinkedInScraper(FileScraperBase):
    def __init__(self, db: Optional[KapiHomeDB] = None):
        super().__init__("linkedin", db)
    
    def save_to_database(self, data: Dict[str, Any]):
        """Save LinkedIn data to database"""
        stats = data.get("stats", {})
        self.db.save_linkedin_stats(stats)
        print(f"    → Saved to DB: {stats.get('followers', 0)} followers, "
              f"{stats.get('post_impressions_7d', 0)} impressions")


class GitHubScraper(FileScraperBase):
    def __init__(self, db: Optional[KapiHomeDB] = None):
        super().__init__("github", db)
    
    def save_to_database(self, data: Dict[str, Any]):
        """Save GitHub data to database"""
        stats = data.get("stats", {})
        self.db.save_github_stats(stats)
        print(f"    → Saved to DB: {stats.get('public_repos', 0)} repos, "
              f"{stats.get('total_stars', 0)} stars")


class ExercismScraper(FileScraperBase):
    def __init__(self, db: Optional[KapiHomeDB] = None):
        super().__init__("exercism", db)
    
    def save_to_database(self, data: Dict[str, Any]):
        """Save Exercism data to database"""
        stats = data.get("stats", {})
        self.db.save_exercism_stats(stats)
        print(f"    → Saved to DB: {stats.get('reputation', 0)} reputation, "
              f"{stats.get('total_solutions', 0)} solutions")


class UdemyScraper(FileScraperBase):
    def __init__(self, db: Optional[KapiHomeDB] = None):
        super().__init__("udemy", db)
    
    def save_to_database(self, data: Dict[str, Any]):
        """Save Udemy data to database"""
        student = data.get("student", {})
        self.db.save_udemy_stats(student)
        print(f"    → Saved to DB: {student.get('total_courses', 0)} courses, "
              f"{student.get('weekly_minutes_current', 0)} min/week")


class RTMScraper(FileScraperBase):
    def __init__(self, db: Optional[KapiHomeDB] = None):
        super().__init__("rtm", db)
    
    def save_to_database(self, data: Dict[str, Any]):
        """Save RTM data to database"""
        stats = data.get("stats", {})
        self.db.save_rtm_stats(stats)
        
        # Save all tasks
        all_tasks = []
        all_tasks.extend(data.get('active_tasks', []))
        all_tasks.extend(data.get('upcoming_tasks', []))
        all_tasks.extend(data.get('overdue_tasks', []))
        
        if all_tasks:
            self.db.save_rtm_tasks(all_tasks)
        
        print(f"    → Saved to DB: {stats.get('total_tasks', 0)} tasks, "
              f"{stats.get('active_tasks', 0)} active")


class WelltoryScraper(FileScraperBase):
    def __init__(self, db: Optional[KapiHomeDB] = None):
        super().__init__("welltory", db)
    
    def save_to_database(self, data: Dict[str, Any]):
        """Save Welltory data to database"""
        current = data.get("current", {})
        self.db.save_welltory_stats(current)
        
        stress = current.get('stress', 0)
        energy = current.get('energy', 0)
        hrv = current.get('hrv', 0)
        
        print(f"    → Saved to DB: Stress={stress}, Energy={energy}, HRV={hrv}")


class MultiSourceImporter:
    """Import data from multiple sources"""
    def __init__(self, db: Optional[KapiHomeDB] = None):
        self.db = db or KapiHomeDB()
        
        self.scrapers = {
            'linkedin': LinkedInScraper(db),
            'github': GitHubScraper(db),
            'exercism': ExercismScraper(db),
            'udemy': UdemyScraper(db),
            'rtm': RTMScraper(db),
            'welltory': WelltoryScraper(db)
        }
    
    def import_all(self) -> Dict[str, bool]:
        """Import all sources that have new data"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Checking for new data in data_tmp...")
        
        results = {}
        updated_count = 0
        
        for name, scraper in self.scrapers.items():
            if scraper.has_new_data():
                success = scraper.import_data()
                results[name] = success
                if success:
                    updated_count += 1
            else:
                results[name] = False
        
        if updated_count > 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ Imported {updated_count} updated source(s)")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] → No new data to import")
        
        return results
    
    def force_import_all(self) -> Dict[str, bool]:
        """Force import all sources regardless of timestamp"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Force importing all sources...")
        
        results = {}
        for name, scraper in self.scrapers.items():
            # Temporarily reset last import time
            old_time = scraper.last_import_time
            scraper.last_import_time = 0
            success = scraper.import_data()
            if not success:
                scraper.last_import_time = old_time  # Restore if failed
            results[name] = success
        
        return results
    
    def get_import_status(self) -> Dict[str, Any]:
        """Get status of all imports"""
        status = {}
        for name, scraper in self.scrapers.items():
            source_file = Path(f"/app/data_tmp/{name}.json")
            status[name] = {
                'file_exists': source_file.exists(),
                'last_import': scraper._format_time(scraper.last_import_time),
                'has_new_data': scraper.has_new_data()
            }
        return status


if __name__ == "__main__":
    # Test importer
    print("\n" + "="*60)
    print("   File-based Scraper Test")
    print("="*60)
    
    importer = MultiSourceImporter()
    
    # Show status
    print("\nCurrent Status:")
    print("-"*60)
    status = importer.get_import_status()
    for source, info in status.items():
        exists = "✓" if info['file_exists'] else "✗"
        new = "NEW" if info['has_new_data'] else "ok"
        print(f"{exists} {source:12} | Last: {info['last_import']:20} | {new}")
    
    # Import new data
    print("\n" + "-"*60)
    results = importer.import_all()
    
    print("\n" + "="*60)
    print("Test completed")
    print("="*60 + "\n")
