"""
Progress tracking callbacks for CrewAI agents
"""

from crewai.agent import BaseCallbackHandler
from datetime import datetime
import time


class VerboseProgressCallback(BaseCallbackHandler):
    """Callback to show detailed progress during agent execution"""
    
    def __init__(self):
        self.start_time = time.time()
        self.agent_start_times = {}
        self.task_start_times = {}
    
    def on_agent_start(self, agent, task):
        """Called when an agent starts working on a task"""
        current_time = datetime.now().strftime('%H:%M:%S')
        elapsed = time.time() - self.start_time
        self.agent_start_times[agent.role] = time.time()
        
        print(f"\n🤖 [{current_time}] Agent '{agent.role}' started working")
        print(f"📋 Task: {task.description[:100]}...")
        print(f"⏱️  Elapsed: {elapsed:.1f}s")
    
    def on_agent_finish(self, agent, result):
        """Called when an agent finishes"""
        current_time = datetime.now().strftime('%H:%M:%S')
        agent_duration = time.time() - self.agent_start_times.get(agent.role, time.time())
        
        print(f"\n✅ [{current_time}] Agent '{agent.role}' completed task")
        print(f"⏱️  Agent duration: {agent_duration:.1f}s")
        print(f"📝 Result length: {len(str(result))} characters")
    
    def on_tool_start(self, tool, input_data):
        """Called when a tool is used"""
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"\n🔧 [{current_time}] Using tool: {tool}")
        print(f"📥 Input: {str(input_data)[:150]}...")
    
    def on_tool_end(self, tool, output):
        """Called when a tool finishes"""
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"✅ [{current_time}] Tool '{tool}' completed")
        print(f"📤 Output length: {len(str(output))} characters")
    
    def on_task_start(self, task):
        """Called when a task starts"""
        current_time = datetime.now().strftime('%H:%M:%S')
        self.task_start_times[task.description[:50]] = time.time()
        print(f"\n📋 [{current_time}] Starting task: {task.description[:100]}...")
    
    def on_task_complete(self, task, result):
        """Called when a task completes"""
        current_time = datetime.now().strftime('%H:%M:%S')
        task_key = task.description[:50]
        task_duration = time.time() - self.task_start_times.get(task_key, time.time())
        
        print(f"\n🎯 [{current_time}] Task completed!")
        print(f"⏱️  Task duration: {task_duration:.1f}s")
        print(f"📄 Result preview: {str(result)[:200]}...")


class SimpleProgressCallback:
    """Simple progress indicator"""
    
    def __init__(self):
        self.start_time = time.time()
        self.last_update = time.time()
    
    def show_progress(self):
        """Show a simple progress indicator"""
        current_time = time.time()
        if current_time - self.last_update > 30:  # Update every 30 seconds
            elapsed = current_time - self.start_time
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"⏳ [{timestamp}] Still working... (elapsed: {elapsed:.0f}s)")
            self.last_update = current_time
