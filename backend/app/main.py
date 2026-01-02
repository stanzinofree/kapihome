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
        recent_posts = data.get("recent_posts", [])
        recent_shares = data.get("recent_shares", [])
        last_updated = data.get("last_updated", "")
        
        # Parse last updated
        try:
            updated_dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            updated_str = updated_dt.strftime("%d %b %Y, %H:%M")
        except:
            updated_str = "Unknown"
        
        # Build posts HTML
        posts_html = ""
        for post in recent_posts[:2]:
            posts_html += f"""
            <div class="linkedin-post">
                <h4 class="post-title">{post.get('title', '')}</h4>
                <p class="post-excerpt">{post.get('excerpt', '')}</p>
                <span class="post-date">📅 {post.get('date', '')}</span>
            </div>
            """
        
        # Build shares HTML
        shares_html = ""
        for share in recent_shares[:2]:
            shares_html += f"""
            <div class="linkedin-share">
                <p class="share-author">🔄 {share.get('author', '')}</p>
                <p class="share-title">{share.get('title', '')}</p>
                <span class="share-date">📅 {share.get('date', '')}</span>
            </div>
            """
        
        # Build HTML response
        html = f"""
        <div class="linkedin-stats-grid">
            <div class="stat-card">
                <div class="stat-icon">👁️</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('profile_views_7d', 0)}</span>
                    <span class="stat-label">Profile Views (7d)</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {min(stats.get('profile_views_7d', 0) / 200 * 100, 100)}%;"></div>
                    </div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('profile_views_30d', 0)}</span>
                    <span class="stat-label">Profile Views (30d)</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {min(stats.get('profile_views_30d', 0) / 800 * 100, 100)}%;"></div>
                    </div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('post_impressions_7d', 0)}</span>
                    <span class="stat-label">Post Impressions (7d)</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {min(stats.get('post_impressions_7d', 0) / 1200 * 100, 100)}%;"></div>
                    </div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📉</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('post_impressions_30d', 0)}</span>
                    <span class="stat-label">Post Impressions (30d)</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {min(stats.get('post_impressions_30d', 0) / 5000 * 100, 100)}%;"></div>
                    </div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🔍</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('search_appearances_7d', 0)}</span>
                    <span class="stat-label">Search Appearances (7d)</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {min(stats.get('search_appearances_7d', 0) / 20 * 100, 100)}%;"></div>
                    </div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('followers', 0)}</span>
                    <span class="stat-label">Followers</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {min(stats.get('followers', 0) / 600 * 100, 100)}%;"></div>
                    </div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📲</div>
                <div class="stat-data">
                    <span class="stat-value">+{stats.get('connection_growth_7d', 0)}</span>
                    <span class="stat-label">New Connections (7d)</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {min(stats.get('connection_growth_7d', 0) / 20 * 100, 100)}%;"></div>
                    </div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">💬</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('engagement_rate', 0)}%</span>
                    <span class="stat-label">Engagement Rate</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {min(stats.get('engagement_rate', 0) * 10, 100)}%;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="linkedin-content-section">
            <h3 class="section-title">📝 Ultimi Articoli</h3>
            <div class="posts-container">
                {posts_html}
            </div>
        </div>
        
        <div class="linkedin-content-section">
            <h3 class="section-title">🔄 Condivisioni Recenti</h3>
            <div class="shares-container">
                {shares_html}
            </div>
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
        
        <div class="profile-section">
            <h4 class="profile-section-title">Job Position</h4>
            <p class="profile-text">{profile.get('job_position', '')}</p>
        </div>
        
        <div class="profile-section">
            <h4 class="profile-section-title">Attitudini</h4>
            <p class="profile-text">{profile.get('attitude', '')}</p>
        </div>
        
        <div class="profile-section">
            <h4 class="profile-section-title">Bio</h4>
            <p class="profile-text">{profile.get('headline', '')}</p>
        </div>
        
        <div class="profile-location">
            <span>📍</span>
            <span>{profile.get('location', '')}</span>
        </div>
        
        <div class="profile-company">
            <span>💼</span>
            <a href="{profile.get('current_company_url', '#')}" target="_blank" rel="noopener">
                {profile.get('current_company', '')}
            </a>
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
