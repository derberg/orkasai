"""
OrcasAI Pod Management System

This module provides a framework for loading YAML-based orca pod configurations
and executing them with CrewAI. Each pod is a specialized group of AI agents
working together like orcas in nature.

A pod of orcas works together with coordinated intelligence - that's exactly
how our AI agents collaborate to achieve complex tasks.
"""

import yaml
import importlib
from typing import Dict, List, Any, Optional
from pathlib import Path
import os
import time
from datetime import datetime, timedelta

from crewai import Agent, Task, Crew, LLM
import warnings
warnings.filterwarnings('ignore')


class ToolRegistry:
    """Registry for managing and loading tools dynamically."""
    
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, name: str, tool_config: Dict[str, Any]):
        """Register a tool from configuration."""
        try:
            module_name = tool_config['module']
            class_name = tool_config['class']
            config = tool_config.get('config', {})
            
            # Import the module
            module = importlib.import_module(module_name)
            tool_class = getattr(module, class_name)
            
            # Initialize the tool with config
            if config:
                # Handle environment variable references
                init_kwargs = {}
                for key, value in config.items():
                    if isinstance(value, str) and value.endswith('_env'):
                        # This is an environment variable reference
                        import os
                        env_var = value.replace('_env', '').upper()
                        env_value = os.getenv(env_var)
                        if env_value:
                            init_kwargs[key] = env_value
                        else:
                            print(f"⚠️  Warning: Environment variable {env_var} not set for tool {name}")
                            print(f"🔄 Switching to tool-free mode for optimal performance")
                            # Don't register the tool if required env var is missing
                            self.tools[name] = None
                            return
                    else:
                        init_kwargs[key] = value
                tool_instance = tool_class(**init_kwargs)
            else:
                tool_instance = tool_class()
            
            self.tools[name] = tool_instance
            print(f"✅ Registered tool: {name}")
            
        except Exception as e:
            print(f"❌ Failed to register tool {name}: {e}")
            print(f"🔄 Fallback: Agent will use built-in knowledge instead")
            self.tools[name] = None
    
    def get_tool(self, name: str):
        """Get a tool instance by name."""
        return self.tools.get(name)
    
    def get_tools(self, tool_names: List[str]) -> List:
        """Get multiple tools by name."""
        tools = []
        for name in tool_names:
            tool = self.get_tool(name)
            if tool is not None:
                tools.append(tool)
        return tools


