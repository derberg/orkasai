#!/usr/bin/env python3
"""
OrcasAI Pod CLI - Command Line Interface for Orca Pod Management

The perfect coordination tool for your orca pods - groups of AI agents
wor                except ValueError:
                    print("❌ Invalid input. Please enter a number.")
            
            elif choice == "4":
                print("🌊 Returning to surface... Goodbye!")
                breakher with the intelligence and teamwork of real orcas.

Usage:
    python orcasai.py list [--pods-dir=<dir>]                    # List all available pods
    python orcasai.py info <pod_name> [--pods-dir=<dir>]         # Get detailed info about a pod
    python orcasai.py run <pod_name> [options]                   # Run a pod
    python orcasai.py interactive [--pods-dir=<dir>]             # Interactive mode

Options:
    --pods-dir=<dir>     Directory containing pod YAML files (default: pods)
    --tools-config=<f>   Tools configuration file (default: tools.yaml)
    --topic=<topic>      Topic for content/research pods
    --project=<project>  Project description for development pods
    --input KEY VALUE    Additional input key-value pairs (can be used multiple times)

Examples:
    python orcasai.py list
    python orcasai.py list --pods-dir=my_custom_pods
    python orcasai.py run content_creation --topic="AI in Healthcare"
    python orcasai.py run code_development --project="E-commerce API"
    python orcasai.py run research_analysis --topic="Market trends" --input industry "Software"
    python orcasai.py interactive
"""

import argparse
import sys
from typing import Dict, Any
from orca_pod_runner import OrcaPodRunner


