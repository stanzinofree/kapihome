from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

app = FastAPI(title="KapiHome API", version="0.2.0")

# Health Score Algorithm
def calculate_health_score(welltory_data: Dict) -> Dict:
    """
    Calculate overall health score from Welltory metrics
    Returns: {
        'score': 0-100,
        'level': 'Excellent'|'Good'|'Fair'|'Poor',
        'emoji': '🟢'|'🟡'|'🟠'|'🔴',
        'insights': ['...']
    }
    """
    current = welltory_data.get('current', {})
    
    stress = current.get('stress')
    energy = current.get('energy')
    hrv = current.get('hrv')
    sleep = current.get('sleep_quality')
    mood = current.get('mood')
    rhr = current.get('resting_heart_rate')
    
    # Weights for each metric (total = 100%)
    weights = {
        'stress': 0.25,      # 25% - High importance
        'energy': 0.20,      # 20%
        'hrv': 0.20,         # 20% - Key recovery indicator
        'sleep': 0.15,       # 15%
        'mood': 0.10,        # 10%
        'rhr': 0.10          # 10%
    }
    
    scores = {}
    insights = []
    
    # Stress: Lower is better (invert scale)
    if stress is not None:
        stress_score = max(0, 100 - stress)  # 0 stress = 100 score, 100 stress = 0 score
        scores['stress'] = stress_score
        
        if stress >= 70:
            insights.append("⚠️ Stress molto alto - Pratica tecniche di rilassamento")
        elif stress >= 50:
            insights.append("⚡ Stress moderato - Fai una pausa")
        elif stress <= 30:
            insights.append("✅ Stress basso - Ottimo!")
    
    # Energy: Higher is better
    if energy is not None:
        scores['energy'] = energy
        
        if energy >= 80:
            insights.append("🚀 Energia eccellente!")
        elif energy < 40:
            insights.append("😴 Energia bassa - Riposo necessario")
    
    # HRV: Higher is better (normalize to 0-100, assuming 120 as max)
    if hrv is not None:
        hrv_score = min(100, (hrv / 120) * 100)
        scores['hrv'] = hrv_score
        
        if hrv >= 70:
            insights.append("❤️ HRV eccellente - Ottimo recupero!")
        elif hrv < 40:
            insights.append("💤 HRV basso - Recupero necessario")
    
    # Sleep Quality: Higher is better
    if sleep is not None:
        scores['sleep'] = sleep
        
        if sleep >= 80:
            insights.append("😴 Sonno di qualità eccellente!")
        elif sleep < 60:
            insights.append("🌙 Qualità del sonno migliorabile")
    
    # Mood: Scale 0-10 to 0-100
    if mood is not None:
        mood_score = mood * 10
        scores['mood'] = mood_score
        
        if mood >= 8:
            insights.append("😄 Umore ottimo!")
        elif mood <= 4:
            insights.append("😔 Umore basso - Prenditi cura di te")
    
    # Resting Heart Rate: Lower is better (normalize, assuming 60 optimal, 90 poor)
    if rhr is not None:
        # Optimal range: 50-70, score decreases above 70
        if rhr <= 60:
            rhr_score = 100
        elif rhr <= 70:
            rhr_score = 90
        elif rhr <= 80:
            rhr_score = 70
        else:
            rhr_score = max(0, 100 - (rhr - 60))
        
        scores['rhr'] = rhr_score
        
        if rhr <= 60:
            insights.append("💓 Frequenza cardiaca ottimale")
        elif rhr >= 80:
            insights.append("⚠️ Frequenza cardiaca elevata")
    
    # Calculate weighted average
    total_score = 0
    total_weight = 0
    
    for metric, score in scores.items():
        weight = weights.get(metric, 0)
        total_score += score * weight
        total_weight += weight
    
    # Normalize to 0-100
    final_score = int(total_score / total_weight) if total_weight > 0 else 0
    
    # Determine level and emoji
    if final_score >= 80:
        level = "Excellent"
        emoji = "🟢"
        badge = "💪 Forma Eccellente"
    elif final_score >= 65:
        level = "Good"
        emoji = "🟡"
        badge = "👍 Buona Salute"
    elif final_score >= 50:
        level = "Fair"
        emoji = "🟠"
        badge = "⚠️ Salute Discreta"
    else:
        level = "Poor"
        emoji = "🔴"
        badge = "🚨 Attenzione Richiesta"
    
    # Add general insight based on score
    if final_score >= 80:
        insights.insert(0, "🌟 Stai mantenendo ottimi livelli di salute!")
    elif final_score < 50:
        insights.insert(0, "🏥 Considera di consultare un medico se i valori persistono")
    
    return {
        'score': final_score,
        'level': level,
        'emoji': emoji,
        'badge': badge,
        'insights': insights[:5],  # Max 5 insights
        'metrics_count': len(scores),
        'component_scores': scores
    }

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
    Returns profile row with 3 columns: Photo | Info | Work/Contact
    Full-width layout for homepage
    """
    profile_path = Path("/app/data/profile.json")
    udemy_path = Path("/app/data/udemy.json")
    welltory_path = Path("/app/data/welltory.json")
    
    try:
        with open(profile_path, "r") as f:
            profile = json.load(f)
        
        # Load Udemy data to get most recently accessed course
        current_course = None
        try:
            with open(udemy_path, "r") as f:
                udemy_data = json.load(f)
                in_progress = udemy_data.get("in_progress_courses", [])
                if in_progress and len(in_progress) > 0:
                    # Take the first course (most recently accessed)
                    current_course = in_progress[0]
        except:
            pass
        
        # Load Welltory data and calculate health score
        health_score = None
        try:
            with open(welltory_path, "r") as f:
                welltory_data = json.load(f)
                health_score = calculate_health_score(welltory_data)
        except:
            pass
        
        # Build health score HTML - simplified version
        health_html = ""
        if health_score:
            health_html = f"""
            <div class="profile-divider"></div>
            <a href="/welltory" class="profile-health-link">
                <div class="profile-health-simple">
                    <span class="health-emoji-large">{health_score.get('emoji', '🟢')}</span>
                    <div class="health-info">
                        <strong>🏥 Stato di Salute</strong>
                        <p class="health-label">{health_score.get('badge', '💪 Forma Eccellente')}</p>
                        <span class="health-score-value">Score: {health_score.get('score', 0)}/100</span>
                    </div>
                    <span class="health-arrow">→</span>
                </div>
            </a>
            """
        
        # Build profile row HTML - 3 columns layout
        html = f"""
        <!-- Column 1: Photo (1/3) -->
        <div class="profile-photo-col">
            <img src="{profile.get('avatar_url', '/static/images/avatar.jpg')}" 
                 alt="{profile.get('name', 'Alessandro Middei')}" 
                 class="profile-avatar-large" />
            <h2 class="profile-name">{profile.get('name', 'Alessandro Middei')}</h2>
            {'<div class="profile-divider"></div><div class="profile-learning"><strong>📚 Attualmente sto studiando:</strong><p class="learning-course">' + current_course.get('title', '') + '</p>' + ('<p class="learning-instructor">👨‍🏫 ' + current_course.get('instructor', '') + '</p>' if current_course.get('instructor') else '') + '<div class="learning-progress"><div class="learning-progress-bar" style="width: ' + str(current_course.get('progress', 0)) + '%"></div></div><span class="learning-percentage">' + str(current_course.get('progress', 0)) + '% completato</span></div>' if current_course else ''}
            {health_html}
        </div>
        
        <!-- Column 2: Info (1/3) -->
        <div class="profile-info-col">
            <h4 class="profile-col-title">Info</h4>
            <div class="profile-info-item">
                <strong>Job Position:</strong>
                <p>{profile.get('job_position', '')}</p>
            </div>
            <div class="profile-info-item">
                <strong>Attitudini:</strong>
                <p>{profile.get('attitudini', '')}</p>
            </div>
            <div class="profile-info-item">
                <strong>Bio:</strong>
                <p>{profile.get('bio', '')}</p>
            </div>
        </div>
        
        <!-- Column 3: Work & Contact (1/3) -->
        <div class="profile-contact-col">
            <h4 class="profile-col-title">Work & Contact</h4>
            <div class="profile-contact-item">
                <span class="contact-icon">💼</span>
                <div class="contact-content">
                    <strong>Current Work</strong>
                    <span>{profile.get('current_work', '')}</span>
                </div>
            </div>
            <div class="profile-contact-item">
                <span class="contact-icon">📍</span>
                <div class="contact-content">
                    <strong>Location</strong>
                    <span>{profile.get('location', '')}</span>
                </div>
            </div>
            <div class="profile-contact-item">
                <span class="contact-icon">✉️</span>
                <div class="contact-content">
                    <strong>Email</strong>
                    <a href="mailto:alessandro@middei.info">alessandro@middei.info</a>
                </div>
            </div>
            <div class="profile-contact-item">
                <span class="contact-icon">📞</span>
                <div class="contact-content">
                    <strong>Book a Call</strong>
                    <a href="https://cal.com/alessandro-middei-8eimru" target="_blank" rel="noopener" class="cal-link">
                        Schedule on Cal.com →
                    </a>
                </div>
            </div>
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

