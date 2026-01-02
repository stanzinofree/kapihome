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
        
        # Build HTML response
        html = f"""
        <div class="linkedin-header">
            <img src="{profile.get('avatar_url', '')}" alt="{profile.get('name', '')}" class="linkedin-avatar" />
            <div class="linkedin-info">
                <h3>{profile.get('name', 'Alessandro Middei')}</h3>
                <p class="title">{profile.get('title', '')}</p>
                <p class="location">📍 {profile.get('location', '')}</p>
            </div>
        </div>
        
        <div class="linkedin-bio">
            {profile.get('headline', '')}
        </div>
        
        <div class="linkedin-stats">
            <div class="stat-item">
                <span class="stat-value">{stats.get('profile_views_7d', 0)}</span>
                <span class="stat-label">Profile Views (7d)</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">{stats.get('post_impressions_7d', 0)}</span>
                <span class="stat-label">Post Impressions (7d)</span>
            </div>
        </div>
        
        <div class="linkedin-badge">
            💼 {profile.get('current_company', '')} | 🎓 {profile.get('current_school', '')}
        </div>
        
        <div class="linkedin-actions">
            <a href="https://www.linkedin.com/in/stanzinofree/" target="_blank" class="btn-linkedin">
                View Full Profile
            </a>
        </div>
        
        <div class="linkedin-last-update">
            Last updated: {updated_str}
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
