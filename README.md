# Agentic Governance Suite

A comprehensive suite of AI-powered tools for enterprise governance, software development lifecycle (SDLC) management, and agent trajectory analysis. Built with Streamlit, Autogen, and Azure OpenAI.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

## 🌟 Features

### 🏛️ Governance Oversight Agents
- **CoreOps Agent**: Extract and analyze core operational metrics from conversation logs
- **Prompt Assessment Agent**: Evaluate prompt quality and effectiveness in agentic pipelines
- **Performance Agent**: Comprehensive performance analysis including latency, cost, and throughput
- **Compliance Agent**: Verify regulatory compliance (GDPR, HIPAA, SOC2, PCI-DSS)

### ⚙️ SDLC Guarding Agents
- **Technical Specs Analysis**: Review and validate technical specification documents
- **Architecture Evaluation**: Multi-agent architecture analysis with cloud platform classification
- **Code Review**: Automated code quality, security, and architecture reviews
- **Test Coverage**: Identify untested components and recommend testing strategies
- **Documentation Generation**: Automated API docs, developer guides, and architecture documentation

### 🚀 Trajectory Analysis Agents
- **Trajectory Observer**: Visualize agent interaction flows and extract performance metrics
- **Trajectory Optimizer**: Score and rank agent trajectories based on goal achievement, cost, and latency

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Main Dashboard](#main-dashboard)
  - [Governance Agents](#governance-agents)
  - [SDLC Agents](#sdlc-agents)
  - [Trajectory Agents](#trajectory-agents)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js (for Repomix integration)
- Azure OpenAI account with API access

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/shivanikabu/agentic-governance-suite.git
cd agentic-governance-suite
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Repomix (for code analysis features)**
```bash
npm install -g repomix
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```env
# Primary Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_primary_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Optional: Jury Model Configuration (for validation/evaluation)
JURY_AZURE_OPENAI_API_KEY=your_jury_api_key
JURY_AZURE_OPENAI_ENDPOINT=https://your-jury-endpoint.openai.azure.com/

# Repomix Configuration (adjust path based on your system)
REPOMIX_CLI_PATH=/path/to/repomix
```

### Environment Variables Explained

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_API_KEY` | ✅ | Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | ✅ | Your Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_VERSION` | ✅ | API version (e.g., 2024-08-01-preview) |
| `JURY_AZURE_OPENAI_API_KEY` | ❌ | Optional jury model API key |
| `JURY_AZURE_OPENAI_ENDPOINT` | ❌ | Optional jury model endpoint |

## 📖 Usage

### Main Dashboard

Launch the main Streamlit dashboard:

```bash
streamlit run main.py
```

Access the application at `http://localhost:8501`

### Governance Agents

#### CoreOps Agent

Extract operational metrics from conversation logs:

```python
import asyncio
from Governance.agents.CoreOpsAgent import start_agent_pipeline

results = asyncio.run(start_agent_pipeline(
    file_path="logs/conversation.json",
    description="Extract core metrics for monitoring"
))

# Parse JSON results
import json
metrics = json.loads(results)
print(f"Total cost: ${metrics['total_cost']}")
print(f"Total tokens: {metrics['total_tokens']}")
```

#### Prompt Assessment Agent

Analyze prompt quality:

```python
from Governance.agents.PromptAssessmentAgent import start_agent_pipeline

results = asyncio.run(start_agent_pipeline(
    file_path="logs/agent_interactions.json",
    description="Evaluate prompt effectiveness"
))
```

#### Performance Agent

Comprehensive performance analysis:

```python
from Governance.agents.PerformanceAgent import start_agent_pipeline

results = asyncio.run(start_agent_pipeline(
    file_path="logs/production.json",
    description="Identify bottlenecks and optimization opportunities"
))
```

#### Compliance Agent

Verify regulatory compliance:

```python
from Governance.agents.ComplianceAgent import start_agent_pipeline

results = asyncio.run(start_agent_pipeline(
    file_path="logs/healthcare_agents.json",
    description="HIPAA compliance verification"
))
```

### SDLC Agents

#### Technical Specs Analysis

Analyze technical specification documents:

```python
# Run from Streamlit UI or directly:
# Upload PDF → Start Analysis → View Results
```

#### Architecture Evaluation

Evaluate architecture diagrams with cloud platform classification:

```python
# Upload technical spec PDF and architecture diagram
# Multi-agent analysis:
# 1. Cloud Classification Agent → Identifies Azure/AWS/GCP
# 2. Architecture Review Agent → Analyzes with platform context
# 3. Evaluator Agent → Validates and enhances analysis
```

#### Code Review

Automated code review from GitHub repositories:

```python
# In Streamlit UI:
# 1. Enter GitHub URL: https://github.com/username/repository
# 2. Click "Run Code Review"
# 3. View comprehensive analysis covering:
#    - Architecture
#    - Security
#    - Performance
#    - Dependencies
#    - Code Quality
```

#### Test Coverage

Analyze test coverage:

```python
# Similar to Code Review, analyzes:
# - Untested components
# - Test quality
# - Additional test cases needed
# - Testing strategies
```

#### Documentation Generation

Generate comprehensive documentation:

```python
# Generates:
# - API Documentation
# - Developer Guide
# - Architecture Documentation
```

### Trajectory Agents

#### Trajectory Observer

Visualize agent interaction flows:

```python
# Upload interaction JSON → View:
# - Visual graph of agent flows
# - Trajectory paths
# - Token usage and cost per trajectory
# - Latency metrics
```

#### Trajectory Optimizer

Score and rank trajectories:

```python
# Upload interaction JSON
# Adjust weights:
# - Goal Achievement Weight
# - Cost Weight
# - Latency Weight
# View ranked trajectories with convergence scores
```

## 🏗️ Architecture

### Project Structure

```
agentic-governance-suite/
├── main.py                          # Main Streamlit dashboard
├── Governance/                     # Governance agents
│   ├── agents/
│   │   ├── CoreOpsAgent.py
│   │   ├── PromptAssessmentAgent.py
│   │   ├── PerformanceAgent.py
│   │   ├── ComplianceAgent.py
│   │   └── CustomAgent.py
│   ├── tools/
│   │   └── AgenticTools.py
│   └── st_*.py                     # Streamlit UI components
├── Auditor/                        # SDLC agents
│   ├── architecture_agent.py
│   ├── tech_specs_agent.py
│   ├── code_reviewer.py
│   ├── test_coverage.py
│   └── document_generation.py
├── Trajectory/                     # Trajectory analysis
│   ├── trajectory_observer.py
│   └── trajectory_optimizing.py
├── utils/
│   └── llm_utils.py               # LLM utility functions
├── requirements.txt
├── .env.example
└── README.md
```

### Technology Stack

- **Frontend**: Streamlit
- **AI Framework**: Autogen, LangChain
- **LLM**: Azure OpenAI GPT-4o
- **Visualization**: Graphviz, Plotly
- **Code Analysis**: Repomix
- **Document Processing**: PyMuPDF (fitz)

## 📚 API Reference

### Core Functions

#### gpt_llm_call(message)

Simple LLM call utility:

```python
from utils.llm_utils import gpt_llm_call

response = gpt_llm_call("Explain quantum computing")
print(response)
```

#### gpt_llm_call_with_config(message, temperature, max_tokens)

Enhanced LLM call with configuration:

```python
from utils.llm_utils import gpt_llm_call_with_config

response = gpt_llm_call_with_config(
    "Creative writing task",
    temperature=1.2,
    max_tokens=500
)
```

#### GPTLLMClient (Singleton Pattern)

Efficient LLM client for production:

```python
from utils.llm_utils import GPTLLMClient

client = GPTLLMClient.get_instance()
response1 = client.call("First question")
response2 = client.call("Second question")
```

## 💡 Examples

### Example 1: Production Monitoring Pipeline

```python
import asyncio
from Governance.agents.CoreOpsAgent import start_agent_pipeline as core_ops
from Governance.agents.PerformanceAgent import start_agent_pipeline as performance

async def monitor_production():
    # Extract metrics
    metrics = await core_ops(
        "logs/production.json",
        "Daily monitoring"
    )
    
    # Analyze performance
    performance_report = await performance(
        "logs/production.json",
        "Performance analysis"
    )
    
    # Send alerts if needed
    if "CRITICAL" in performance_report:
        send_alert(performance_report)

asyncio.run(monitor_production())
```

### Example 2: Compliance Audit Pipeline

```python
async def compliance_audit(log_files):
    from Governance.agents.ComplianceAgent import start_agent_pipeline
    
    results = []
    for log_file in log_files:
        result = await start_agent_pipeline(
            log_file,
            "GDPR compliance check"
        )
        results.append(result)
    
    return results

# Run audit
log_files = ["logs/q4_2024_1.json", "logs/q4_2024_2.json"]
audit_results = asyncio.run(compliance_audit(log_files))
```

### Example 3: Code Quality Pipeline

```bash
# Run complete code quality pipeline
streamlit run main.py

# Navigate to SDLC Agents → Code Evals
# Enter GitHub URL → Run Analysis
# View comprehensive report
```

### Example 4: Trajectory Optimization

```python
# Upload trajectory logs to Trajectory Optimizer
# Adjust weights based on priorities:
# - Goal Achievement: 0.5 (50%)
# - Cost Efficiency: 0.3 (30%)
# - Latency: 0.2 (20%)
# View best performing trajectory
```

## 🔧 Advanced Configuration

### Custom Agent Development

Create custom agents by extending `CustomAgent`:

```python
from Governance.agents.CustomAgent import CustomAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage

class MyCustomAgent(CustomAgent):
    async def on_messages(self, messages, cancellation_token):
        # Your custom logic here
        result = process_messages(messages)
        return Response(
            chat_message=TextMessage(
                content=result,
                source='MyCustomAgent'
            )
        )
```

### Integration with Monitoring Systems

```python
# Example: Push metrics to Datadog
async def push_to_monitoring(log_file):
    from Governance.agents.CoreOpsAgent import start_agent_pipeline
    
    metrics_json = await start_agent_pipeline(log_file, "Monitoring")
    metrics = json.loads(metrics_json)
    
    # Push to your monitoring system
    datadog_client.metric('agent.cost', metrics['total_cost'])
    datadog_client.metric('agent.tokens', metrics['total_tokens'])
    datadog_client.metric('agent.latency', metrics['average_response_time'])
```

## 🧪 Testing

Run tests:

```bash
pytest tests/
```

Run specific test suite:

```bash
pytest tests/test_governance_agents.py
pytest tests/test_sdlc_agents.py
pytest tests/test_trajectory_agents.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new features
5. Run tests: `pytest`
6. Commit changes: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature-name`
8. Submit a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions and classes
- Include type hints where applicable
- Write comprehensive comments
- Add usage examples for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Autogen](https://github.com/microsoft/autogen)
- Powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- UI built with [Streamlit](https://streamlit.io)
- Code analysis using [Repomix](https://github.com/yamadashy/repomix)

## 📧 Contact

- **Project Lead**: [Shivani Kabu]
- **Team Member**: [Nikhil Khandelwal]
- **Email**: shivani.dhar@gmail.com and nikhil.khandelwal2022@gmail.com
- **GitHub**: [@shivanikabu](https://github.com/shivanikabu)

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ Governance oversight agents
- ✅ SDLC guarding agents
- ✅ Trajectory analysis agents
- ✅ Streamlit dashboard
- ✅ Azure OpenAI integration

### Upcoming Features (v1.1)
- 🔄 Real-time monitoring dashboard
- 🔄 Webhook integration for alerts
- 🔄 Historical trend analysis
- 🔄 Multi-cloud support (AWS, GCP)
- 🔄 Custom metric definitions

### Future Plans (v2.0)
- 📋 Agent marketplace for custom agents
- 📋 Advanced visualization tools
- 📋 ML-based anomaly detection
- 📋 Cost prediction models
- 📋 Automated remediation suggestions

## 🐛 Known Issues

- Repomix path configuration may need adjustment for different OS
- Large log files (>10MB) may cause slow processing
- Graph visualization may not render properly in some browsers

See [Issues](https://github.com/shivanikabu/agentic-governance-suite/issues) for full list.

## 📊 Performance Benchmarks

| Agent Type | Avg Processing Time | Memory Usage |
|------------|---------------------|--------------|
| CoreOps | 2-3 seconds | ~200MB |
| Performance | 3-5 seconds | ~300MB |
| Compliance | 4-6 seconds | ~350MB |
| Code Review | 10-15 seconds | ~500MB |
| Architecture | 8-12 seconds | ~400MB |

*Benchmarks based on typical log files (~1MB) and repository size (~1000 files)*

## ❓ FAQ

**Q: Can I use this with other LLM providers?**  
A: Currently, only Azure OpenAI is supported. We plan to add support for other providers in future releases.

**Q: How do I handle rate limits?**  
A: The agents use temperature=0.0 for deterministic output. Implement exponential backoff in production use.

**Q: Can I run multiple agents in parallel?**  
A: Yes! All agents support async execution. See Example 2 for batch processing.

**Q: What's the cost of using these agents?**  
A: Costs depend on Azure OpenAI usage. Monitor with CoreOps Agent for detailed cost tracking.

**Q: Is this production-ready?**  
A: The toolkit is suitable for production with proper error handling and monitoring setup.

---

**Star ⭐ this repository if you find it helpful!**

For detailed documentation, visit our [Wiki](https://github.com/shivanikabu/agentic-governance-suite/wiki)