@app.get("/api/cal/mini", response_class=HTMLResponse)
async def get_cal_mini():
    """
    Returns Cal.com availability card for homepage
    Shows upcoming events and availability status
    """
    # Static data - can be enhanced with real Cal.com API integration
    
    html = f"""
    <h2 class="card-source-title gradient-text-cal">Calendar</h2>
    <div class="cal-content">
        <p class="cal-description">
            Prossimi eventi e disponibilità
        </p>
        
        <div class="cal-features">
            <div class="cal-feature">
                <span class="cal-icon">📅</span>
                <span class="cal-text">30 min slots disponibili</span>
            </div>
            <div class="cal-feature">
                <span class="cal-icon">🌍</span>
                <span class="cal-text">Online (Google Meet)</span>
            </div>
            <div class="cal-feature">
                <span class="cal-icon">⏰</span>
                <span class="cal-text">Lun-Ven 9:00-18:00</span>
            </div>
        </div>
        
        <div class="cal-availability">
            <p class="cal-availability-text">
                <span class="cal-status">🟢</span> Disponibile questa settimana
            </p>
        </div>
    </div>
    """
    
    return HTMLResponse(content=html)

@app.get("/api/udemy/mini", response_class=HTMLResponse)
async def get_udemy_mini():
    """
    Returns Udemy student learning stats card for homepage
    Shows enrolled courses, completed, and weekly learning activity
    """
    data_path = Path("/app/data/udemy.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        student = data.get("student", {})
        stats = data.get("stats", {})
        
        html = f"""
        <h2 class="card-source-title gradient-text-udemy">Udemy Learning</h2>
        <div class="udemy-stats-mini">
            <div class="stat-row">
                <div class="stat-item">
                    <span class="stat-icon">📚</span>
                    <div class="stat-content">
                        <span class="stat-value">{student.get('total_courses', 0)}</span>
                        <span class="stat-label">Corsi totali</span>
                    </div>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">⏱️</span>
                    <div class="stat-content">
                        <span class="stat-value">{student.get('weekly_minutes_current', 0)}/{student.get('weekly_minutes_goal', 30)}</span>
                        <span class="stat-label">Minuti/settimana</span>
                    </div>
                </div>
            </div>
            <div class="stat-row">
                <div class="stat-item">
                    <span class="stat-icon">👀</span>
                    <div class="stat-content">
                        <span class="stat-value">{student.get('visits_this_week', 0)}/{student.get('visits_last_week', 0)}</span>
                        <span class="stat-label">Visite sett.</span>
                    </div>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">🔥</span>
                    <div class="stat-content">
                        <span class="stat-value">{student.get('weekly_streak', 0)}</span>
                        <span class="stat-label">Sett. consecutive</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card-footer">
            <a href="/udemy" class="btn btn-outline">View Courses →</a>
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p class='text-muted-foreground'>Udemy data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p class='text-muted-foreground'>Error loading Udemy data</p>",
            status_code=500
        )

@app.get("/api/welltory/mini", response_class=HTMLResponse)
async def get_welltory_mini():
    """
    Returns Welltory health metrics card for homepage
    Shows stress, energy, HRV and other wellness metrics
    """
    data_path = Path("/app/data/welltory.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        current = data.get("current", {})
        date = data.get("date", "")
        
        stress = current.get('stress')
        energy = current.get('energy')
        hrv = current.get('hrv')
        mood = current.get('mood')
        
        # Determine stress level indicator
        stress_indicator = "🟢"
        stress_label = "Low"
        if stress:
            if stress >= 60:
                stress_indicator = "🔴"
                stress_label = "High"
            elif stress >= 30:
                stress_indicator = "🟡"
                stress_label = "Medium"
        
        # Determine energy level indicator
        energy_indicator = "⚡"
        energy_label = "Good"
        if energy:
            if energy >= 70:
                energy_indicator = "🚀"
                energy_label = "High"
            elif energy < 40:
                energy_indicator = "😴"
                energy_label = "Low"
        
        html = f"""
        <h2 class="card-source-title gradient-text-welltory">Health Metrics</h2>
        <div class="welltory-stats-mini">
            <div class="stat-row">
                <div class="stat-item">
                    <span class="stat-icon">{stress_indicator}</span>
                    <div class="stat-content">
                        <span class="stat-value">{stress if stress is not None else 'N/A'}</span>
                        <span class="stat-label">Stress {stress_label if stress is not None else ''}</span>
                    </div>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">{energy_indicator}</span>
                    <div class="stat-content">
                        <span class="stat-value">{energy if energy is not None else 'N/A'}</span>
                        <span class="stat-label">Energy {energy_label if energy is not None else ''}</span>
                    </div>
                </div>
            </div>
            <div class="stat-row">
                <div class="stat-item">
                    <span class="stat-icon">❤️</span>
                    <div class="stat-content">
                        <span class="stat-value">{hrv if hrv is not None else 'N/A'}</span>
                        <span class="stat-label">HRV</span>
                    </div>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">😊</span>
                    <div class="stat-content">
                        <span class="stat-value">{mood if mood is not None else 'N/A'}</span>
                        <span class="stat-label">Mood</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card-footer">
            <a href="/welltory" class="btn btn-outline">View Details →</a>
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p class='text-muted-foreground'>Welltory data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p class='text-muted-foreground'>Error loading Welltory data</p>",
            status_code=500
        )

