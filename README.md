# 🐋 OrcasAI - Pod-Based AI Agent Coordination System

**Built on CrewAI** - A YAML-based system for managing groups of AI agents that work together like orcas in pods.

*This tool is built on top of [CrewAI](https://crewai.com/), an open-source framework for orchestrating role-playing, autonomous AI agents.*

## 🌊 What is OrcasAI?

OrcasAI is inspired by how orcas work together in pods. Just like orcas coordinate to accomplish complex tasks, this system organizes AI agents into specialized groups called "pods" to handle different challenges.

OrcasAI provides a simple YAML configuration layer on top of CrewAI, making it easy to create and manage agent teams without writing code.

### Key Features

- **🐋 Pod Architecture**: Groups of AI agents working together
- **🔧 Tool Management**: Enable/disable tools per pod
- **📁 YAML Configuration**: Each pod defined in a simple YAML file
- **🎯 CLI Interface**: Command-line interface for running pods
- **🔄 Flexible Inputs**: Pass different parameters to each pod
- **🧠 LLM Support**: Configure different language models per pod

## 🗂️ Project Structure

```
orkasai/
├── pods/                     # Individual pod configurations
│   ├── content_creation.yaml # Content creation pod
│   ├── code_development.yaml # Software development pod
│   └── research_analysis.yaml# Research & analysis pod
├── tools.yaml               # Global tool registry
├── orcasai.py              # Main CLI interface
├── orca_pod_runner.py      # Core pod management framework
├── custom_tools.py         # Custom tool implementations
├── setup.sh                # Linux/macOS setup script
├── setup.bat               # Windows setup script
└── requirements.txt        # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Python 3.9+ recommended)

### Method 1: Automated Setup (Recommended)

**For Linux/macOS:**
```bash
git clone <your-repo-url>
cd orkasai
./setup.sh
```

**For Windows:**
```cmd
git clone <your-repo-url>
cd orkasai
setup.bat
```

### Method 2: Manual Setup

**1. Clone and Navigate:**
```bash
git clone <your-repo-url>
cd orkasai
```

**2. Create Virtual Environment:**
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install Dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Install LLM Backend

**Install Ollama (Recommended for local AI):**

**For macOS:**
```bash
# Option A: Download from website (recommended)
# Visit https://ollama.ai and download the macOS app

# Option B: Using Homebrew
brew install ollama

# Start Ollama service
ollama serve  # or it starts automatically with the app
```

**For Linux:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

**For Windows:**
```cmd
# Download and install from https://ollama.ai
# The installer will set up everything automatically
```

**Pull AI Models:**
```bash
# Recommended models (choose based on your hardware)
ollama pull llama3.2        # 3B parameters (fast, good for testing)
ollama pull llama3.1        # 8B parameters (better quality, slower)
ollama pull codellama       # Specialized for code development pod

# Optional: Larger models (require more RAM)
ollama pull llama3.1:70b    # 70B parameters (excellent quality, needs 64GB+ RAM)
```

### Optional: Install Web UI for Model Management

```bash
# Activate your virtual environment first!
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

pip install open-webui
open-webui serve
```

Then visit http://localhost:8080 in your browser.

## 🎯 Usage

**Important: Always activate your virtual environment first!**

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 1. List Available Pods

```bash
python orcasai.py list
```

### 2. Get Pod Information

```bash
python orcasai.py info content_creation
```

### 3. Deploy a Pod

```bash
# Content creation pod
python orcasai.py run content_creation --topic "AI in Healthcare"

# Code development pod  
python orcasai.py run code_development --project "REST API with authentication"

# Research pod
python orcasai.py run research_analysis --topic "Market trends in AI tools"
```

### 4. Interactive Mode

```bash
python orcasai.py interactive
```

### 5. Custom Pod Directory

```bash
python orcasai.py list --pods-dir=my_custom_pods --tools-config=my_tools.yaml
```

## 📝 Pod Configuration Format

Each pod is defined in its own YAML file in the `pods/` directory:

```yaml
name: "Your Pod Name"
description: "What this pod accomplishes"

# LLM Configuration
llm:
  model: "ollama/llama3.2"
  base_url: "http://localhost:11434"
  temperature: 0.7
  max_tokens: 2048

# Agents in this pod
agents:
  agent_name:
    role: "Role description"
    goal: "What this agent aims to achieve"
    backstory: "Background story for this agent"
    tools: ["tool1", "tool2"]
    allow_delegation: false
    verbose: true

# Tasks
tasks:
  task_name:
    description: "Detailed task description with {topic} placeholder"
    expected_output: "What output is expected"
    agent: "agent_name"

# Mission workflow
workflow:
  tasks: ["task1", "task2", "task3"]
  verbose: true

# Tools enabled for this pod
tools:
  enabled: ["search_tool", "scrape_tool"]
  disabled: []

# Input parameters
inputs:
  required:
    - name: "topic"
      description: "Main topic"
  optional:
    - name: "style"
      description: "Content style preference"
```

## 🔧 Tool Configuration

Tools are defined globally in `tools.yaml`:

```yaml
tools:
  search_tool:
    module: "crewai_tools"
    class: "SerperDevTool"
    config:
      # Configure as needed

  custom_analysis_tool:
    module: "custom_tools"
    class: "DataAnalysisTool"
    config:
      max_rows: 1000
```

## 🛠️ Creating Custom Pods

1. **Create a new YAML file** in the `pods/` directory
2. **Define your orcas** with their roles, goals, and backstories
3. **Set up the mission workflow** with coordinated tasks
4. **Configure tools** needed for the mission
5. **Test your pod** with the CLI

Example minimal pod:

```yaml
name: "Simple Test Pod"
description: "A basic pod for testing agent coordination"

agents:
  test_agent:
    role: "Test Specialist"
    goal: "Validate system functionality"
    backstory: "An experienced agent focused on quality assurance"
    tools: []

tasks:
  test_task:
    description: "Perform a simple test with topic: {topic}"
    expected_output: "A brief test result summary"
    agent: "test_agent"

workflow:
  tasks: ["test_task"]

inputs:
  required:
    - name: "topic"
      description: "Test topic"
```

## 🔌 Custom Tools

Add custom tools to `custom_tools.py`:

```python
from crewai_tools import BaseTool

class YourCustomTool(BaseTool):
    name: str = "Your Tool Name"
    description: str = "What your tool does"
    
    def _run(self, argument: str) -> str:
        # Your tool logic here
        return "Tool result"
```

Then register in `tools.yaml`:

```yaml
tools:
  your_tool:
    module: "custom_tools"
    class: "YourCustomTool"
```

## 📋 CLI Reference

```bash
# List all pods
python orcasai.py list

# Get pod details
python orcasai.py info <pod_name>

# Run a pod
python orcasai.py run <pod_name> [options]

# Interactive mode
python orcasai.py interactive

# Custom directories
python orcasai.py --pods-dir=custom_pods --tools-config=custom_tools.yaml list
```

### CLI Options

- `--pods-dir`: Directory containing pod YAML files (default: `pods`)
- `--tools-config`: Tools configuration file (default: `tools.yaml`)
- `--topic`: Topic for content/research pods
- `--project`: Project description for development pods
- `--input KEY VALUE`: Additional input parameters (can be used multiple times)

## 🐋 The Orca Philosophy

Real orcas are intelligent marine mammals known for:

- **Pod Coordination**: Working together in groups
- **Communication**: Complex vocalizations for coordination
- **Specialized Roles**: Different orcas take on different roles
- **Adaptive Intelligence**: Adjusting strategies based on the situation
- **Collective Success**: Achieving goals no single orca could accomplish alone

OrcasAI applies these principles to AI agent coordination, where each "agent" has specialized skills and works together with others in the pod to accomplish complex tasks.

## 🙏 Credits

This project is built on top of [CrewAI](https://crewai.com/), an excellent open-source framework for orchestrating role-playing, autonomous AI agents. CrewAI provides the core agent coordination capabilities, while OrcasAI adds a simplified YAML-based configuration layer.