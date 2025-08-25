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
    python orcasai.py interactive --serper-api-key="your_api_key_here"
    python orcasai.py run running_trainer --topic="Marathon training" --serper-api-key="your_api_key"
"""

import argparse
import sys
import os
from pathlib import Path
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
        pod_config = self.runner.loader.pods.get(pod_name)
        if not pod_config:
            print(f"❌ Pod '{pod_name}' not found in the ocean.")
            print("\n🐋 Available pods:")
            for pod in self.runner.loader.pods.keys():
                print(f"   • {pod}")
            return
        
        # Add output configuration to inputs for agents to use
        output_config = pod_config.get('output', {})
        if output_config:
            # Add style guidelines as context for agents
            style_guidelines = output_config.get('style_guidelines', [])
            # Only use user input for language, no YAML default
            language = inputs.get('output_language')
            
            guidelines_parts = []
            if language:
                guidelines_parts.append(f"- SEARCH AND RESEARCH in English and {language} for best results")
                guidelines_parts.append(f"- THINK AND ANALYZE in English for optimal reasoning")
                guidelines_parts.append(f"- WRITE FINAL OUTPUT in {language} only")
                guidelines_parts.append(f"- Use English keywords when searching for information unless they are provided in {language}")
            if style_guidelines:
                guidelines_parts.extend([f"- {guideline}" for guideline in style_guidelines])
            
            if guidelines_parts:
                guidelines_text = "\n".join(guidelines_parts)
                inputs['_output_guidelines'] = f"""
IMPORTANT LANGUAGE AND OUTPUT REQUIREMENTS:
{guidelines_text}

PROCESS:
1. Search using English terms unless data provided in {language}
2. Think and analyze information in English 
3. Only translate the final response to the requested language
4. This ensures better search results and reasoning quality

Please follow these guidelines strictly in all your responses.
"""
        
        print(f"\n🐋 Deploying pod: {pod_name}")
        if inputs:
            # Don't show internal guidelines in the display
            display_inputs = {k: v for k, v in inputs.items() if not k.startswith('_')}
            if display_inputs:
                print(f"📝 Mission parameters: {display_inputs}")
        
        result = self.runner.run_pod(pod_name, inputs)
        
        if result:
            print(f"\n📄 Mission Results:")
            print("=" * 70)
            print(result.raw)
            
            # Handle file output if configured
            self._save_output_files(pod_name, pod_config, inputs, result)
        else:
            print("❌ Pod mission failed.")
    
    def _save_output_files(self, pod_name: str, pod_config: Dict[str, Any], inputs: Dict[str, Any], result: Any):
        """Save pod results to files based on output configuration."""
        output_config = pod_config.get('output', {})
        if not output_config:
            return
        
        try:
            # Create output folder - hardcoded path
            folder = "./results"
            Path(folder).mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            file_naming = inputs.get('file_naming', '{pod_name}_{timestamp}')
            filename = self._generate_filename(file_naming, pod_name, inputs)
            
            # Determine file extension
            file_format = output_config.get('format', 'markdown')
            extension = '.md' if file_format == 'markdown' else '.txt'
            
            filepath = Path(folder) / f"{filename}{extension}"
            
            # Format content based on configuration
            content = self._format_output_content(result.raw, output_config, pod_config)
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n💾 Results saved to: {filepath}")
            
        except Exception as e:
            print(f"⚠️  Failed to save output files: {e}")
    
    def _generate_filename(self, naming_pattern: str, pod_name: str, inputs: Dict[str, Any]) -> str:
        """Generate filename from naming pattern and inputs."""
        from datetime import datetime
        
        # Start with the pattern
        filename = naming_pattern
        
        # Replace common placeholders
        filename = filename.replace('{pod_name}', pod_name)
        filename = filename.replace('{timestamp}', datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        # Replace input placeholders
        for key, value in inputs.items():
            if not key.startswith('_'):  # Skip internal variables
                # Clean value for filename
                clean_value = str(value).replace(' ', '_').replace('/', '_')[:50]
                filename = filename.replace(f'{{{key}}}', clean_value)
        
        # Clean up any remaining brackets and invalid characters
        filename = filename.replace('{', '').replace('}', '')
        filename = ''.join(c for c in filename if c.isalnum() or c in '_-.')
        
        return filename
    
    def _format_output_content(self, raw_content: str, output_config: Dict[str, Any], pod_config: Dict[str, Any]) -> str:
        """Format output content based on configuration."""
        content_parts = []
        
        # Add header
        pod_name = pod_config.get('name', 'Pod Results')
        content_parts.append(f"# {pod_name}")
        content_parts.append(f"*Generated by OrcasAI*\n")
        
        # Add the raw content directly
        content_parts.append(raw_content)
        
        return "\n".join(content_parts)
    
    def interactive_mode(self):
        """Interactive mode for running pods."""
        print("🌊 Welcome to OrcasAI Interactive Mode!")
        print("The depths of AI coordination await...")
        
        # Check for API key if search tools are available
        if not os.environ.get('SERPER_API_KEY'):
            print("\n🔍 Search functionality requires a Serper API key")
            serper_key = input("Enter your Serper API key (or press Enter to skip): ").strip()
            if serper_key:
                os.environ['SERPER_API_KEY'] = serper_key
                print("✅ Serper API key set for this session")
        
        while True:
            print("\n" + "="*50)
            print("🐋 What would you like to do?")
            print("1. 📋 List available pods")
            print("2. ℹ️  Get pod information") 
            print("3. 🚀 Run a pod")
            print("4. 🌊 Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\n📋 Available Pods:")
                self.list_pods()
                
            elif choice == "2":
                pod_name = input("Enter pod name: ").strip()
                if pod_name:
                    self.get_pod_info(pod_name)
                else:
                    print("❌ Please enter a valid pod name")
                    
            elif choice == "3":
                print("\n📋 Available Pods:")
                self.list_pods()
                
                pod_name = input("\nEnter pod name to run: ").strip()
                if not pod_name:
                    print("❌ Please enter a valid pod name")
                    continue
                
                # Gather inputs and run the pod
                inputs = self._get_pod_inputs(pod_name)
                print(f"\n🚀 Running pod: {pod_name}")
                print("🌊 The pod is diving deep...")
                
                try:
                    result = self.runner.run_pod(pod_name, inputs)
                    print("\n✅ Pod execution completed successfully!")
                    print(f"\nResult:\n{result}")
                except Exception as e:
                    print(f"\n❌ Pod execution failed: {e}")
                    
            elif choice == "4":
                print("🌊 Returning to surface... Goodbye!")
                break
                
            else:
                try:
                    choice_num = int(choice)
                    if choice_num < 1 or choice_num > 4:
                        print("❌ Please enter a number between 1-4")
                    else:
                        print("❌ Invalid choice. Please try again.")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")
    
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
    run_parser.add_argument('--serper-api-key', help='Serper API key for search functionality')
    run_parser.add_argument('--openai-api-key', help='OpenAI API key (optional)')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Run in interactive mode')
    interactive_parser.add_argument('--serper-api-key', help='Serper API key for search functionality')
    interactive_parser.add_argument('--openai-api-key', help='OpenAI API key (optional)')
    
    args = parser.parse_args()
    
    # Set API keys as environment variables if provided
    if hasattr(args, 'serper_api_key') and args.serper_api_key:
        os.environ['SERPER_API_KEY'] = args.serper_api_key
        print("✅ Serper API key set from command line")
    if hasattr(args, 'openai_api_key') and args.openai_api_key:
        os.environ['OPENAI_API_KEY'] = args.openai_api_key
        print("✅ OpenAI API key set from command line")
    
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