@app.get("/api/welltory", response_class=HTMLResponse)
async def get_welltory():
    """
    Returns Welltory full health dashboard with charts
    """
    data_path = Path("/app/data/welltory.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        current = data.get("current", {})
        historical = data.get("historical_data", [])
        last_updated = data.get("last_updated", "")
        
        # Calculate health score
        health_score = calculate_health_score(data)
        
        # Build stats cards
        stats_html = f"""
        <div class="welltory-stats-grid">
            <div class="welltory-stat-card health-score-card">
                <div class="stat-icon">{health_score.get('emoji', '🟢')}</div>
                <div class="stat-data">
                    <span class="stat-value">{health_score.get('score', 0)}</span>
                    <span class="stat-label">{health_score.get('badge', 'Health Score')}</span>
                </div>
            </div>
            <div class="welltory-stat-card">
                <div class="stat-icon">😰</div>
                <div class="stat-data">
                    <span class="stat-value">{current.get('stress', 'N/A')}</span>
                    <span class="stat-label">Stress Level</span>
                </div>
            </div>
            <div class="welltory-stat-card">
                <div class="stat-icon">⚡</div>
                <div class="stat-data">
                    <span class="stat-value">{current.get('energy', 'N/A')}</span>
                    <span class="stat-label">Energy</span>
                </div>
            </div>
            <div class="welltory-stat-card">
                <div class="stat-icon">❤️</div>
                <div class="stat-data">
                    <span class="stat-value">{current.get('hrv', 'N/A')}</span>
                    <span class="stat-label">HRV</span>
                </div>
            </div>
            <div class="welltory-stat-card">
                <div class="stat-icon">💓</div>
                <div class="stat-data">
                    <span class="stat-value">{current.get('resting_heart_rate', 'N/A')}</span>
                    <span class="stat-label">Resting HR</span>
                </div>
            </div>
            <div class="welltory-stat-card">
                <div class="stat-icon">😴</div>
                <div class="stat-data">
                    <span class="stat-value">{current.get('sleep_quality', 'N/A')}</span>
                    <span class="stat-label">Sleep Quality</span>
                </div>
            </div>
        </div>
        """
        
        # Build insights
        insights_html = "".join([f"<li>{i}</li>" for i in health_score.get('insights', [])])
        
        # Build detailed metrics explanations
        metrics_explanations = f"""
        <div class="metrics-explanations">
            <div class="metric-explain">
                <h4>😰 Livello di Stress</h4>
                <p class="current-value">Valore attuale: <strong>{current.get('stress', 'N/A')}</strong></p>
                <p class="explanation">Lo stress indica quanto il tuo corpo è sotto pressione. Valori bassi (0-30) sono ottimali, medi (31-60) richiedono attenzione, alti (61-100) necessitano di riposo e recupero.</p>
            </div>
            
            <div class="metric-explain">
                <h4>⚡ Energia</h4>
                <p class="current-value">Valore attuale: <strong>{current.get('energy', 'N/A')}</strong></p>
                <p class="explanation">L'energia misura la tua capacità fisica e mentale di affrontare la giornata. Valori alti (70-100) indicano forma ottimale, medi (40-69) suggeriscono di bilanciare attività e riposo, bassi (<40) richiedono recupero.</p>
            </div>
            
            <div class="metric-explain">
                <h4>❤️ HRV (Heart Rate Variability)</h4>
                <p class="current-value">Valore attuale: <strong>{current.get('hrv', 'N/A')}</strong></p>
                <p class="explanation">L'HRV misura la variabilità tra i battiti cardiaci. Valori più alti indicano migliore capacità di recupero e resilienza del sistema nervoso. È uno dei migliori indicatori di salute generale e fitness cardiovascolare.</p>
            </div>
            
            <div class="metric-explain">
                <h4>💓 Frequenza Cardiaca a Riposo</h4>
                <p class="current-value">Valore attuale: <strong>{current.get('resting_heart_rate', 'N/A')} bpm</strong></p>
                <p class="explanation">La frequenza cardiaca a riposo indica l'efficienza del tuo cuore. Valori più bassi (50-60 bpm) indicano migliore fitness cardiovascolare. Un aumento improvviso può segnalare stress, malattia o sovrallenamento.</p>
            </div>
            
            <div class="metric-explain">
                <h4>😴 Qualità del Sonno</h4>
                <p class="current-value">Valore attuale: <strong>{current.get('sleep_quality', 'N/A')}</strong></p>
                <p class="explanation">La qualità del sonno valuta quanto il tuo riposo notturno è stato rigenerante. Include durata, profondità e continuità. Valori alti (80-100) indicano sonno ristoratore, bassi (<60) suggeriscono di migliorare igiene del sonno.</p>
            </div>
            
            <div class="metric-explain">
                <h4>😊 Umore</h4>
                <p class="current-value">Valore attuale: <strong>{current.get('mood', 'N/A')}</strong></p>
                <p class="explanation">L'umore riflette il tuo stato emotivo generale. È influenzato da stress, sonno, attività fisica e nutrizione. Monitorarlo ti aiuta a identificare pattern e fattori che influenzano il tuo benessere mentale.</p>
            </div>
        </div>
        """
        
        html = f"""
        <h2 class="card-source-title gradient-text-welltory">Welltory Health Dashboard</h2>
        
        {stats_html}
        
        <div class="health-insights-section">
            <h3>💡 Analisi Generale</h3>
            <ul class="insights-list">{insights_html}</ul>
        </div>
        
        <div class="health-metrics-detailed">
            <h3>📊 Spiegazione Metriche</h3>
            {metrics_explanations}
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <canvas id="stress-chart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="energy-chart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="hrv-chart"></canvas>
            </div>
        </div>
        
        <script>
        const historicalData = {json.dumps(historical[:30])};
        
        // Stress Chart
        new Chart(document.getElementById('stress-chart'), {{
            type: 'line',
            data: {{
                labels: historicalData.map(d => new Date(d.date).toLocaleDateString('it-IT')),
                datasets: [{{
                    label: 'Stress',
                    data: historicalData.map(d => d.stats.stress),
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4
                }}]
            }},
            options: {{ responsive: true, plugins: {{ title: {{ display: true, text: 'Stress Trend' }} }} }}
        }});
        
        // Energy Chart  
        new Chart(document.getElementById('energy-chart'), {{
            type: 'line',
            data: {{
                labels: historicalData.map(d => new Date(d.date).toLocaleDateString('it-IT')),
                datasets: [{{
                    label: 'Energy',
                    data: historicalData.map(d => d.stats.energy),
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    tension: 0.4
                }}]
            }},
            options: {{ responsive: true, plugins: {{ title: {{ display: true, text: 'Energy Trend' }} }} }}
        }});
        
        // HRV Chart
        new Chart(document.getElementById('hrv-chart'), {{
            type: 'line',
            data: {{
                labels: historicalData.map(d => new Date(d.date).toLocaleDateString('it-IT')),
                datasets: [{{
                    label: 'HRV',
                    data: historicalData.map(d => d.stats.hrv),
                    borderColor: 'rgb(236, 72, 153)',
                    backgroundColor: 'rgba(236, 72, 153, 0.1)',
                    tension: 0.4
                }}]
            }},
            options: {{ responsive: true, plugins: {{ title: {{ display: true, text: 'HRV Trend' }} }} }}
        }});
        </script>
        
        <div class="last-update">Last updated: {last_updated}</div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(content="<p>Welltory data not available</p>", status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"<p>Error: {str(e)}</p>", status_code=500)

@app.get("/api/rtm/mini", response_class=HTMLResponse)
async def get_rtm_mini():
    """
    Returns Remember The Milk mini stats card for homepage
    Shows active tasks, upcoming deadlines, and weekly/monthly stats
    """
    data_path = Path("/app/data/rtm.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        stats = data.get("stats", {})
        active_tasks = data.get("active_tasks", [])
        upcoming_tasks = data.get("upcoming_tasks", [])
        overdue_tasks = data.get("overdue_tasks", [])
        
        # Build tasks preview (show up to 3 most urgent)
        tasks_html = ""
        urgent_tasks = overdue_tasks[:2] + active_tasks[:1] if overdue_tasks else active_tasks[:3]
        
        for task in urgent_tasks:
            priority_icon = "🔴" if task.get('priority') == "1" else "🟡" if task.get('priority') == "2" else "🟢"
            is_overdue = task in overdue_tasks
            task_class = "rtm-task-overdue" if is_overdue else "rtm-task-active"
            
            tasks_html += f"""
            <div class="{task_class}">
                <span class="task-priority">{priority_icon}</span>
                <span class="task-name">{task.get('name', '')}</span>
                <span class="task-due">{task.get('due_date', '')}</span>
            </div>
            """
        
        html = f"""
        <h2 class="card-source-title gradient-text-rtm">Tasks (RTM)</h2>
        <div class="rtm-stats-mini">
            <div class="stat-row">
                <div class="stat-item">
                    <span class="stat-icon">📋</span>
                    <div class="stat-content">
                        <span class="stat-value">{stats.get('active_tasks', 0)}</span>
                        <span class="stat-label">Task attivi</span>
                    </div>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">⚠️</span>
                    <div class="stat-content">
                        <span class="stat-value">{stats.get('overdue_tasks', 0)}</span>
                        <span class="stat-label">Scaduti</span>
                    </div>
                </div>
            </div>
            <div class="stat-row">
                <div class="stat-item">
                    <span class="stat-icon">✅</span>
                    <div class="stat-content">
                        <span class="stat-value">{stats.get('completed_this_week', 0)}</span>
                        <span class="stat-label">Completati (7gg)</span>
                    </div>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">📅</span>
                    <div class="stat-content">
                        <span class="stat-value">{stats.get('due_this_week', 0)}</span>
                        <span class="stat-label">In scadenza</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="rtm-tasks-preview">
            <h4 class="rtm-section-title">🎯 Task più urgenti</h4>
            {tasks_html if tasks_html else '<p class="no-tasks">Nessun task attivo</p>'}
        </div>
        
        <div class="card-footer">
            <a href="/rtm" class="btn btn-outline">View All Tasks →</a>
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p class='text-muted-foreground'>RTM data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p class='text-muted-foreground'>Error loading RTM data: {str(e)}</p>",
            status_code=500
        )

