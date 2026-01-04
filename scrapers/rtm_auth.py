#!/usr/bin/env python3
"""
RTM Authentication Helper
Run this script to authenticate with Remember The Milk API
"""
import os
import sys
from pathlib import Path

try:
    from rtmilk import AuthorizationSession, CreateClient
except ImportError:
    print("Error: rtmilk library not installed")
    sys.exit(1)


def authenticate():
    """Authenticate with RTM and save token"""
    api_key = os.getenv('RTM_API_KEY')
    api_secret = os.getenv('RTM_API_SECRET')
    
    if not api_key or not api_secret:
        print("Error: RTM_API_KEY and RTM_API_SECRET environment variables required")
        sys.exit(1)
    
    token_file = Path("/app/data/.rtm_token")
    
    # Check if already authenticated
    if token_file.exists():
        print("Checking existing token...")
        with open(token_file, 'r') as f:
            token = f.read().strip()
        
        try:
            client = CreateClient(
                clientId=api_key,
                clientSecret=api_secret,
                token=token
            )
            client.rtm.auth.checkToken()
            print("✓ Token is still valid!")
            return True
        except Exception as e:
            print(f"⚠ Saved token expired: {e}")
            print("Getting new token...\n")
    
    # Start new authentication
    print("="*60)
    print("  RTM Authentication")
    print("="*60)
    
    auth_session = AuthorizationSession(
        apiKey=api_key,
        sharedSecret=api_secret,
        perms='read'
    )
    
    print(f"\n1. Visit this URL in your browser:")
    print(f"   {auth_session.url}")
    print(f"\n2. Click 'OK, I'll authorize it' and then 'Done'")
    print(f"\n3. Press Enter here when done...")
    
    input()
    
    # Complete authorization
    print("\nCompleting authorization...")
    try:
        token = auth_session.Done()
        
        # Save token
        token_file.parent.mkdir(parents=True, exist_ok=True)
        with open(token_file, 'w') as f:
            f.write(token)
        
        print(f"✓ Token saved to {token_file}")
        print("✓ Authentication successful!")
        print(f"✓ Token: {token[:20]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = authenticate()
    sys.exit(0 if success else 1)