class OrcaPodLoader:
    """Loads and manages orca pod configurations from separate YAML files."""
    
    def __init__(self, pods_dir: str = "pods", tools_config: str = "tools.yaml"):
        self.pods_dir = Path(pods_dir)
        self.tools_config = Path(tools_config)
        self.pods = {}
        self.tool_registry = ToolRegistry()
        self.load_tools()
        self.load_pods()
    
    def load_tools(self):
        """Load the global tools configuration."""
        try:
            with open(self.tools_config, 'r') as file:
                tools_config = yaml.safe_load(file)
            
            # Register all tools
            if 'tools' in tools_config:
                for tool_name, tool_config in tools_config['tools'].items():
                    self.tool_registry.register_tool(tool_name, tool_config)
            
            print(f"✅ Loaded tools configuration from {self.tools_config}")
            
        except FileNotFoundError:
            print(f"❌ Tools configuration file {self.tools_config} not found")
        except Exception as e:
            print(f"❌ Error loading tools configuration: {e}")
    
    def load_pods(self):
        """Load all pod configurations from the pods directory."""
        if not self.pods_dir.exists():
            print(f"❌ Pods directory {self.pods_dir} does not exist")
            return
        
        pod_files = list(self.pods_dir.glob("*.yaml")) + list(self.pods_dir.glob("*.yml"))
        
        for pod_file in pod_files:
            try:
                with open(pod_file, 'r') as file:
                    pod_config = yaml.safe_load(file)
                
                pod_name = pod_file.stem  # filename without extension
                self.pods[pod_name] = pod_config
                
                print(f"✅ Loaded pod: {pod_name} ({pod_config.get('name', 'Unnamed Pod')})")
                
            except Exception as e:
                print(f"❌ Error loading pod {pod_file}: {e}")
        
        print(f"\n🐋 Total pods loaded: {len(self.pods)}")
    
    def list_pods(self):
        """List all available pods with details."""
        if not self.pods:
            print("❌ No pods available")
            return
        
        print("\n🐋 Available Orca Pods:")
        print("=" * 60)
        
        for pod_name, pod_config in self.pods.items():
            print(f"\n📋 {pod_config.get('name', pod_name)}")
            print(f"   {pod_config.get('description', 'No description available')}")
            
            # List agents (orcas)
            agents = list(pod_config.get('agents', {}).keys())
            if agents:
                print(f"   🐋 Orcas: {', '.join(agents)}")
            
            # List tasks  
            tasks = list(pod_config.get('tasks', {}).keys())
            if tasks:
                print(f"   📋 Tasks: {', '.join(tasks)}")
            
            # List tools
            tools = pod_config.get('tools', {}).get('enabled', [])
            if tools:
                print(f"   🔧 Tools: {', '.join(tools)}")
            
            # Required inputs
            required_inputs = [inp['name'] for inp in pod_config.get('inputs', {}).get('required', [])]
            optional_inputs = [inp['name'] for inp in pod_config.get('inputs', {}).get('optional', [])]
            
            if required_inputs:
                print(f"   📝 Required: {', '.join(required_inputs)}")
            if optional_inputs:
                print(f"   📝 Optional: {', '.join(optional_inputs)}")
    
    def get_pod_info(self, pod_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific pod."""
        if pod_name not in self.pods:
            return None
        
        pod = self.pods[pod_name]
        return {
            'name': pod.get('name', pod_name),
            'description': pod.get('description', 'No description'),
            'agents': list(pod.get('agents', {}).keys()),
            'tasks': list(pod.get('tasks', {}).keys()),
            'enabled_tools': pod.get('tools', {}).get('enabled', []),
            'disabled_tools': pod.get('tools', {}).get('disabled', []),
            'required_inputs': [inp['name'] for inp in pod.get('inputs', {}).get('required', [])],
            'optional_inputs': [inp['name'] for inp in pod.get('inputs', {}).get('optional', [])]
        }
    
    def create_llm(self, pod_config: Dict[str, Any]) -> LLM:
        """Create LLM instance from pod configuration."""
        llm_config = pod_config.get('llm', {})
        
        # Set timeout environment variables for litellm
        timeout_seconds = llm_config.get('timeout', 1800)  # Default 30 minutes
        os.environ['LITELLM_TIMEOUT'] = str(timeout_seconds)
        os.environ['LITELLM_REQUEST_TIMEOUT'] = str(timeout_seconds)
        
        print(f"🕐 LLM timeout set to {timeout_seconds} seconds ({timeout_seconds//60} minutes)")
        
        return LLM(
            model=llm_config.get('model', 'ollama/llama3.2'),
            base_url=llm_config.get('base_url', 'http://localhost:11434'),
            temperature=llm_config.get('temperature', 0.7),
            max_tokens=llm_config.get('max_tokens', 2048),
            timeout=timeout_seconds  # Set timeout directly on LLM
        )
    
    def create_agents(self, pod_config: Dict[str, Any], llm: LLM) -> Dict[str, Agent]:
        """Create agents from pod configuration."""
        agents = {}
        agent_configs = pod_config.get('agents', {})
        
        for agent_name, agent_config in agent_configs.items():
            # Get tools for this agent
            tool_names = agent_config.get('tools', [])
            tools = self.tool_registry.get_tools(tool_names)
            
            agent = Agent(
                role=agent_config['role'],
                goal=agent_config['goal'],
                backstory=agent_config['backstory'],
                allow_delegation=agent_config.get('allow_delegation', False),
                verbose=agent_config.get('verbose', True),
                llm=llm,
                tools=tools
            )
            
            agents[agent_name] = agent
            print(f"✅ Created agent: {agent_name} with {len(tools)} tools")
        
        return agents
    
    def create_tasks(self, pod_config: Dict[str, Any], agents: Dict[str, Agent]) -> List[Task]:
        """Create tasks from pod configuration."""
        tasks = []
        task_configs = pod_config.get('tasks', {})
        workflow = pod_config.get('workflow', {})
        task_order = workflow.get('tasks', list(task_configs.keys()))
        
        for task_name in task_order:
            if task_name not in task_configs:
                print(f"⚠️  Task {task_name} not found in configuration")
                continue
            
            task_config = task_configs[task_name]
            agent_name = task_config['agent']
            
            if agent_name not in agents:
                print(f"⚠️  Agent {agent_name} not found for task {task_name}")
                continue
            
            task = Task(
                description=task_config['description'],
                expected_output=task_config['expected_output'],
                agent=agents[agent_name]
            )
            
            tasks.append(task)
            print(f"✅ Created task: {task_name} -> {agent_name}")
        
        return tasks
    
    def create_crew(self, pod_name: str) -> Optional[Crew]:
        """Create a complete crew from pod configuration."""
        if pod_name not in self.pods:
            print(f"❌ Pod '{pod_name}' not found")
            return None
        
        pod_config = self.pods[pod_name]
        
        print(f"\n🚀 Creating pod: {pod_config.get('name', pod_name)}")
        print(f"📝 Description: {pod_config.get('description', 'No description')}")
        
        # Create LLM
        llm = self.create_llm(pod_config)
        print(f"🧠 LLM: {llm.model}")
        
        # Create agents
        agents = self.create_agents(pod_config, llm)
        
        # Create tasks
        tasks = self.create_tasks(pod_config, agents)
        
        if not agents or not tasks:
            print("❌ Failed to create agents or tasks")
            return None
        
        # Create crew
        workflow = pod_config.get('workflow', {})
        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            verbose=workflow.get('verbose', True)
        )
        
        print(f"✅ Pod '{pod_name}' ready with {len(agents)} agents and {len(tasks)} tasks\n")
        return crew


class OrcaPodRunner:
    """Main runner for orchestrating orca pods."""
    
    def __init__(self, pods_dir: str = "pods", tools_config: str = "tools.yaml"):
        self.loader = OrcaPodLoader(pods_dir, tools_config)
    
    def list_available_pods(self):
        """List all available pods."""
        self.loader.list_pods()
    
    def get_pod_info(self, pod_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific pod."""
        return self.loader.get_pod_info(pod_name)
    
    def run_pod(self, pod_name: str, inputs: Dict[str, Any] = None) -> Optional[Any]:
        """Run a specific pod with given inputs."""
        # Start timing
        start_time = time.time()
        start_datetime = datetime.now()
        
        print(f"🐋 Pod diving into action: {pod_name}")
        print(f"🕐 Mission started at: {start_datetime.strftime('%H:%M:%S')}")
        
        crew = self.loader.create_crew(pod_name)
        
        if not crew:
            return None

        try:
            # Get pod configuration for timing estimates
            pod_config = self.loader.pods.get(pod_name, {})
            agents_count = len(pod_config.get('agents', {}))
            tasks_count = len(pod_config.get('tasks', {}))
            
            # Estimate completion time based on complexity
            estimated_minutes = self._estimate_completion_time(pod_config)
            estimated_completion = start_datetime + timedelta(minutes=estimated_minutes)
            
            print(f"📊 Mission complexity: {agents_count} agents, {tasks_count} tasks")
            print(f"⏱️  Estimated completion: {estimated_completion.strftime('%H:%M:%S')} (≈{estimated_minutes} min)")
            print(f"🌊 Dive depth: {'Deep' if agents_count > 3 else 'Standard'}")
            
            # Execute with progress tracking
            result = self._execute_with_progress_tracking(crew, inputs or {}, start_time, estimated_minutes)
            
            # Calculate final timing
            end_time = time.time()
            total_duration = end_time - start_time
            end_datetime = datetime.now()
            
            print(f"🎯 Pod mission accomplished!")
            print(f"⏰ Mission completed at: {end_datetime.strftime('%H:%M:%S')}")
            print(f"📈 Total duration: {self._format_duration(total_duration)}")
            
            # Performance summary
            if total_duration > estimated_minutes * 60:
                overtime = total_duration - (estimated_minutes * 60)
                print(f"📊 Mission took {self._format_duration(overtime)} longer than estimated")
            else:
                time_saved = (estimated_minutes * 60) - total_duration
                print(f"🚀 Mission completed {self._format_duration(time_saved)} ahead of schedule!")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"❌ Pod mission failed after {self._format_duration(duration)}: {e}")
            return None
    
    def _estimate_completion_time(self, pod_config: Dict[str, Any]) -> int:
        """Estimate completion time in minutes based on pod complexity."""
        agents_count = len(pod_config.get('agents', {}))
        tasks_count = len(pod_config.get('tasks', {}))
        enabled_tools = len(pod_config.get('tools', {}).get('enabled', []))
        
        # Base time per agent/task
        base_time = 3  # 3 minutes per agent
        tool_time = enabled_tools * 2  # 2 minutes per tool
        complexity_multiplier = 1.2 if agents_count > 5 else 1.0
        
        estimated = (agents_count * base_time + tool_time) * complexity_multiplier
        return max(5, int(estimated))  # Minimum 5 minutes
    
    def _execute_with_progress_tracking(self, crew, inputs: Dict[str, Any], start_time: float, estimated_minutes: int):
        """Execute crew with progress updates."""
        import threading
        import sys
        
        result = None
        progress_thread = None
        
        def progress_tracker():
            """Background thread to show progress updates."""
            while True:
                elapsed = time.time() - start_time
                elapsed_minutes = elapsed / 60
                
                if elapsed_minutes < estimated_minutes:
                    progress = (elapsed_minutes / estimated_minutes) * 100
                    remaining = estimated_minutes - elapsed_minutes
                    
                    sys.stdout.write(f"\r🔄 Progress: {progress:.1f}% | Elapsed: {self._format_duration(elapsed)} | Est. remaining: {remaining:.1f}min")
                    sys.stdout.flush()
                else:
                    # Beyond estimate
                    overtime = elapsed_minutes - estimated_minutes
                    sys.stdout.write(f"\r⏰ Running overtime: +{overtime:.1f}min | Total elapsed: {self._format_duration(elapsed)}")
                    sys.stdout.flush()
                
                time.sleep(30)  # Update every 30 seconds
        
        try:
            # Start progress tracking
            progress_thread = threading.Thread(target=progress_tracker, daemon=True)
            progress_thread.start()
            
            # Execute the crew
            result = crew.kickoff(inputs=inputs)
            
            # Clear progress line
            sys.stdout.write("\r" + " " * 100 + "\r")
            sys.stdout.flush()
            
        except Exception as e:
            # Clear progress line
            sys.stdout.write("\r" + " " * 100 + "\r")
            sys.stdout.flush()
            raise e
        
        return result
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}min"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def _get_crew_timing_info(self, pod_name: str) -> Dict[str, Any]:
        """Get timing information for debugging and optimization."""
        pod_config = self.loader.pods.get(pod_name, {})
        
        timing_info = {
            'pod_name': pod_name,
            'agents_count': len(pod_config.get('agents', {})),
            'tasks_count': len(pod_config.get('tasks', {})),
            'enabled_tools': list(pod_config.get('tools', {}).get('enabled', [])),
            'timeout_seconds': pod_config.get('timeout', 1800),
            'complexity_level': self._assess_complexity(pod_config)
        }
        
        return timing_info
    
    def _assess_complexity(self, pod_config: Dict[str, Any]) -> str:
        """Assess pod complexity level for timing predictions."""
        agents_count = len(pod_config.get('agents', {}))
        tools_count = len(pod_config.get('tools', {}).get('enabled', []))
        
        if agents_count == 1 and tools_count <= 2:
            return "Simple"
        elif agents_count <= 3 and tools_count <= 5:
            return "Moderate"
        elif agents_count <= 6 and tools_count <= 8:
            return "Complex"
        else:
            return "Ultra-Complex"
    
    def show_timing_summary(self, pod_name: str = None):
        """Show timing information for pods."""
        if pod_name:
            timing_info = self._get_crew_timing_info(pod_name)
            print(f"\n🐋 Pod Timing Analysis: {pod_name}")
            print(f"   Agents: {timing_info['agents_count']}")
            print(f"   Tasks: {timing_info['tasks_count']}")
            print(f"   Tools: {len(timing_info['enabled_tools'])}")
            print(f"   Timeout: {timing_info['timeout_seconds']}s ({timing_info['timeout_seconds']/60:.1f}min)")
            print(f"   Complexity: {timing_info['complexity_level']}")
            print(f"   Est. Runtime: {self._estimate_completion_time(self.loader.pods.get(pod_name, {}))} minutes")
        else:
            print("\n🐋 Available Pods Timing Overview:")
            for pod in self.loader.pods.keys():
                timing_info = self._get_crew_timing_info(pod)
                complexity_emoji = {
                    "Simple": "🟢", "Moderate": "🟡", 
                    "Complex": "🟠", "Ultra-Complex": "🔴"
                }.get(timing_info['complexity_level'], "⚪")
                print(f"   {complexity_emoji} {pod}: {timing_info['agents_count']} agents, ~{self._estimate_completion_time(self.loader.pods.get(pod, {}))}min")

    def run_with_time_tracking(self):
        """Interactive mode with enhanced timing visibility."""
        print("🐋 Welcome to OrcAI Pod Command Center!")
        print("🕐 Enhanced with real-time mission tracking\n")
        
        while True:
            # Show timing overview
            self.show_timing_summary()
            
            print("\nCommands:")
            print("  📝 'list' - Show available pods")
            print("  🕐 'timing <pod>' - Show detailed timing for specific pod")
            print("  🚀 'run <pod>' - Launch pod mission")
            print("  🚪 'exit' - Surface from depths")
            
            command = input("\n🐋 Captain's orders: ").strip().lower()
            
            if command == 'exit':
                print("🌊 Surfacing... Safe travels, Captain!")
                break
            elif command == 'list':
                self.loader.list_pods()
            elif command.startswith('timing '):
                pod_name = command[7:].strip()
                if pod_name in self.loader.pods.keys():
                    self.show_timing_summary(pod_name)
                else:
                    print(f"❌ Pod '{pod_name}' not found in fleet!")
            elif command.startswith('run '):
                pod_name = command[4:].strip()
                if pod_name in self.loader.pods.keys():
                    print(f"\n🚀 Launching {pod_name} mission...")
                    result = self.run_pod(pod_name)
                    if result:
                        print(f"\n📋 Mission Report:")
                        print(result)
                else:
                    print(f"❌ Pod '{pod_name}' not found in fleet!")
            else:
                print("❓ Unknown command. Try 'list', 'timing <pod>', 'run <pod>', or 'exit'")


# Example usage and testing functions
def main():
    """Example usage of the orca pod system."""
    runner = OrcaPodRunner()
    
    # List available pods
    runner.list_available_pods()
    
    # Example: Run the content creation pod
    inputs = {
        "topic": "Using AsyncAPI and Microcks with WebSocket protocol for automated testing"
    }
    
    result = runner.run_pod("content_creation", inputs)
    
    if result:
        print("\n📄 Result:")
        print("=" * 50)
        print(result.raw)


if __name__ == "__main__":
    main()