@app.get("/api/rtm", response_class=HTMLResponse)
async def get_rtm():
    """
    Returns full Remember The Milk tasks data as HTML component for HTMX
    """
    data_path = Path("/app/data/rtm.json")
    
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
        
        stats = data.get("stats", {})
        active_tasks = data.get("active_tasks", [])
        upcoming_tasks = data.get("upcoming_tasks", [])
        overdue_tasks = data.get("overdue_tasks", [])
        lists = data.get("lists", [])
        extracted_at = data.get("extracted_at", "")
        
        # Parse extracted_at
        try:
            updated_dt = datetime.fromisoformat(extracted_at.replace("Z", "+00:00"))
            updated_str = updated_dt.strftime("%d %b %Y, %H:%M")
        except:
            updated_str = "Unknown"
        
        # Build stats cards
        stats_html = f"""
        <div class="rtm-stats-grid">
            <div class="rtm-stat-card">
                <div class="rtm-stat-icon">📋</div>
                <div class="rtm-stat-data">
                    <span class="rtm-stat-value">{stats.get('total_tasks', 0)}</span>
                    <span class="rtm-stat-label">Task totali</span>
                </div>
            </div>
            <div class="rtm-stat-card">
                <div class="rtm-stat-icon">✅</div>
                <div class="rtm-stat-data">
                    <span class="rtm-stat-value">{stats.get('active_tasks', 0)}</span>
                    <span class="rtm-stat-label">Task attivi</span>
                </div>
            </div>
            <div class="rtm-stat-card">
                <div class="rtm-stat-icon">📅</div>
                <div class="rtm-stat-data">
                    <span class="rtm-stat-value">{stats.get('due_today', 0)}</span>
                    <span class="rtm-stat-label">Scadenza oggi</span>
                </div>
            </div>
            <div class="rtm-stat-card">
                <div class="rtm-stat-icon">⚠️</div>
                <div class="rtm-stat-data">
                    <span class="rtm-stat-value">{stats.get('overdue_tasks', 0)}</span>
                    <span class="rtm-stat-label">Scaduti</span>
                </div>
            </div>
            <div class="rtm-stat-card">
                <div class="rtm-stat-icon">🎯</div>
                <div class="rtm-stat-data">
                    <span class="rtm-stat-value">{stats.get('completed_this_week', 0)}</span>
                    <span class="rtm-stat-label">Completati (7gg)</span>
                </div>
            </div>
            <div class="rtm-stat-card">
                <div class="rtm-stat-icon">📊</div>
                <div class="rtm-stat-data">
                    <span class="rtm-stat-value">{stats.get('completed_this_month', 0)}</span>
                    <span class="rtm-stat-label">Completati (30gg)</span>
                </div>
            </div>
        </div>
        """
        
        # Build overdue tasks section
        overdue_html = ""
        for task in overdue_tasks:
            priority_icon = "🔴" if task.get('priority') == "1" else "🟡" if task.get('priority') == "2" else "🟢"
            tags_html = " ".join([f'<span class="task-tag">{tag}</span>' for tag in task.get('tags', [])])
            
            overdue_html += f"""
            <div class="rtm-task-item rtm-task-overdue">
                <div class="task-header">
                    <span class="task-priority">{priority_icon}</span>
                    <span class="task-name">{task.get('name', '')}</span>
                    <span class="task-list-badge">{task.get('list', '')}</span>
                </div>
                <div class="task-meta">
                    <span class="task-due">📅 {task.get('due_date', '')}</span>
                    <div class="task-tags">{tags_html}</div>
                </div>
            </div>
            """
        
        overdue_section = f"""
        <div class="rtm-tasks-section">
            <h3 class="section-title">⚠️ Task Scaduti ({len(overdue_tasks)})</h3>
            <div class="rtm-tasks-container">
                {overdue_html if overdue_html else '<p class="no-content">Nessun task scaduto</p>'}
            </div>
        </div>
        """ if overdue_tasks else ""
        
        # Build active tasks section
        active_html = ""
        for task in active_tasks:
            priority_icon = "🔴" if task.get('priority') == "1" else "🟡" if task.get('priority') == "2" else "🟢"
            tags_html = " ".join([f'<span class="task-tag">{tag}</span>' for tag in task.get('tags', [])])
            
            active_html += f"""
            <div class="rtm-task-item">
                <div class="task-header">
                    <span class="task-priority">{priority_icon}</span>
                    <span class="task-name">{task.get('name', '')}</span>
                    <span class="task-list-badge">{task.get('list', '')}</span>
                </div>
                <div class="task-meta">
                    <span class="task-due">📅 {task.get('due_date', '')}</span>
                    <div class="task-tags">{tags_html}</div>
                </div>
            </div>
            """
        
        active_section = f"""
        <div class="rtm-tasks-section">
            <h3 class="section-title">📋 Task Attivi ({len(active_tasks)})</h3>
            <div class="rtm-tasks-container">
                {active_html if active_html else '<p class="no-content">Nessun task attivo</p>'}
            </div>
        </div>
        """ if active_tasks else ""
        
        # Build upcoming tasks section
        upcoming_html = ""
        for task in upcoming_tasks:
            priority_icon = "🔴" if task.get('priority') == "1" else "🟡" if task.get('priority') == "2" else "🟢"
            tags_html = " ".join([f'<span class="task-tag">{tag}</span>' for tag in task.get('tags', [])])
            
            upcoming_html += f"""
            <div class="rtm-task-item">
                <div class="task-header">
                    <span class="task-priority">{priority_icon}</span>
                    <span class="task-name">{task.get('name', '')}</span>
                    <span class="task-list-badge">{task.get('list', '')}</span>
                </div>
                <div class="task-meta">
                    <span class="task-due">📅 {task.get('due_date', '')}</span>
                    <div class="task-tags">{tags_html}</div>
                </div>
            </div>
            """
        
        upcoming_section = f"""
        <div class="rtm-tasks-section">
            <h3 class="section-title">📅 Prossimi Task ({len(upcoming_tasks)})</h3>
            <div class="rtm-tasks-container">
                {upcoming_html if upcoming_html else '<p class="no-content">Nessun task in arrivo</p>'}
            </div>
        </div>
        """ if upcoming_tasks else ""
        
        # Build lists section
        lists_html = ""
        for lst in lists:
            lists_html += f"""
            <div class="rtm-list-item">
                <span class="list-name">📁 {lst.get('name', '')}</span>
                <span class="list-count">{lst.get('task_count', 0)} tasks</span>
            </div>
            """
        
        lists_section = f"""
        <div class="rtm-lists-section">
            <h3 class="section-title">📁 Liste</h3>
            <div class="rtm-lists-grid">
                {lists_html if lists_html else '<p class="no-content">Nessuna lista</p>'}
            </div>
        </div>
        """ if lists else ""
        
        # Build complete HTML
        html = f"""
        <h2 class="card-source-title">Remember The Milk - Tasks</h2>
        {stats_html}
        {overdue_section}
        {active_section}
        {upcoming_section}
        {lists_section}
        
        <div class="rtm-actions">
            <a href="https://www.rememberthemilk.com" target="_blank" class="btn-rtm">
                Open Remember The Milk →
            </a>
        </div>
        
        <div class="rtm-last-update">
            🔄 Last sync: {updated_str}
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except FileNotFoundError:
        return HTMLResponse(
            content="<p>RTM data not available</p>",
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<p>Error loading RTM data: {str(e)}</p>",
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


@app.get("/api/about-me", response_class=HTMLResponse)
async def get_about_me():
    """
    Returns infographic about me page with data storytelling
    Combines all data sources to tell a comprehensive story
    """
    # Load all data sources
    profile_path = Path("/app/data/profile.json")
    linkedin_path = Path("/app/data/linkedin.json")
    github_path = Path("/app/data/github.json")
    exercism_path = Path("/app/data/exercism.json")
    udemy_path = Path("/app/data/udemy.json")
    welltory_path = Path("/app/data/welltory.json")
    rtm_path = Path("/app/data/rtm.json")
    
    try:
        # Load profile
        profile = {}
        try:
            with open(profile_path, "r") as f:
                profile = json.load(f)
        except:
            pass
        
        # Load LinkedIn
        linkedin_data = {}
        try:
            with open(linkedin_path, "r") as f:
                linkedin_data = json.load(f)
        except:
            pass
        
        # Load GitHub
        github_data = {}
        try:
            with open(github_path, "r") as f:
                github_data = json.load(f)
        except:
            pass
        
        # Load Exercism
        exercism_data = {}
        try:
            with open(exercism_path, "r") as f:
                exercism_data = json.load(f)
        except:
            pass
        
        # Load Udemy
        udemy_data = {}
        try:
            with open(udemy_path, "r") as f:
                udemy_data = json.load(f)
        except:
            pass
        
        # Load Welltory and calculate health score
        welltory_data = {}
        health_score = None
        try:
            with open(welltory_path, "r") as f:
                welltory_data = json.load(f)
                health_score = calculate_health_score(welltory_data)
        except:
            pass
        
        # Load RTM
        rtm_data = {}
        try:
            with open(rtm_path, "r") as f:
                rtm_data = json.load(f)
        except:
            pass
        
        # Extract key metrics
        linkedin_stats = linkedin_data.get("stats", {})
        github_stats = github_data.get("stats", {})
        exercism_stats = exercism_data.get("stats", {})
        udemy_student = udemy_data.get("student", {})
        rtm_stats = rtm_data.get("stats", {})
        welltory_current = welltory_data.get("current", {})
        
        html = f"""
        <div class="about-hero">
            <div class="hero-avatar">
                <img src="{profile.get('avatar_url', '/static/images/avatar.jpg')}" alt="Alessandro Middei" />
            </div>
            <h1 class="hero-title">Alessandro Middei</h1>
            <p class="hero-subtitle">{profile.get('job_position', 'Senior Software Engineer')}</p>
            <p class="hero-bio">{profile.get('bio', '')}</p>
        </div>
        
        <div class="data-story-section">
            <h2 class="story-title">📊 My Life in Numbers</h2>
            <p class="story-intro">Ecco come vivo, lavoro e cresco ogni giorno, raccontato attraverso i dati.</p>
        </div>
        
        <!-- Health & Wellness -->
        <div class="story-block health-block">
            <div class="block-header">
                <h3>🏥 Salute e Benessere</h3>
                <span class="block-badge">{health_score.get('badge', 'In Forma') if health_score else 'N/A'}</span>
            </div>
            <div class="block-content">
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-icon">{health_score.get('emoji', '🟢') if health_score else '📊'}</div>
                        <div class="metric-value">{health_score.get('score', 'N/A') if health_score else 'N/A'}</div>
                        <div class="metric-label">Health Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">😰</div>
                        <div class="metric-value">{welltory_current.get('stress', 'N/A')}</div>
                        <div class="metric-label">Stress Level</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">⚡</div>
                        <div class="metric-value">{welltory_current.get('energy', 'N/A')}</div>
                        <div class="metric-label">Energy</div>
                    </div>
                </div>
                <p class="block-story">
                    Monitoro costantemente la mia salute per mantenere un equilibrio tra lavoro intenso e benessere personale. 
                    {'Un livello di stress sotto controllo e alta energia mi permettono di essere produttivo senza compromettere la salute.' if health_score and health_score.get('score', 0) >= 70 else 'Sto lavorando per migliorare il mio equilibrio vita-lavoro.'}
                </p>
            </div>
        </div>
        
        <!-- Professional Network -->
        <div class="story-block network-block">
            <div class="block-header">
                <h3>💼 Network Professionale</h3>
                <span class="block-badge">LinkedIn Active</span>
            </div>
            <div class="block-content">
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-icon">👥</div>
                        <div class="metric-value">{linkedin_stats.get('followers', 0)}</div>
                        <div class="metric-label">Followers</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">📊</div>
                        <div class="metric-value">{linkedin_stats.get('post_impressions_7d', 0)}</div>
                        <div class="metric-label">Weekly Impressions</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">👁️</div>
                        <div class="metric-value">{linkedin_stats.get('profile_views_90d', 0)}</div>
                        <div class="metric-label">Profile Views (90d)</div>
                    </div>
                </div>
                <p class="block-story">
                    Condivido regolarmente contenuti tecnici e insights su LinkedIn, raggiungendo migliaia di professionisti. 
                    Il mio network cresce costantemente grazie a contenuti di valore su architetture software, cloud e best practices.
                </p>
            </div>
        </div>
        
        <!-- Coding Activity -->
        <div class="story-block coding-block">
            <div class="block-header">
                <h3>💻 Attività di Coding</h3>
                <span class="block-badge">Open Source Contributor</span>
            </div>
            <div class="block-content">
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-icon">📦</div>
                        <div class="metric-value">{github_stats.get('public_repos', 0)}</div>
                        <div class="metric-label">Public Repos</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">⭐</div>
                        <div class="metric-value">{github_stats.get('total_stars', 0)}</div>
                        <div class="metric-label">Total Stars</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">🔥</div>
                        <div class="metric-value">{github_stats.get('current_streak', 0)}</div>
                        <div class="metric-label">Current Streak</div>
                    </div>
                </div>
                <p class="block-story">
                    Contribuisco attivamente a progetti open source e mantengo una streak di commit costante. 
                    Il codice è la mia passione, e GitHub è il mio laboratorio dove sperimento nuove tecnologie e condivido soluzioni.
                </p>
            </div>
        </div>
        
        <!-- Learning & Growth -->
        <div class="story-block learning-block">
            <div class="block-header">
                <h3>📚 Apprendimento Continuo</h3>
                <span class="block-badge">Lifelong Learner</span>
            </div>
            <div class="block-content">
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-icon">🎓</div>
                        <div class="metric-value">{udemy_student.get('total_courses', 0)}</div>
                        <div class="metric-label">Udemy Courses</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">⭐</div>
                        <div class="metric-value">{exercism_stats.get('reputation', 0)}</div>
                        <div class="metric-label">Exercism Rep</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">✅</div>
                        <div class="metric-value">{exercism_stats.get('total_solutions', 0)}</div>
                        <div class="metric-label">Code Solutions</div>
                    </div>
                </div>
                <p class="block-story">
                    Non smetto mai di imparare. Tra Udemy, Exercism e altre piattaforme, dedico tempo ogni settimana 
                    per migliorare le mie competenze in nuove tecnologie, linguaggi e paradigmi di programmazione.
                </p>
            </div>
        </div>
        
        <!-- Productivity -->
        <div class="story-block productivity-block">
            <div class="block-header">
                <h3>✅ Produttività e Organizzazione</h3>
                <span class="block-badge">Task Master</span>
            </div>
            <div class="block-content">
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-icon">📋</div>
                        <div class="metric-value">{rtm_stats.get('total_tasks', 0)}</div>
                        <div class="metric-label">Total Tasks</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">🎯</div>
                        <div class="metric-value">{rtm_stats.get('active_tasks', 0)}</div>
                        <div class="metric-label">Active Now</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">✨</div>
                        <div class="metric-value">{rtm_stats.get('completed_tasks', 0)}</div>
                        <div class="metric-label">Completed</div>
                    </div>
                </div>
                <p class="block-story">
                    Gestisco ogni aspetto della mia vita con sistemi organizzati. Remember The Milk mi aiuta a 
                    mantenere il focus su ciò che conta, completando costantemente task e raggiungendo obiettivi.
                </p>
            </div>
        </div>
        
        <!-- Life Philosophy -->
        <div class="story-block philosophy-block">
            <div class="block-header">
                <h3>🎯 La Mia Filosofia</h3>
            </div>
            <div class="block-content philosophy-content">
                <div class="philosophy-item">
                    <span class="philosophy-icon">💡</span>
                    <p><strong>Data-Driven:</strong> Misuro, analizzo e ottimizzocostantemente ogni aspetto della mia vita.</p>
                </div>
                <div class="philosophy-item">
                    <span class="philosophy-icon">🔄</span>
                    <p><strong>Continuous Improvement:</strong> Ogni giorno è un'opportunità per imparare qualcosa di nuovo.</p>
                </div>
                <div class="philosophy-item">
                    <span class="philosophy-icon">🤝</span>
                    <p><strong>Knowledge Sharing:</strong> Condivido ciò che imparo per far crescere la community.</p>
                </div>
                <div class="philosophy-item">
                    <span class="philosophy-icon">⚖️</span>
                    <p><strong>Work-Life Balance:</strong> Alta produttività senza sacrificare salute e benessere.</p>
                </div>
            </div>
        </div>
        
        <!-- Call to Action -->
        <div class="story-cta">
            <h3>Lavoriamo Insieme</h3>
            <p>Se cerchi un professionista che unisce competenza tecnica, passione per l'apprendimento 
            e attenzione al benessere, parliamone!</p>
            <div class="cta-buttons">
                <a href="{profile.get('cal_link', '#')}" class="btn btn-primary" target="_blank">📅 Prenota una Call</a>
                <a href="https://www.linkedin.com/in/stanzinofree/" class="btn btn-outline" target="_blank">💼 LinkedIn</a>
                <a href="https://cv.middei.info" class="btn btn-outline" target="_blank">📄 CV</a>
            </div>
        </div>
        """
        
        return HTMLResponse(content=html)
        
    except Exception as e:
        return HTMLResponse(
            content=f"<p>Error loading about page: {str(e)}</p>",
            status_code=500
        )

@app.get("/api/monitoring")
async def get_monitoring():
    """
    Returns monitoring data for all scrapers with execution history and stats
    """
    import sqlite3
    from datetime import datetime, timedelta
    
    db_path = Path("/app/data/kapihome.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        monitoring_data = {
            "last_updated": datetime.now().isoformat(),
            "scrapers": {}
        }
        
        # RTM Scraper Stats
        cursor.execute("""
            SELECT timestamp, total_tasks, active_tasks, overdue_tasks 
            FROM rtm_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        rtm_last = cursor.fetchone()
        
        cursor.execute("""
            SELECT timestamp, total_tasks, active_tasks, overdue_tasks 
            FROM rtm_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        rtm_history = cursor.fetchall()
        
        monitoring_data["scrapers"]["rtm"] = {
            "name": "Remember The Milk",
            "last_execution": rtm_last[0] if rtm_last else None,
            "status": "active" if rtm_last else "no_data",
            "current_stats": {
                "total_tasks": rtm_last[1] if rtm_last else 0,
                "active_tasks": rtm_last[2] if rtm_last else 0,
                "overdue_tasks": rtm_last[3] if rtm_last else 0
            } if rtm_last else {},
            "history": [
                {
                    "timestamp": row[0],
                    "total_tasks": row[1],
                    "active_tasks": row[2],
                    "overdue_tasks": row[3]
                }
                for row in rtm_history
            ]
        }
        
        # LinkedIn Scraper Stats
        cursor.execute("""
            SELECT timestamp, followers, post_impressions_7d, profile_views_90d, search_appearances_7d 
            FROM linkedin_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        linkedin_last = cursor.fetchone()
        
        cursor.execute("""
            SELECT timestamp, followers, post_impressions_7d, profile_views_90d, search_appearances_7d 
            FROM linkedin_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        linkedin_history = cursor.fetchall()
        
        monitoring_data["scrapers"]["linkedin"] = {
            "name": "LinkedIn",
            "last_execution": linkedin_last[0] if linkedin_last else None,
            "status": "active" if linkedin_last else "no_data",
            "current_stats": {
                "followers": linkedin_last[1] if linkedin_last else 0,
                "post_impressions_7d": linkedin_last[2] if linkedin_last else 0,
                "profile_views_90d": linkedin_last[3] if linkedin_last else 0,
                "search_appearances_7d": linkedin_last[4] if linkedin_last else 0
            } if linkedin_last else {},
            "history": [
                {
                    "timestamp": row[0],
                    "followers": row[1],
                    "post_impressions_7d": row[2],
                    "profile_views_90d": row[3],
                    "search_appearances_7d": row[4]
                }
                for row in linkedin_history
            ]
        }
        
        # GitHub Scraper Stats
        cursor.execute("""
            SELECT timestamp, public_repos, total_stars, contributions_last_year, current_streak 
            FROM github_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        github_last = cursor.fetchone()
        
        cursor.execute("""
            SELECT timestamp, public_repos, total_stars, contributions_last_year, current_streak 
            FROM github_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        github_history = cursor.fetchall()
        
        monitoring_data["scrapers"]["github"] = {
            "name": "GitHub",
            "last_execution": github_last[0] if github_last else None,
            "status": "active" if github_last else "no_data",
            "current_stats": {
                "public_repos": github_last[1] if github_last else 0,
                "total_stars": github_last[2] if github_last else 0,
                "contributions_last_year": github_last[3] if github_last else 0,
                "current_streak": github_last[4] if github_last else 0
            } if github_last else {},
            "history": [
                {
                    "timestamp": row[0],
                    "public_repos": row[1],
                    "total_stars": row[2],
                    "contributions_last_year": row[3],
                    "current_streak": row[4]
                }
                for row in github_history
            ]
        }
        
        # Exercism Scraper Stats
        cursor.execute("""
            SELECT timestamp, reputation, total_badges, total_solutions, total_tracks 
            FROM exercism_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        exercism_last = cursor.fetchone()
        
        cursor.execute("""
            SELECT timestamp, reputation, total_badges, total_solutions, total_tracks 
            FROM exercism_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        exercism_history = cursor.fetchall()
        
        monitoring_data["scrapers"]["exercism"] = {
            "name": "Exercism",
            "last_execution": exercism_last[0] if exercism_last else None,
            "status": "active" if exercism_last else "no_data",
            "current_stats": {
                "reputation": exercism_last[1] if exercism_last else 0,
                "total_badges": exercism_last[2] if exercism_last else 0,
                "total_solutions": exercism_last[3] if exercism_last else 0,
                "total_tracks": exercism_last[4] if exercism_last else 0
            } if exercism_last else {},
            "history": [
                {
                    "timestamp": row[0],
                    "reputation": row[1],
                    "total_badges": row[2],
                    "total_solutions": row[3],
                    "total_tracks": row[4]
                }
                for row in exercism_history
            ]
        }
        
        # Udemy Scraper Stats
        cursor.execute("""
            SELECT timestamp, total_courses, completed_courses, in_progress_courses, weekly_streak 
            FROM udemy_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        udemy_last = cursor.fetchone()
        
        cursor.execute("""
            SELECT timestamp, total_courses, completed_courses, in_progress_courses, weekly_streak 
            FROM udemy_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        udemy_history = cursor.fetchall()
        
        monitoring_data["scrapers"]["udemy"] = {
            "name": "Udemy",
            "last_execution": udemy_last[0] if udemy_last else None,
            "status": "active" if udemy_last else "no_data",
            "current_stats": {
                "total_courses": udemy_last[1] if udemy_last else 0,
                "completed_courses": udemy_last[2] if udemy_last else 0,
                "in_progress_courses": udemy_last[3] if udemy_last else 0,
                "weekly_streak": udemy_last[4] if udemy_last else 0
            } if udemy_last else {},
            "history": [
                {
                    "timestamp": row[0],
                    "total_courses": row[1],
                    "completed_courses": row[2],
                    "in_progress_courses": row[3],
                    "weekly_streak": row[4]
                }
                for row in udemy_history
            ]
        }
        
        # Welltory Health Stats
        cursor.execute("""
            SELECT timestamp, stress, energy, hrv, mood 
            FROM welltory_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        welltory_last = cursor.fetchone()
        
        cursor.execute("""
            SELECT timestamp, stress, energy, hrv, mood 
            FROM welltory_stats_history 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        welltory_history = cursor.fetchall()
        
        # Calculate health score for current stats
        welltory_score = None
        if welltory_last:
            welltory_current = {
                "current": {
                    "stress": welltory_last[1],
                    "energy": welltory_last[2],
                    "hrv": welltory_last[3],
                    "mood": welltory_last[4]
                }
            }
            welltory_score = calculate_health_score(welltory_current)
        
        monitoring_data["scrapers"]["welltory"] = {
            "name": "Welltory Health",
            "last_execution": welltory_last[0] if welltory_last else None,
            "status": "active" if welltory_last else "no_data",
            "current_stats": {
                "health_score": welltory_score.get('score') if welltory_score else 0,
                "stress": welltory_last[1] if welltory_last else None,
                "energy": welltory_last[2] if welltory_last else None,
                "hrv": welltory_last[3] if welltory_last else None,
                "mood": welltory_last[4] if welltory_last else None
            } if welltory_last else {},
            "history": [
                {
                    "timestamp": row[0],
                    "stress": row[1],
                    "energy": row[2],
                    "hrv": row[3],
                    "mood": row[4]
                }
                for row in welltory_history
            ]
        }
        
        conn.close()
        
        return JSONResponse(content=monitoring_data)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error loading monitoring data: {str(e)}"}
        )
