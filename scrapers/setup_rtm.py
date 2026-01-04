"""
RTM Setup Script - First time authentication
Run this once to authenticate with Remember The Milk
"""
import os
from dotenv import load_dotenv
from rtm_scraper import RTMScraper

# Load environment variables
load_dotenv()

def setup_rtm():
    """Setup RTM authentication"""
    print("\n" + "="*60)
    print("   Remember The Milk - First Time Setup")
    print("="*60)
    
    api_key = os.getenv('RTM_API_KEY')
    api_secret = os.getenv('RTM_API_SECRET')
    
    if not api_key or not api_secret:
        print("\n✗ Error: RTM credentials not found!")
        print("\nPlease add your RTM credentials to .env file:")
        print("  RTM_API_KEY=your_api_key_here")
        print("  RTM_API_SECRET=your_api_secret_here")
        print("\nGet your API key from: https://www.rememberthemilk.com/services/api/")
        return False
    
    print(f"\n✓ Found RTM credentials")
    print(f"  API Key: {api_key[:10]}...")
    print(f"  API Secret: {api_secret[:10]}...")
    
    # Create scraper and authenticate
    scraper = RTMScraper(api_key=api_key, api_secret=api_secret)
    
    print("\nStarting authentication process...")
    print("-"*60)
    
    if not scraper.authenticate():
        print("\n✗ Authentication failed!")
        return False
    
    print("-"*60)
    print("\n✓ Authentication successful!")
    print("\nYou can now run the scraper to fetch your tasks.")
    print("\nCommands:")
    print("  - Run scraper once:  task scrape:rtm")
    print("  - Start scheduler:   docker-compose up scrapers")
    print("\n" + "="*60 + "\n")
    
    return True


if __name__ == "__main__":
    success = setup_rtm()
    exit(0 if success else 1)
