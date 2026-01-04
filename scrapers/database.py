"""
Database module for storing historical data
Stores snapshots of all metrics for time-series analysis
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class KapiHomeDB:
    def __init__(self, db_path: str = "/app/data/kapihome.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # RTM Stats History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rtm_stats_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_tasks INTEGER,
                active_tasks INTEGER,
                completed_this_week INTEGER,
                completed_this_month INTEGER,
                overdue_tasks INTEGER,
                due_today INTEGER,
                due_this_week INTEGER
            )
        """)
        
        # RTM Tasks Snapshot
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rtm_tasks_snapshot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                task_id TEXT,
                task_name TEXT,
                due_date TEXT,
                priority TEXT,
                list_name TEXT,
                tags TEXT,
                status TEXT,
                completed_at TEXT
            )
        """)
        
        # LinkedIn Stats History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_stats_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                followers INTEGER,
                post_impressions_7d INTEGER,
                profile_views_90d INTEGER,
                search_appearances_7d INTEGER
            )
        """)
        
        # GitHub Stats History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS github_stats_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                public_repos INTEGER,
                total_stars INTEGER,
                total_forks INTEGER,
                followers INTEGER,
                contributions_last_year INTEGER,
                current_streak INTEGER
            )
        """)
        
        # Exercism Stats History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercism_stats_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                reputation INTEGER,
                total_badges INTEGER,
                total_solutions INTEGER,
                total_tracks INTEGER
            )
        """)
        
        # Udemy Stats History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS udemy_stats_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_courses INTEGER,
                completed_courses INTEGER,
                in_progress_courses INTEGER,
                weekly_minutes_current INTEGER,
                weekly_streak INTEGER,
                visits_this_week INTEGER
            )
        """)
        
        # Welltory Health Stats History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS welltory_stats_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                stress REAL,
                energy REAL,
                productivity REAL,
                hrv REAL,
                resting_heart_rate REAL,
                sleep_quality REAL,
                mood REAL
            )
        """)
        
        # Generic metrics for extensibility
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                metric_name TEXT,
                metric_value REAL,
                metric_metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"✓ Database initialized at {self.db_path}")
    
    def save_rtm_stats(self, stats: Dict[str, Any]):
        """Save RTM statistics snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO rtm_stats_history 
            (total_tasks, active_tasks, completed_this_week, completed_this_month, 
             overdue_tasks, due_today, due_this_week)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            stats.get('total_tasks', 0),
            stats.get('active_tasks', 0),
            stats.get('completed_this_week', 0),
            stats.get('completed_this_month', 0),
            stats.get('overdue_tasks', 0),
            stats.get('due_today', 0),
            stats.get('due_this_week', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def save_rtm_tasks(self, tasks: List[Dict[str, Any]]):
        """Save RTM tasks snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        for task in tasks:
            cursor.execute("""
                INSERT INTO rtm_tasks_snapshot
                (timestamp, task_id, task_name, due_date, priority, list_name, tags, status, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                task.get('id', ''),
                task.get('name', ''),
                task.get('due_date', ''),
                task.get('priority', ''),
                task.get('list', ''),
                json.dumps(task.get('tags', [])),
                task.get('status', 'active'),
                task.get('completed_at', '')
            ))
        
        conn.commit()
        conn.close()
    
    def save_linkedin_stats(self, stats: Dict[str, Any]):
        """Save LinkedIn statistics snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO linkedin_stats_history
            (followers, post_impressions_7d, profile_views_90d, search_appearances_7d)
            VALUES (?, ?, ?, ?)
        """, (
            stats.get('followers', 0),
            stats.get('post_impressions_7d', 0),
            stats.get('profile_views_90d', 0),
            stats.get('search_appearances_7d', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def save_github_stats(self, stats: Dict[str, Any]):
        """Save GitHub statistics snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO github_stats_history
            (public_repos, total_stars, total_forks, followers, contributions_last_year, current_streak)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            stats.get('public_repos', 0),
            stats.get('total_stars', 0),
            stats.get('total_forks', 0),
            stats.get('followers', 0),
            stats.get('contributions_last_year', 0),
            stats.get('current_streak', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def save_exercism_stats(self, stats: Dict[str, Any]):
        """Save Exercism statistics snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO exercism_stats_history
            (reputation, total_badges, total_solutions, total_tracks)
            VALUES (?, ?, ?, ?)
        """, (
            stats.get('reputation', 0),
            stats.get('total_badges', 0),
            stats.get('total_solutions', 0),
            stats.get('total_tracks', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def save_udemy_stats(self, stats: Dict[str, Any]):
        """Save Udemy statistics snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO udemy_stats_history
            (total_courses, completed_courses, in_progress_courses, weekly_minutes_current, 
             weekly_streak, visits_this_week)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            stats.get('total_courses', 0),
            stats.get('completed_courses', 0),
            stats.get('in_progress_courses', 0),
            stats.get('weekly_minutes_current', 0),
            stats.get('weekly_streak', 0),
            stats.get('visits_this_week', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def save_welltory_stats(self, stats: Dict[str, Any]):
        """Save Welltory health statistics snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO welltory_stats_history
            (stress, energy, productivity, hrv, resting_heart_rate, sleep_quality, mood)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            stats.get('stress'),
            stats.get('energy'),
            stats.get('productivity'),
            stats.get('hrv'),
            stats.get('resting_heart_rate'),
            stats.get('sleep_quality'),
            stats.get('mood')
        ))
        
        conn.commit()
        conn.close()
    
    def get_rtm_stats_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get RTM stats for last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, total_tasks, active_tasks, completed_this_week, 
                   completed_this_month, overdue_tasks
            FROM rtm_stats_history
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        """, (days,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'timestamp': row[0],
                'total_tasks': row[1],
                'active_tasks': row[2],
                'completed_week': row[3],
                'completed_month': row[4],
                'overdue': row[5]
            })
        
        conn.close()
        return results
    
    def get_completion_trend(self, source: str = 'rtm', days: int = 30) -> Dict[str, Any]:
        """Get completion trend for dashboard"""
        # This will be used for the analytics dashboard
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if source == 'rtm':
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    AVG(completed_this_week) as avg_completed_week,
                    AVG(active_tasks) as avg_active
                FROM rtm_stats_history
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """, (days,))
        
        results = cursor.fetchall()
        conn.close()
        
        return {
            'labels': [r[0] for r in results],
            'completed': [r[1] for r in results],
            'active': [r[2] for r in results]
        }
