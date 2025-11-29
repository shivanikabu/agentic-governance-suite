"""
Agentic Tools Module
===================
Provides specialized tools for AI governance and assessment across multiple dimensions:
- Core operations monitoring (tokens, costs, LLM calls)
- Compliance assessment against regulatory frameworks
- Prompt security and injection detection
- Performance evaluation against guardrails
- Agentic system description and analysis
"""

# ============================================================================
# IMPORTS
# ============================================================================
import sys
sys.path.append("../")  # Add parent directory to Python path for module imports

import base64
import io
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from Governance.genai_calls import gpt_llm_call
from Governance.agents_system_message import agent_system_messages


# ============================================================================
# AGENTIC TOOLS CLASS
# ============================================================================
class AgenticTools:
    """
    Main class containing tools for AI agent governance and assessment.
    Provides methods for operational monitoring, compliance checking,
    prompt analysis, and performance evaluation.
    """
    
    def __init__(self):
        """Initialize the AgenticTools with system messages for different agents."""
        self.system_messages = agent_system_messages

    
    # ========================================================================
    # CORE OPERATIONS PROCESSING
    # ========================================================================
    def core_ops_processing(self, file_name, description, type=None):
        """
        Analyze operational metrics of AI agents including token usage, costs,
        system messages, and LLM call statistics.
        
        Args:
            file_name: Path to JSON log file or JSON data object
            description: User-provided description of the agentic architecture
            type: 'file' if file_name is a path, None if it's already loaded data
            
        Returns:
            dict: Comprehensive operational analysis including:
                - Agent descriptions
                - Token consumption metrics
                - Cost analysis
                - System messages
                - LLM call statistics
                - Visual charts (as base64-encoded images)
        """
        # Load JSON data from file or use provided data object
        if type == 'file':
            with open(file_name, 'r', encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = file_name

        final_output = {}

        # ====================================================================
        # 1. GENERATE AGENTIC SYSTEM DESCRIPTION
        # ====================================================================
        agentic_description = self.agentic_description_tool(file_name, description, "file")
        final_output["Description:"] = agentic_description

        # ====================================================================
        # 2. IDENTIFY ALL AGENTS (EXCLUDING USER)
        # ====================================================================
        # Extract unique agent names from log entries
        # Only include entries where models_usage indicates actual API requests
        agents = set(
            entry['source'] 
            for entry in data 
            if entry['source'] != 'user' and entry['models_usage'] == "RequestUsage"
        )
        print("Agents used:", list(agents))
        final_output["List of Agents:"] = list(agents)

        # ====================================================================
        # 3. TOKEN CONSUMPTION ANALYSIS
        # ====================================================================
        # Collect token usage data for each agent
        token_data = []
        for entry in data:
            if entry['source'] != 'user' and 'prompt_tokens' in entry:
                token_data.append({
                    'Agent': entry['source'],
                    'Prompt Tokens': int(entry['prompt_tokens']),
                    'Completion Tokens': int(entry['completion_tokens']),
                    'Total Tokens': int(entry['total_tokens'])
                })

        # Create DataFrame for structured token data
        token_df = pd.DataFrame(token_data)
        print("\nTokens Consumption:")
        print(token_df)
        final_output['Tokens Consumption:'] = token_df.to_dict(orient="records")

        # Generate pie chart for token distribution across agents
        grouped_tokens = token_df.groupby('Agent')['Total Tokens'].sum()
        colors = ['#4A90E2', '#72B6E2', '#A0D1E2', '#cacdcf']
        plt.figure(figsize=(8, 6))
        plt.pie(grouped_tokens, labels=grouped_tokens.index, autopct='%1.1f%%', colors=colors)
        plt.title('Token Distribution by Agent')
        
        # Convert chart to base64-encoded image for embedding
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        final_output['Tokens Consumption by Agents:'] = (
            f"data:image/png;base64,{base64.b64encode(img_buf.getvalue()).decode('utf-8')}"
        )
        plt.close()

        # ====================================================================
        # 4. COST ANALYSIS
        # ====================================================================
        # Collect cost data for each agent
        cost_data = []
        for entry in data:
            if entry['source'] != 'user' and 'Total_Cost' in entry:
                cost_data.append({
                    'Agent': entry['source'],
                    'Total Cost ($)': float(entry['Total_Cost'].replace(' $', ''))
                })

        # Create DataFrame for structured cost data
        cost_df = pd.DataFrame(cost_data)
        print("\nCost Incurrance:")
        print(cost_df)
        final_output["Cost Incurrance:"] = cost_df.to_dict(orient="records")

        # Generate pie chart for cost distribution across agents
        grouped_costs = cost_df.groupby('Agent')['Total Cost ($)'].sum()
        colors = ['#4A90E2', '#72B6E2', '#A0D1E2', '#cacdcf']
        plt.figure(figsize=(8, 6))
        plt.pie(grouped_costs, labels=grouped_costs.index, autopct='%1.1f%%', colors=colors)
        plt.title('Cost Distribution by Agent')
        
        # Convert chart to base64-encoded image for embedding
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        final_output['Cost Incurred by Agents:'] = (
            f"data:image/png;base64,{base64.b64encode(img_buf.getvalue()).decode('utf-8')}"
        )
        plt.close()

        # ====================================================================
        # 5. EXTRACT SYSTEM MESSAGES
        # ====================================================================
        # Collect system messages for each agent (excluding user and empty messages)
        system_messages = {
            entry['source']: entry['System_Message'] 
            for entry in data 
            if entry['source'] != 'user' and entry['System_Message']
        }
        print("\nSystem Messages:")
        for agent, message in system_messages.items():
            print(f"{agent}: {message}\n")
        final_output["System Messages:"] = system_messages

        # ====================================================================
        # 6. COUNT TOTAL LLM API CALLS
        # ====================================================================
        # Count entries where models_usage indicates an actual API request
        llm_calls = sum(1 for entry in data if entry.get('models_usage') == 'RequestUsage')
        print("\nTotal LLM Calls:", llm_calls)
        final_output["Total LLM Calls:"] = llm_calls

        return final_output

    
    # ========================================================================
    # COMPLIANCE ASSESSMENT
    # ========================================================================
    def compliance_assessment(self, file_name, type=None):
        """
        Evaluate AI agent outputs against regulatory frameworks (GDPR, HIPAA,
        ISO 27001, etc.) to detect compliance risks and provide recommendations.
        
        Args:
            file_name: Path to JSON log file or JSON data object
            type: 'file' if file_name is a path, None if it's already loaded data
            
        Returns:
            str: Compliance assessment report with risk classifications and recommendations
        """
        # Load JSON data from file or use provided data object
        if type == "file":
            with open(file_name, 'r', encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = file_name

        # Prepare system message with file context
        replacements = {"file_name": file_name}
        system_message = self.system_messages['compliance_assessment_agent'].format(**replacements)
        
        # Construct prompt with log file data
        processed_prompt = f'Log File {file_name}:\n{data}'

        # Create message payload for LLM
        message = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': processed_prompt}
        ]

        # Execute compliance assessment via LLM
        response = gpt_llm_call(message)
        return response

    
    # ========================================================================
    # PROMPT ASSESSMENT
    # ========================================================================
    def prompt_assessment(self, file_name, type=None):
        """
        Analyze prompts for security vulnerabilities including injection attacks,
        bias, and hallucinations using NLP-based classification.
        
        Args:
            file_name: Path to JSON log file or JSON data object
            type: 'file' if file_name is a path, None if it's already loaded data
            
        Returns:
            str: Prompt security assessment report with identified risks and recommendations
        """
        # Load JSON data from file or use provided data object
        if type == "file":
            with open(file_name, 'r', encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = file_name

        # Prepare system message with file context
        replacements = {"file_name": file_name}
        system_message = self.system_messages['prompt_assessment_agent'].format(**replacements)
        
        # Construct prompt with log file data
        processed_prompt = f'Log File {file_name}:\n{data}'

        # Create message payload for LLM
        message = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': processed_prompt}
        ]

        # Execute prompt security assessment via LLM
        response = gpt_llm_call(message)
        return response

    
    # ========================================================================
    # PERFORMANCE ASSESSMENT
    # ========================================================================
    def performance_assessment_processing(self, file_name, type=None):
        """
        Evaluate AI agent performance against defined guardrails including
        hallucination detection, accuracy, consistency, latency, and failure rates.
        
        Args:
            file_name: Path to JSON log file or JSON data object
            type: 'file' if file_name is a path, None if it's already loaded data
            
        Returns:
            str: Performance assessment report with metrics and improvement recommendations
        """
        # Load JSON data from file or use provided data object
        if type == "file":
            with open(file_name, 'r', encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = file_name

        # Load performance guardrails configuration
        with open('data/performance_guardrails.txt', 'r') as file:
            performance_guardrails_content = file.read()

        # Prepare system message with file context and guardrails
        replacements = {
            "file_name": file_name,
            "performance_guardrails_content": performance_guardrails_content
        }
        system_message = self.system_messages['performance_assessment_agent'].format(**replacements)
        
        # Construct prompt with log file data
        processed_prompt = f'Log File {file_name}:\n{data}'

        # Create message payload for LLM
        message = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': processed_prompt}
        ]

        # Execute performance assessment via LLM
        response = gpt_llm_call(message)
        return response

    
    # ========================================================================
    # AGENTIC DESCRIPTION TOOL
    # ========================================================================
    def agentic_description_tool(self, file_name, description, type=None):
        """
        Generate a comprehensive description of the agentic system by combining
        user-provided description with AI-generated analysis of the log file.
        
        Args:
            file_name: Path to JSON log file or JSON data object
            description: User-provided description of the architecture
            type: 'file' if file_name is a path, None if it's already loaded data
            
        Returns:
            str: Combined description (user-provided + AI-generated analysis)
        """
        # Load JSON data from file or use provided data object
        if type == "file":
            with open(file_name, 'r', encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = file_name

        # Prepare system message with file context
        replacements = {"file_name": file_name}
        system_message = self.system_messages['agentic_description'].format(**replacements)
        
        # Construct prompt with log file data
        processed_prompt = f'Log File {file_name}:\n{data}'

        # Create message payload for LLM
        message = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': processed_prompt}
        ]

        # Generate AI description of the agentic system
        response = gpt_llm_call(message)
        
        # Combine user description with AI-generated analysis
        return description + '\n\n' + response