class OrcaCLI:
    """Command Line Interface for Orca Pods - The Pod Commander."""
    
    def __init__(self, pods_dir: str = "pods", tools_config: str = "tools.yaml"):
        self.runner = OrcaPodRunner(pods_dir, tools_config)
    
    def list_pods(self):
        """List all available pods."""
        self.runner.list_available_pods()
    
    def pod_info(self, pod_name: str):
        """Show detailed information about a specific pod."""
        info = self.runner.loader.get_pod_info(pod_name)
        
        if not info:
            print(f"❌ Pod '{pod_name}' not found.")
            return
        
        print(f"\n🐋 Pod: {info['name']}")
        print("=" * 60)
        print(f"📝 Mission: {info['description']}")
        
        print(f"\n� Orcas in this pod ({len(info['agents'])}):")
        for agent in info['agents']:
            print(f"   • {agent}")
        
        print(f"\n📋 Coordinated Tasks ({len(info['tasks'])}):")
        for task in info['tasks']:
            print(f"   • {task}")
        
        print(f"\n🔧 Available Tools ({len(info['enabled_tools'])}):")
        for tool in info['enabled_tools']:
            print(f"   • {tool}")
        
        if info['disabled_tools']:
            print(f"\n🚫 Disabled Tools ({len(info['disabled_tools'])}):")
            for tool in info['disabled_tools']:
                print(f"   • {tool}")
        
        if info['required_inputs']:
            print(f"\n📝 Required Inputs:")
            for inp in info['required_inputs']:
                print(f"   • {inp}")
        
        if info['optional_inputs']:
            print(f"\n📝 Optional Inputs:")
            for inp in info['optional_inputs']:
                print(f"   • {inp}")
    
    def run_pod(self, pod_name: str, inputs: Dict[str, Any] = None):
        """Run a specific pod."""
        if not inputs:
            inputs = {}
        
        # Check if pod exists
        if pod_name not in self.runner.loader.list_pods():
            print(f"❌ Pod '{pod_name}' not found in the ocean.")
            print("\n🐋 Available pods:")
            for pod in self.runner.loader.list_pods():
                print(f"   • {pod}")
            return
        
        print(f"\n� Deploying pod: {pod_name}")
        if inputs:
            print(f"📝 Mission parameters: {inputs}")
        
        result = self.runner.run_pod(pod_name, inputs)
        
        if result:
            print(f"\n📄 Mission Results:")
            print("=" * 70)
            print(result.raw)
        else:
            print("❌ Pod mission failed.")
    
    def interactive_mode(self):
        """Run in interactive mode."""
        print("\n🐋 OrcasAI Pod Commander - Interactive Mode")
        print("=" * 50)
        print("Welcome to the pod coordination center!")
        
        while True:
            print(f"\n🌊 Pod Commands:")
            print("  1. List available pods")
            print("  2. Show pod information")
            print("  3. Deploy pod on mission")
            print("  4. Exit to surface")
            
            choice = input("\nEnter your command (1-4): ").strip()
            
            if choice == "1":
                self.list_pods()
            
            elif choice == "2":
                pods = list(self.runner.loader.pods.keys())
                if not pods:
                    print("🐋 No pods in the ocean.")
                    continue
                
                print(f"\n🐋 Available pods:")
                for i, pod in enumerate(pods, 1):
                    print(f"   {i}. {pod}")
                
                try:
                    pod_choice = int(input(f"\nSelect pod (1-{len(pods)}): ").strip())
                    if 1 <= pod_choice <= len(pods):
                        pod_name = pods[pod_choice - 1]
                        self.pod_info(pod_name)
                    else:
                        print(f"❌ Invalid choice. Please enter 1-{len(pods)}.")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")
            
            elif choice == "3":
                pods = list(self.runner.loader.pods.keys())
                if not pods:
                    print("🐋 No pods in the ocean.")
                    continue
                
                print(f"\n🐋 Available pods:")
                for i, pod in enumerate(pods, 1):
                    print(f"   {i}. {pod}")
                
                try:
                    pod_choice = int(input(f"\nSelect pod for mission (1-{len(pods)}): ").strip())
                    if 1 <= pod_choice <= len(pods):
                        pod_name = pods[pod_choice - 1]
                        # Get inputs based on pod type
                        inputs = self._get_pod_inputs(pod_name)
                        self.run_pod(pod_name, inputs)
                    else:
                        print(f"❌ Invalid choice. Please enter 1-{len(pods)}.")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")
                
                # Get inputs based on pod type
                inputs = self._get_pod_inputs(pod_name)
                self.run_pod(pod_name, inputs)
            
            elif choice == "4":
                print("� Returning to surface... Goodbye!")
                break
            
            else:
                print("❌ Invalid command. Please enter 1-4.")
    
    def _get_pod_inputs(self, pod_name: str) -> Dict[str, Any]:
        """Get inputs for a specific pod interactively."""
        inputs = {}
        
        # Get pod configuration directly to access full input details
        pod_config = self.runner.loader.pods.get(pod_name, {})
        input_config = pod_config.get('inputs', {})
        
        if input_config.get('required'):
            print(f"\n📝 Required parameters:")
            for inp in input_config['required']:
                name = inp['name']
                description = inp.get('description', f'{name} parameter')
                example = inp.get('example', '')
                
                prompt = f"Enter {name} ({description})"
                if example:
                    prompt += f"\n   Example: {example}"
                prompt += ": "
                
                value = input(prompt).strip()
                if value:
                    inputs[name] = value
                else:
                    print(f"⚠️  {name} is required but no value provided")
        
        if input_config.get('optional'):
            print(f"\n📝 Optional parameters (press Enter to skip):")
            for inp in input_config['optional']:
                name = inp['name']
                description = inp.get('description', f'{name} parameter')
                example = inp.get('example', '')
                
                prompt = f"Enter {name} ({description}, optional)"
                if example:
                    prompt += f"\n   Example: {example}"
                prompt += ": "
                
                value = input(prompt).strip()
                if value:
                    inputs[name] = value
        
        # Allow additional custom inputs
        print(f"\n📝 Additional parameters (optional):")
        while True:
            key = input("Enter parameter name (or 'done' to finish): ").strip()
            if key.lower() == 'done':
                break
            if key:
                value = input(f"Enter value for '{key}': ").strip()
                if value:
                    inputs[key] = value
        
        return inputs


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OrcasAI Pod CLI - Coordinate your orca pods with precision",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Global options
    parser.add_argument('--pods-dir', default='pods',
                       help='Directory containing pod YAML files (default: pods)')
    parser.add_argument('--tools-config', default='tools.yaml',
                       help='Tools configuration file (default: tools.yaml)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List all available pods')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show pod information')
    info_parser.add_argument('pod_name', help='Name of the pod')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Deploy a pod on mission')
    run_parser.add_argument('pod_name', help='Name of the pod to deploy')
    run_parser.add_argument('--topic', help='Topic for content/research pods')
    run_parser.add_argument('--project', help='Project description for development pods')
    run_parser.add_argument('--input', action='append', nargs=2, metavar=('KEY', 'VALUE'),
                           help='Additional input key-value pairs (can be used multiple times)')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = OrcaCLI(args.pods_dir, args.tools_config)
    
    try:
        if args.command == 'list':
            cli.list_pods()
        
        elif args.command == 'info':
            cli.pod_info(args.pod_name)
        
        elif args.command == 'run':
            inputs = {}
            
            if args.topic:
                inputs['topic'] = args.topic
            if args.project:
                inputs['project'] = args.project
            if args.input:
                for key, value in args.input:
                    inputs[key] = value
            
            cli.run_pod(args.pod_name, inputs)
        
        elif args.command == 'interactive':
            cli.interactive_mode()
    
    except KeyboardInterrupt:
        print("\n\n� Mission interrupted by commander. Returning to surface!")
    except Exception as e:
        print(f"\n❌ Critical system error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
