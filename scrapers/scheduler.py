"""
Main Scheduler - Orchestrates all scrapers and cache sync
Runs every 10 minutes
"""
import os
import time
import schedule
from datetime import datetime

try:
    from rtm_scraper import RTMScraper, HAS_RTM
except ImportError:
    HAS_RTM = False
    RTMScraper = None

from cache_manager import CacheManager
from database import KapiHomeDB
from file_scraper import MultiSourceImporter


class KapiHomeScheduler:
    def __init__(self):
        self.db = KapiHomeDB()
        self.cache_manager = CacheManager(db=self.db)
        self.file_importer = MultiSourceImporter(db=self.db)
        
        # RTM credentials from environment
        self.rtm_api_key = os.getenv('RTM_API_KEY')
        self.rtm_api_secret = os.getenv('RTM_API_SECRET')
        
        if not self.rtm_api_key or not self.rtm_api_secret:
            print("⚠ Warning: RTM_API_KEY or RTM_API_SECRET not set")
            print("  RTM API scraping will be disabled (file-based import still works)")
    
    def run_rtm_scraper(self):
        """Run RTM scraper"""
        if not HAS_RTM:
            print("  ⊘ RTM scraper skipped (rtmilk library not available)")
            return
        
        if not self.rtm_api_key or not self.rtm_api_secret:
            print("  ⊘ RTM scraper skipped (credentials not configured)")
            return
        
        try:
            scraper = RTMScraper(
                api_key=self.rtm_api_key,
                api_secret=self.rtm_api_secret
            )
            scraper.scrape()
        except Exception as e:
            print(f"  ✗ RTM scraper error: {e}")
    
    def run_cache_sync(self):
        """Run cache synchronization"""
        try:
            self.cache_manager.sync_all()
        except Exception as e:
            print(f"  ✗ Cache sync error: {e}")
    
    def run_file_importers(self):
        """Import data from data_tmp if files have been updated"""
        try:
            self.file_importer.import_all()
        except Exception as e:
            print(f"  ✗ File import error: {e}")
    
    def run_all_scrapers(self):
        """Run all configured scrapers"""
        print("\n" + "="*60)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Starting scheduled scrape cycle")
        print("="*60)
        
        # Run RTM API scraper (if configured)
        self.run_rtm_scraper()
        
        # Import from data_tmp (LinkedIn, GitHub, Exercism, Udemy)
        print("\n" + "-"*60)
        self.run_file_importers()
        
        # Sync cache after all scrapers complete
        print("\n" + "-"*60)
        self.run_cache_sync()
        
        print("="*60)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ Scheduled scrape cycle completed")
        print("="*60 + "\n")
    
    def run_manual_sync(self):
        """Manual sync for when user updates data_tmp manually"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Running manual cache sync...")
        self.run_cache_sync()
    
    def start(self):
        """Start the scheduler"""
        print("\n" + "="*60)
        print("   KapiHome Scraper Service")
        print("="*60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if HAS_RTM and self.rtm_api_key:
            print(f"RTM API Scraper: Enabled")
        else:
            print(f"RTM API Scraper: Disabled (will use file-based import)")
        print(f"File Importers: LinkedIn, GitHub, Exercism, Udemy, RTM")
        print(f"Schedule: Every 10 minutes")
        print(f"Cache Sync: Every 2 minutes")
        print("="*60 + "\n")
        
        # Schedule tasks
        schedule.every(10).minutes.do(self.run_all_scrapers)
        
        # Also run cache sync every 2 minutes (for manual data_tmp updates)
        schedule.every(2).minutes.do(self.run_cache_sync)
        
        # Run immediately on startup
        print("Running initial scrape cycle...")
        self.run_all_scrapers()
        
        # Main loop
        print("\n⏰ Scheduler running. Press Ctrl+C to stop.")
        print(f"Next run scheduled in 10 minutes...\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n" + "="*60)
            print("Scheduler stopped by user")
            print("="*60)


if __name__ == "__main__":
    scheduler = KapiHomeScheduler()
    scheduler.start()
