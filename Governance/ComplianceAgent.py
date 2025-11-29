"""
Compliance Assessment Agent System
===================================
A specialized agent for verifying compliance of agentic pipelines against
regulatory, security, and organizational standards.

Features:
- Compliance Verification: Evaluates agent logs for compliance violations
- Regulatory Standards: Checks against industry regulations (GDPR, HIPAA, etc.)
- Security Assessment: Identifies security compliance issues
- Custom Agent Implementation: Extends base CustomAgent class
- Asynchronous Processing: Efficient async/await pattern
- Tool Integration: Uses AgenticTools for comprehensive compliance checks

Compliance Areas Checked:
- Data privacy and protection regulations
- Security best practices and standards
- Industry-specific compliance requirements
- Organizational policies and guidelines
- Audit trail completeness
- Access control and authentication

Use Cases:
- Production pipeline compliance auditing
- Regulatory compliance verification
- Security policy enforcement
- Pre-deployment compliance checks
- Continuous compliance monitoring
- Incident investigation and audit support

Author: [Shivani Kabu & Nikhil Khandelwal]
Date: [01/12/2025]
Version: 1.0
"""

# ============================================================================
# IMPORTS
# ============================================================================
import sys
import os
import ast
import asyncio
import json
from typing import Sequence
from dotenv import load_dotenv

# Autogen framework imports
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage, ChatMessage, MultiModalMessage
from autogen_agentchat.base import Response
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient

# Custom modules
from Governance.agents.CustomAgent import CustomAgent
from Governance.tools import AgenticTools

# Add parent directory to path for imports
sys.path.append("../")


# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================
# Load environment variables from .env file
load_dotenv()


# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

def configure_model_client():
    """
    Configure and initialize the ChatCompletionClient for compliance analysis.
    
    Model Configuration:
        - Model: GPT-4o for advanced reasoning and compliance analysis
        - Temperature: 0.0 for deterministic, consistent compliance checks
        - Provider: Azure OpenAI
        - API Version: Loaded from environment variables
        
    Returns:
        ChatCompletionClient: Configured model client for agent use
        
    Note:
        Uses deterministic output (temp=0.0) to ensure consistent
        compliance assessments across multiple runs of the same data.
    """
    # Azure OpenAI configuration
    oai_config = {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "model": "gpt-4o",
        "azure_deployment": "gpt-4o",
        "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "api_type": "azure",
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
        "temperature": 0.0,  # Deterministic for consistent compliance checks
    }
    
    # Create LLM configuration for ChatCompletionClient
    llm_config = {
        "provider": "AzureOpenAIChatCompletionClient",
        "config": oai_config
    }
    
    # Initialize and return model client
    return ChatCompletionClient.load_component(llm_config)


# Initialize model client
model_client = configure_model_client()

# Initialize agentic tools for compliance assessment
agentic_tools = AgenticTools()


# ============================================================================
# CUSTOM AGENT IMPLEMENTATION
# ============================================================================

class ComplianceAgent(CustomAgent):
    """
    Custom agent for verifying compliance of agentic pipelines.
    
    This agent analyzes log files to identify compliance violations,
    security issues, and regulatory non-compliance in agent interactions.
    
    Compliance Checks Include:
        - Data privacy regulations (GDPR, CCPA, etc.)
        - Security standards (OWASP, NIST, etc.)
        - Industry regulations (HIPAA, PCI-DSS, SOC2, etc.)
        - Organizational policies
        - Audit trail requirements
        - Access control compliance
        
    Inherits from:
        CustomAgent: Base class for custom agent implementations
        
    Methods:
        on_messages: Main message processing handler for compliance checks
        
    Message Format:
        Expects messages with content as string representation of list:
        "[file_path, description]"
        - file_path: Path to log file to analyze for compliance
        - description: Context or specific compliance requirements to check
    """
    
    async def on_messages(
        self, 
        messages: Sequence[ChatMessage], 
        cancellation_token: CancellationToken
    ) -> Response:
        """
        Process incoming messages and perform compliance assessment.
        
        Args:
            messages (Sequence[ChatMessage]): Incoming message sequence
            cancellation_token (CancellationToken): Token for async cancellation
            
        Returns:
            Response: Agent response containing compliance assessment results
            
        Process:
            1. Extract user message content (last message in sequence)
            2. Parse message content to get file path and description
            3. Use AgenticTools to perform comprehensive compliance assessment
            4. Return assessment results wrapped in Response object
            
        Assessment Output Includes:
            - Compliance violations found
            - Severity levels (Critical, High, Medium, Low)
            - Specific regulation/policy violated
            - Remediation recommendations
            - Risk assessment
            
        Note:
            Uses ast.literal_eval to safely parse string representation
            of the message content list.
        """
        # Extract the last message (most recent user input)
        user_message = ast.literal_eval(messages[-1].content)
        
        # Perform compliance assessment using agentic tools
        # user_message[0]: file path to log file
        # 'file': indicates input is a file (vs direct text)
        final_output = agentic_tools.compliance_assessment(
            user_message[0], 
            'file'
        )
        
        # Return response wrapped in Response object
        return Response(
            chat_message=TextMessage(
                content=final_output, 
                source='ComplianceAgent'
            )
        )


