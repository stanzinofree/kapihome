"""
Remember The Milk Scraper
Authenticates with RTM API and fetches tasks data using rtmilk 3.0.5
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from rtmilk import API
    HAS_RTM = True
except ImportError:
    HAS_RTM = False
    API = None


class RTMScraper:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = None
        self.token_file = Path("/app/data/.rtm_token")
    
    def authenticate(self) -> bool:
        """Authenticate with RTM API - requires token file from rtm_auth.py"""
        if not HAS_RTM:
            print("  ✗ rtmilk library not available")
            return False
        
        try:
            # Check if token file exists
            if not self.token_file.exists():
                print("  ⚠ RTM token not found")
                print("  → Run authentication first: docker exec -it kapihome-scrapers python rtm_auth.py")
                return False
            
            # Load existing token
            with open(self.token_file, 'r') as f:
                token = f.read().strip()
            print("  → Using saved RTM token")
            
            # Create API client with existing token
            self.client = API(
                apiKey=self.api_key,
                sharedSecret=self.api_secret,
                token=token
            )
            
            print("  ✓ RTM authentication successful")
            return True
        
        except Exception as e:
            print(f"  ✗ RTM authentication failed: {e}")
            return False
    
    def fetch_tasks(self) -> Dict[str, Any]:
        """Fetch all tasks from RTM"""
        if not self.client:
            raise RuntimeError("RTM client not initialized. Call authenticate() first.")
        
        try:
            print("  → Fetching tasks from RTM...")
            
            # Get all lists
            lists_response = self.client.ListsGetList()
            lists_data = []
            
            for lst in lists_response.lists.list:
                if hasattr(lst, 'smart') and lst.smart == '1':
                    continue  # Skip smart lists
                lists_data.append({
                    'id': lst.id,
                    'name': lst.name,
                    'task_count': 0  # Will update this below
                })
            
            # Get all tasks
            print("  → Calling TasksGetList()...")
            tasks_response = self.client.TasksGetList()
            print("  → TasksGetList() completed")
            
            all_tasks = []
            active_tasks = []
            upcoming_tasks = []
            overdue_tasks = []
            completed_tasks = []
            
            today = datetime.now().date()
            week_from_now = today + timedelta(days=7)
            
            # Parse tasks
            if hasattr(tasks_response, 'tasks') and hasattr(tasks_response.tasks, 'list'):
                for task_list in tasks_response.tasks.list:
                    # Skip if no taskseries or taskseries is None
                    if not hasattr(task_list, 'taskseries') or task_list.taskseries is None:
                        continue
                    
                    # Handle both single taskseries and list of taskseries
                    taskseries_list = task_list.taskseries if isinstance(task_list.taskseries, list) else [task_list.taskseries]
                    
                    for task_series in taskseries_list:
                        if not hasattr(task_series, 'task'):
                            continue
                        
                        for task in task_series.task:
                            # Get list name
                            list_name = 'Inbox'
                            for lst in lists_data:
                                if lst['id'] == task_list.id:
                                    list_name = lst['name']
                                    break
                            
                            # Parse tags
                            tags = []
                            if hasattr(task_series, 'tags'):
                                if isinstance(task_series.tags, list):
                                    tags = task_series.tags
                                elif hasattr(task_series.tags, 'tag'):
                                    if isinstance(task_series.tags.tag, list):
                                        tags = task_series.tags.tag
                                    else:
                                        tags = [task_series.tags.tag]
                            
                            # Parse due date (datetime object)
                            due_date = ''
                            if hasattr(task, 'due') and task.due:
                                if isinstance(task.due, datetime):
                                    due_date = task.due.isoformat()
                                else:
                                    due_date = str(task.due)
                            
                            # Check if completed
                            is_completed = hasattr(task, 'completed') and task.completed is not None
                            
                            # Parse priority (enum value)
                            priority = 'N'
                            if hasattr(task, 'priority'):
                                priority = task.priority.value if hasattr(task.priority, 'value') else str(task.priority)
                            
                            task_data = {
                                'id': str(task.id),
                                'name': task_series.name,
                                'due_date': due_date,
                                'priority': priority,
                                'list': list_name,
                                'tags': tags,
                                'has_notes': hasattr(task_series, 'notes') and task_series.notes,
                                'completed': is_completed
                            }
                            
                            all_tasks.append(task_data)
                            
                            # Update list task count
                            for lst in lists_data:
                                if lst['name'] == list_name:
                                    lst['task_count'] += 1
                                    break
                            
                            # Categorize tasks
                            if is_completed:
                                completed_tasks.append(task_data)
                            elif due_date:
                                try:
                                    # Parse RTM date format (YYYY-MM-DDTHH:MM:SSZ)
                                    due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                                    due_date_only = due_datetime.date()
                                    
                                    if due_date_only < today:
                                        overdue_tasks.append(task_data)
                                    elif due_date_only == today:
                                        active_tasks.append(task_data)
                                    elif due_date_only <= week_from_now:
                                        upcoming_tasks.append(task_data)
                                    else:
                                        active_tasks.append(task_data)
                                except:
                                    active_tasks.append(task_data)
                            else:
                                active_tasks.append(task_data)
            
            # Calculate statistics
            stats = {
                'total_tasks': len([t for t in all_tasks if not t['completed']]),
                'active_tasks': len(active_tasks),
                'completed_this_week': len(completed_tasks),  # Simplified
                'completed_this_month': len(completed_tasks),  # Simplified
                'overdue_tasks': len(overdue_tasks),
                'due_today': len([t for t in active_tasks if t['due_date'] and 
                                  datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')).date() == today]),
                'due_this_week': len(upcoming_tasks)
            }
            
            result = {
                'stats': stats,
                'active_tasks': sorted(active_tasks, key=lambda x: (x['priority'] != '1', x['due_date']))[:10],
                'upcoming_tasks': sorted(upcoming_tasks, key=lambda x: x['due_date'])[:10],
                'overdue_tasks': sorted(overdue_tasks, key=lambda x: x['due_date']),
                'lists': sorted(lists_data, key=lambda x: -x['task_count']),
                'extracted_at': datetime.now().isoformat()
            }
            
            print(f"  ✓ Fetched {len(all_tasks)} total tasks ({stats['total_tasks']} active) from RTM")
            return result
        
        except Exception as e:
            print(f"  ✗ Error fetching RTM tasks: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def scrape(self, output_file: str = "/app/data_tmp/rtm.json") -> bool:
        """Main scrape method - authenticate and fetch data"""
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Starting RTM scrape...")
            
            # Authenticate
            if not self.authenticate():
                return False
            
            # Fetch tasks
            data = self.fetch_tasks()
            
            # Save to file
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"  ✓ RTM data saved to {output_file}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ RTM scrape completed")
            return True
        
        except Exception as e:
            print(f"  ✗ RTM scrape failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # Test scraper
    api_key = os.getenv('RTM_API_KEY')
    api_secret = os.getenv('RTM_API_SECRET')
    
    if not api_key or not api_secret:
        print("Error: RTM_API_KEY and RTM_API_SECRET environment variables required")
        exit(1)
    
    scraper = RTMScraper(api_key=api_key, api_secret=api_secret)
    success = scraper.scrape()
    
    if success:
        print("✓ RTM scraper test successful")
    else:
        print("✗ RTM scraper test failed")
