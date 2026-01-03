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

@app.get("/api/linkedin/mini", response_class=HTMLResponse)
async def get_linkedin_mini():
    """
    Returns LinkedIn mini stats (4 metrics only) for homepage
    """
    data_path = Path("/app/data/linkedin.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        stats = data.get("stats", {})
        
        # Build mini stats HTML - Only 4 cards
        html = f"""
        <h2 class="card-source-title gradient-text-linkedin">LinkedIn</h2>
        <div class="stats-grid-mini">
            <div class="stat-card-mini">
                <div class="stat-icon">📊</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('post_impressions_7d', 0)}</span>
                    <span class="stat-label">Impressions</span>
                </div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-icon">👥</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('followers', 0)}</span>
                    <span class="stat-label">Followers</span>
                </div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-icon">👁️</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('profile_views_90d', 0)}</span>
                    <span class="stat-label">Views</span>
                </div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-icon">🔍</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('search_appearances_7d', 0)}</span>
                    <span class="stat-label">Searches</span>
                </div>
            </div>
        </div>
        <div class="card-footer">
            <a href="/linkedin" class="btn btn-outline">View Details →</a>
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p class='text-muted-foreground'>LinkedIn data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p class='text-muted-foreground'>Error loading LinkedIn data</p>",
            status_code=500
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
        last_updated = data.get("last_updated", "")
        
        # Parse last updated
        try:
            updated_dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            updated_str = updated_dt.strftime("%d %b %Y, %H:%M")
        except:
            updated_str = "Unknown"
        
        # Build posts HTML (show up to 5 posts)
        posts_html = ""
        for post in recent_posts[:5]:
            post_url = post.get('url', '#')
            posts_html += f"""
            <a href="{post_url}" target="_blank" class="linkedin-post">
                <h4 class="post-title">{post.get('title', '')}</h4>
                <p class="post-excerpt">{post.get('excerpt', '')}</p>
                <span class="post-date">📅 {post.get('date', '')}</span>
            </a>
            """
        
        # Build HTML response - Only show real data available from LinkedIn dashboard
        html = f"""
        <h2 class="card-source-title">LinkedIn</h2>
        <div class="linkedin-stats-grid">
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
                <div class="stat-icon">👥</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('followers', 0)}</span>
                    <span class="stat-label">Followers</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {min(stats.get('followers', 0) / 700 * 100, 100)}%;"></div>
                    </div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">👁️</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('profile_views_90d', 0)}</span>
                    <span class="stat-label">Profile Views (90d)</span>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {min(stats.get('profile_views_90d', 0) / 200 * 100, 100)}%;"></div>
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
        </div>
        
        <div class="linkedin-content-section">
            <h3 class="section-title">📝 Ultimi Post</h3>
            <div class="posts-container">
                {posts_html if posts_html else '<p class="no-content">Nessun post recente disponibile</p>'}
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