# ============================================================================
# AGENT INSTANTIATION
# ============================================================================

# Create instance of ComplianceAgent
compliance_agent = ComplianceAgent(
    name="ComplianceAgent",
    description=(
        "You are a ComplianceAgent. "
        "Your task is to verify the compliance of the Agentic pipeline "
        "from the given log file."
    ),
)


# ============================================================================
# AGENT PROCESSING FUNCTIONS
# ============================================================================

async def process_agent(file_name, description):
    """
    Process a single agent request for compliance assessment.
    
    Args:
        file_name (str): Path to the log file to analyze
        description (str): Context or specific compliance requirements
        
    Returns:
        str: Compliance assessment results from the agent
        
    Process:
        1. Create TextMessage with file name and description
        2. Call agent's on_messages method
        3. Extract and return the compliance assessment results
        
    Note:
        Wraps parameters in a list and converts to string for message content.
        This format is expected by the agent's message parser.
    """
    # Call agent with formatted message
    response = await compliance_agent.on_messages(
        [TextMessage(
            content=str([file_name, description]), 
            source="user"
        )],
        cancellation_token=CancellationToken(),
    )
    
    # Extract and return response content
    return response.chat_message.content


async def start_agent_pipeline(file_path, description):
    """
    Start the complete agent pipeline for compliance assessment.
    
    This is the main entry point for analyzing compliance of agent logs.
    
    Args:
        file_path (str): Path to the log file to analyze
        description (str): Context or specific compliance requirements to check
                          Examples:
                          - "GDPR compliance check"
                          - "HIPAA audit for patient data handling"
                          - "SOC2 Type II compliance verification"
        
    Returns:
        str: Complete compliance assessment results including:
             - Violations found
             - Severity ratings
             - Affected regulations
             - Remediation steps
             - Risk assessment
        
    Process:
        1. Invoke process_agent with file path and description
        2. Print formatted results to console for immediate review
        3. Return results for further processing or storage
        
    Output Format:
        Prints agent name and response with visual separator (*)
        for clear console output visibility and easy log parsing.
    """
    # Execute compliance assessment
    results = await process_agent(
        file_name=file_path, 
        description=description
    )
    
    # Print formatted results
    print('PRINTING AGENTS RESPONSES:')
    print(f'Agent Name: ComplianceAgent')
    print(f'Response: {results}')
    print('*' * 100)
    
    return results


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Example Usage:

# Example 1: GDPR Compliance Check
import asyncio

results = asyncio.run(start_agent_pipeline(
    file_path="logs/production_agents_2024_q4.json",
    description="GDPR compliance verification for EU user data processing"
))

# Example 2: HIPAA Compliance Audit
results = asyncio.run(start_agent_pipeline(
    file_path="logs/healthcare_agents.json",
    description="HIPAA audit for protected health information handling"
))

# Example 3: SOC2 Type II Compliance
results = asyncio.run(start_agent_pipeline(
    file_path="logs/security_agents.json",
    description="SOC2 Type II compliance check for access controls"
))

# Example 4: Async execution in existing event loop
async def main():
    results = await start_agent_pipeline(
        file_path="logs/financial_agents.json",
        description="PCI-DSS compliance for payment processing"
    )
    
    # Process results
    if "CRITICAL" in results:
        send_alert_to_security_team(results)
    
    return results

# Example 5: Batch compliance checking
async def batch_compliance_check(log_files):
    tasks = [
        start_agent_pipeline(file_path, "General compliance check")
        for file_path in log_files
    ]
    results = await asyncio.gather(*tasks)
    return results

log_files = [
    "logs/agent_1.json",
    "logs/agent_2.json",
    "logs/agent_3.json"
]
batch_results = asyncio.run(batch_compliance_check(log_files))
"""