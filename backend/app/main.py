from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(title="KapiHome API", version="0.2.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "KapiHome API - Zen Capibara Style"}

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "kapihome-backend"}
    )

@app.get("/api/linkedin", response_class=HTMLResponse)
async def get_linkedin():
    """
    Returns LinkedIn profile data as HTML component for HTMX
    """
    data_path = Path("/app/data/linkedin.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        profile = data.get("profile", {})
        stats = data.get("stats", {})
        last_updated = data.get("last_updated", "")
        
        # Parse last updated
        try:
            updated_dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            updated_str = updated_dt.strftime("%d %b %Y, %H:%M")
        except:
            updated_str = "Unknown"
        
        # Build HTML response (without name, only job title)
        html = f"""
        <div class="linkedin-header">
            <div class="linkedin-info">
                <p class="title">{profile.get('title', '')}</p>
            </div>
        </div>
        
        <div class="linkedin-bio">
            {profile.get('headline', '')}
        </div>
        
        <div class="linkedin-stats-grid">
            <div class="stat-card">
                <div class="stat-icon">👁️</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('profile_views_7d', 0)}</span>
                    <span class="stat-label">Profile Views</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: 75%;"></div>
                    </div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('post_impressions_7d', 0)}</span>
                    <span class="stat-label">Post Impressions</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: 85%;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="linkedin-badge">
            💼 {profile.get('current_company', '')}
        </div>
        
        <div class="linkedin-actions">
            <a href="https://www.linkedin.com/in/stanzinofree/" target="_blank" class="btn-linkedin">
                View Full Profile →
            </a>
        </div>
        
        <div class="linkedin-last-update">
            🔄 Last sync: {updated_str}
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p>LinkedIn data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p>Error loading LinkedIn data: {str(e)}</p>",
            status_code=500
        )

@app.get("/api/profile", response_class=HTMLResponse)
async def get_profile():
    """
    Returns profile card with photo and bio data as HTML component for HTMX
    """
    data_path = Path("/app/data/linkedin.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        profile = data.get("profile", {})
        
        # Build profile card HTML
        html = f"""
        <img src="{profile.get('avatar_url', '/static/images/avatar.jpg')}" 
             alt="{profile.get('name', 'Alessandro Middei')}" 
             class="profile-avatar" />
        
        <h2 class="profile-name">{profile.get('name', 'Alessandro Middei')}</h2>
        
        <p class="profile-bio">{profile.get('headline', '')}</p>
        
        <div class="profile-location">
            <span>📍</span>
            <span>{profile.get('location', '')}</span>
        </div>
        
        <div class="profile-connections">
            <span>🤝</span>
            <span>{profile.get('connections', '500+')} connections</span>
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p>Profile data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p>Error loading profile data: {str(e)}</p>",
            status_code=500
        )