@app.get("/api/exercism/mini", response_class=HTMLResponse)
async def get_exercism_mini():
    """
    Returns Exercism mini stats (4 metrics only) for homepage
    """
    data_path = Path("/app/data/exercism.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        stats = data.get("stats", {})
        badges = data.get("badges", [])
        tracks = data.get("tracks", [])
        
        reputation = stats.get("reputation", 0)
        total_badges = stats.get("total_badges", len(badges))
        total_solutions = stats.get("total_solutions", 0)
        total_tracks = stats.get("total_tracks", len(tracks))
        
        # Build mini stats HTML - Only 4 cards
        html = f"""
        <h2 class="card-source-title gradient-text-exercism">Exercism</h2>
        <div class="stats-grid-mini">
            <div class="stat-card-mini">
                <div class="stat-icon">⭐</div>
                <div class="stat-data">
                    <span class="stat-value">{reputation}</span>
                    <span class="stat-label">Reputation</span>
                </div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-icon">🏆</div>
                <div class="stat-data">
                    <span class="stat-value">{total_badges}</span>
                    <span class="stat-label">Badges</span>
                </div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-icon">✅</div>
                <div class="stat-data">
                    <span class="stat-value">{total_solutions}</span>
                    <span class="stat-label">Solutions</span>
                </div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-icon">💻</div>
                <div class="stat-data">
                    <span class="stat-value">{total_tracks}</span>
                    <span class="stat-label">Tracks</span>
                </div>
            </div>
        </div>
        <div class="card-footer">
            <a href="/exercism" class="btn btn-outline">View Details →</a>
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p class='text-muted-foreground'>Exercism data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p class='text-muted-foreground'>Error loading Exercism data</p>",
            status_code=500
        )

@app.get("/api/exercism", response_class=HTMLResponse)
async def get_exercism():
    """
    Returns Exercism profile data as HTML component for HTMX
    """
    data_path = Path("/app/data/exercism.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        profile = data.get("profile", {})
        stats = data.get("stats", {})
        badges = data.get("badges", [])
        tracks = data.get("tracks", [])
        recent_solutions = data.get("recent_solutions", [])
        extracted_at = data.get("extracted_at", "")
        
        # Parse extracted_at
        try:
            updated_dt = datetime.fromisoformat(extracted_at.replace("Z", "+00:00"))
            updated_str = updated_dt.strftime("%d %b %Y, %H:%M")
        except:
            updated_str = "Unknown"
        
        # Build stats cards
        reputation = stats.get("reputation", 0)
        total_badges = stats.get("total_badges", len(badges))
        total_solutions = stats.get("total_solutions", 0)
        total_tracks = stats.get("total_tracks", len(tracks))
        
        stats_html = f"""
        <div class="exercism-stats-grid">
            <div class="exercism-stat-card">
                <div class="exercism-stat-icon">⭐</div>
                <div class="exercism-stat-data">
                    <span class="exercism-stat-value">{reputation}</span>
                    <span class="exercism-stat-label">Reputation</span>
                </div>
            </div>
            <div class="exercism-stat-card">
                <div class="exercism-stat-icon">🏆</div>
                <div class="exercism-stat-data">
                    <span class="exercism-stat-value">{total_badges}</span>
                    <span class="exercism-stat-label">Badges</span>
                </div>
            </div>
            <div class="exercism-stat-card">
                <div class="exercism-stat-icon">✅</div>
                <div class="exercism-stat-data">
                    <span class="exercism-stat-value">{total_solutions}</span>
                    <span class="exercism-stat-label">Solutions</span>
                </div>
            </div>
            <div class="exercism-stat-card">
                <div class="exercism-stat-icon">💻</div>
                <div class="exercism-stat-data">
                    <span class="exercism-stat-value">{total_tracks}</span>
                    <span class="exercism-stat-label">Tracks</span>
                </div>
            </div>
        </div>
        """
        
        # Build badges section (show up to 10)
        badges_html = ""
        for badge in badges[:10]:
            badge_name = badge.get("name", "Unknown")
            badge_rarity = badge.get("rarity", "common")
            badge_icon = badge.get("icon_url", "")
            
            badges_html += f"""
            <div class="badge-item">
                <span class="badge-rarity {badge_rarity}"></span>
                <img src="{badge_icon}" alt="{badge_name}" class="badge-icon" />
                <span class="badge-name">{badge_name}</span>
            </div>
            """
        
        badges_section = f"""
        <div class="exercism-badges-section">
            <h3 class="section-title">🏆 Badges ({total_badges})</h3>
            <div class="badges-grid">
                {badges_html if badges_html else '<p class="no-content">No badges yet</p>'}
            </div>
        </div>
        """ if badges else ""
        
        # Build tracks section
        tracks_html = ""
        for track in tracks[:6]:  # Show up to 6
            track_name = track.get("name", "Unknown")
            track_icon = track.get("icon_url", "")
            exercises_count = track.get("exercises_completed", 0)
            
            tracks_html += f"""
            <div class="track-item">
                <img src="{track_icon}" alt="{track_name}" class="track-icon" />
                <div class="track-info">
                    <div class="track-name">{track_name}</div>
                    <div class="track-count">{exercises_count} exercises</div>
                </div>
            </div>
            """
        
        tracks_section = f"""
        <div class="exercism-tracks-section">
            <h3 class="section-title">💻 Tracks ({total_tracks})</h3>
            <div class="tracks-grid">
                {tracks_html if tracks_html else '<p class="no-content">No tracks yet</p>'}
            </div>
        </div>
        """ if tracks else ""
        
        # Build solutions section (show up to 5)
        solutions_html = ""
        for sol in recent_solutions[:5]:
            exercise = sol.get("exercise", "Unknown")
            track = sol.get("track", "Unknown")
            track_icon = sol.get("track_icon", "")
            published_at = sol.get("published_at", "")
            num_stars = sol.get("num_stars", 0)
            num_comments = sol.get("num_comments", 0)
            url = sol.get("url", "#")
            
            solutions_html += f"""
            <a href="{url}" target="_blank" class="solution-item">
                <div class="solution-header">
                    <img src="{track_icon}" alt="{track}" class="solution-track-icon" />
                    <span class="solution-title">{exercise}</span>
                    <span class="solution-track">{track}</span>
                </div>
                <div class="solution-meta">
                    <span class="solution-date">📅 {published_at}</span>
                    <div class="solution-stats">
                        <span>⭐ {num_stars}</span>
                        <span>💬 {num_comments}</span>
                    </div>
                </div>
            </a>
            """
        
        solutions_section = f"""
        <div class="exercism-solutions-section">
            <h3 class="section-title">📝 Recent Solutions</h3>
            <div class="solutions-container">
                {solutions_html if solutions_html else '<p class="no-content">No solutions yet</p>'}
            </div>
        </div>
        """ if recent_solutions else ""
        
        # Build complete HTML
        username = profile.get("username", "stanzinofree")
        html = f"""
        <h2 class="card-source-title">Exercism</h2>
        {stats_html}
        {badges_section}
        {tracks_section}
        {solutions_section}
        
        <div class="exercism-actions">
            <a href="https://exercism.org/profiles/{username}" target="_blank" class="btn-exercism">
                View Full Profile →
            </a>
        </div>
        
        <div class="exercism-last-update">
            🔄 Last sync: {updated_str}
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p>Exercism data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p>Error loading Exercism data: {str(e)}</p>",
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

@app.get("/api/github/mini", response_class=HTMLResponse)
async def get_github_mini():
    """
    Returns GitHub mini stats (4 metrics only) for homepage
    """
    data_path = Path("/app/data/github.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        stats = data.get("stats", {})
        
        # Build mini stats HTML - Only 4 cards
        html = f"""
        <h2 class="card-source-title gradient-text-github">GitHub</h2>
        <div class="stats-grid-mini">
            <div class="stat-card-mini">
                <div class="stat-icon">📦</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('public_repos', 0)}</span>
                    <span class="stat-label">Repositories</span>
                </div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-icon">⭐</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('total_stars', 0)}</span>
                    <span class="stat-label">Stars</span>
                </div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-icon">👥</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('followers', 0)}</span>
                    <span class="stat-label">Followers</span>
                </div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-icon">🔥</div>
                <div class="stat-data">
                    <span class="stat-value">{stats.get('current_streak', 0)}</span>
                    <span class="stat-label">Day Streak</span>
                </div>
            </div>
        </div>
        <div class="card-footer">
            <a href="/github" class="btn btn-outline">View Details →</a>
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p class='text-muted-foreground'>GitHub data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p class='text-muted-foreground'>Error loading GitHub data</p>",
            status_code=500
        )

@app.get("/api/github", response_class=HTMLResponse)
async def get_github():
    """
    Returns GitHub profile data as HTML component for HTMX
    """
    data_path = Path("/app/data/github.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        profile = data.get("profile", {})
        stats = data.get("stats", {})
        top_languages = data.get("top_languages", [])
        top_repos = data.get("top_repos", [])
        recent_activity = data.get("recent_activity", [])
        extracted_at = data.get("extracted_at", "")
        
        # Parse extracted_at
        try:
            updated_dt = datetime.fromisoformat(extracted_at.replace("Z", "+00:00"))
            updated_str = updated_dt.strftime("%d %b %Y, %H:%M")
        except:
            updated_str = "Unknown"
        
        # Build stats cards
        stats_html = f"""
        <div class="github-stats-grid">
            <div class="github-stat-card">
                <div class="github-stat-icon">📦</div>
                <div class="github-stat-data">
                    <span class="github-stat-value">{stats.get('public_repos', 0)}</span>
                    <span class="github-stat-label">Public Repositories</span>
                </div>
            </div>
            <div class="github-stat-card">
                <div class="github-stat-icon">⭐</div>
                <div class="github-stat-data">
                    <span class="github-stat-value">{stats.get('total_stars', 0)}</span>
                    <span class="github-stat-label">Total Stars</span>
                </div>
            </div>
            <div class="github-stat-card">
                <div class="github-stat-icon">🍴</div>
                <div class="github-stat-data">
                    <span class="github-stat-value">{stats.get('total_forks', 0)}</span>
                    <span class="github-stat-label">Total Forks</span>
                </div>
            </div>
            <div class="github-stat-card">
                <div class="github-stat-icon">👥</div>
                <div class="github-stat-data">
                    <span class="github-stat-value">{stats.get('followers', 0)}</span>
                    <span class="github-stat-label">Followers</span>
                </div>
            </div>
            <div class="github-stat-card">
                <div class="github-stat-icon">📈</div>
                <div class="github-stat-data">
                    <span class="github-stat-value">{stats.get('contributions_last_year', 0)}</span>
                    <span class="github-stat-label">Contributions (Year)</span>
                </div>
            </div>
            <div class="github-stat-card">
                <div class="github-stat-icon">🔥</div>
                <div class="github-stat-data">
                    <span class="github-stat-value">{stats.get('current_streak', 0)}</span>
                    <span class="github-stat-label">Current Streak (days)</span>
                </div>
            </div>
        </div>
        """
        
        # Build languages section
        languages_html = ""
        for lang in top_languages[:5]:
            languages_html += f"""
            <div class="language-item">
                <div class="language-header">
                    <span class="language-name">{lang.get('name', 'Unknown')}</span>
                    <span class="language-percentage">{lang.get('percentage', 0)}%</span>
                </div>
                <div class="language-bar">
                    <div class="language-fill" style="width: {lang.get('percentage', 0)}%;"></div>
                </div>
            </div>
            """
        
        languages_section = f"""
        <div class="github-languages-section">
            <h3 class="section-title">💻 Top Languages</h3>
            <div class="languages-container">
                {languages_html if languages_html else '<p class="no-content">No language data</p>'}
            </div>
        </div>
        """ if top_languages else ""
        
        # Build repos section
        repos_html = ""
        for repo in top_repos[:6]:
            repos_html += f"""
            <a href="{repo.get('url', '#')}" target="_blank" class="repo-item">
                <div class="repo-header">
                    <span class="repo-name">{repo.get('name', 'Unknown')}</span>
                    <span class="repo-lang">{repo.get('language', 'Unknown')}</span>
                </div>
                <p class="repo-description">{repo.get('description', 'No description')}</p>
                <div class="repo-stats">
                    <span>⭐ {repo.get('stars', 0)}</span>
                    <span>🍴 {repo.get('forks', 0)}</span>
                </div>
            </a>
            """
        
        repos_section = f"""
        <div class="github-repos-section">
            <h3 class="section-title">⭐ Top Repositories</h3>
            <div class="repos-grid">
                {repos_html if repos_html else '<p class="no-content">No repositories</p>'}
            </div>
        </div>
        """ if top_repos else ""
        
        # Build complete HTML
        username = profile.get("username", "stanzinofree")
        html = f"""
        <h2 class="card-source-title">GitHub</h2>
        {stats_html}
        {languages_section}
        {repos_section}
        
        <div class="github-actions">
            <a href="https://github.com/{username}" target="_blank" class="btn-github">
                View GitHub Profile →
            </a>
        </div>
        
        <div class="github-last-update">
            🔄 Last sync: {updated_str}
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p>GitHub data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p>Error loading GitHub data: {str(e)}</p>",
            status_code=500
        )
