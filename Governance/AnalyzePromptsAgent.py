"""
Prompt Assessment Agent System
================================
A specialized agent for analyzing and assessing prompts used in agentic pipelines.
Uses custom agents with Azure OpenAI to evaluate prompt quality and effectiveness.

Features:
- Prompt Quality Analysis: Evaluates prompts from log files
- Custom Agent Implementation: Extends base CustomAgent class
- Dual LLM Support: Primary and optional jury model configuration
- Asynchronous Processing: Efficient async/await pattern
- Tool Integration: Uses AgenticTools for prompt assessment

Use Cases:
- Analyzing prompts in production agent logs
- Evaluating prompt effectiveness
- Quality assurance for agentic systems
- Prompt optimization recommendations

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
    Configure and initialize the ChatCompletionClient for agent communication.
    
    Configuration Priority:
    1. Jury Model: If JURY_AZURE_OPENAI_API_KEY and JURY_AZURE_OPENAI_ENDPOINT exist
    2. Primary Model: Falls back to AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
    
    Returns:
        ChatCompletionClient: Configured model client for agent use
        
    Model Configuration:
        - Model: GPT-4o for advanced reasoning
        - Temperature: 0.0 for deterministic, consistent outputs
        - API Version: Loaded from environment
        - Type: Azure OpenAI
        
    Note:
        The jury model is an optional secondary model that can be used
        for validation or evaluation tasks requiring a different perspective.
    """
    # Check for jury model credentials
    if os.getenv("JURY_AZURE_OPENAI_API_KEY") and os.getenv("JURY_AZURE_OPENAI_ENDPOINT"):
        # Use jury model configuration
        oai_config = {
            "api_key": os.getenv("JURY_AZURE_OPENAI_API_KEY"),
            "model": "gpt-4o",
            "azure_deployment": "gpt-4o",
            "azure_endpoint": os.getenv("JURY_AZURE_OPENAI_ENDPOINT"),
            "api_type": "azure",
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
            "temperature": 0.0,  # Deterministic outputs
        }
    else:
        # Use primary model configuration
        oai_config = {
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "model": "gpt-4o",
            "azure_deployment": "gpt-4o",
            "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_type": "azure",
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
            "temperature": 0.0,  # Deterministic outputs
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

# Initialize agentic tools for prompt assessment
agentic_tools = AgenticTools()


# ============================================================================
# CUSTOM AGENT IMPLEMENTATION
# ============================================================================

class AnalyzePromptsAgent(CustomAgent):
    """
    Custom agent for analyzing prompts used in agentic pipelines.
    
    This agent processes log files to extract and evaluate prompts,
    providing quality assessments and recommendations for improvement.
    
    Inherits from:
        CustomAgent: Base class for custom agent implementations
        
    Methods:
        on_messages: Main message processing handler
        
    Message Format:
        Expects messages with content as string representation of list:
        "[file_path, description]"
        - file_path: Path to log file containing prompts
        - description: Context or additional information about the analysis
    """
    
    async def on_messages(
        self, 
        messages: Sequence[ChatMessage], 
        cancellation_token: CancellationToken
    ) -> Response:
        """
        Process incoming messages and perform prompt analysis.
        
        Args:
            messages (Sequence[ChatMessage]): Incoming message sequence
            cancellation_token (CancellationToken): Token for async cancellation
            
        Returns:
            Response: Agent response containing prompt assessment results
            
        Process:
            1. Extract user message content (last message in sequence)
            2. Parse message content to get file path and description
            3. Use AgenticTools to perform prompt assessment
            4. Return assessment results wrapped in Response object
            
        Note:
            Uses ast.literal_eval to safely parse string representation
            of the message content list.
        """
        # Extract the last message (most recent user input)
        user_message = ast.literal_eval(messages[-1].content)
        
        # Perform prompt assessment using agentic tools
        # user_message[0]: file path
        # 'file': indicates input is a file (vs direct text)
        prompt_assessment_response = agentic_tools.prompt_assessment(
            user_message[0], 
            'file'
        )
        
        # Return response wrapped in Response object
        return Response(
            chat_message=TextMessage(
                content=prompt_assessment_response, 
                source='AnalyzePromptsAgent'
            )
        )


# ============================================================================
# AGENT INSTANTIATION
# ============================================================================

# Create instance of AnalyzePromptsAgent
analyze_prompts_agent = AnalyzePromptsAgent(
    name="AnalyzePromptsAgent",
    description=(
        "Your are an AnalyzePromptsAgent. "
        "Your task is to analyze the prompt used in the Agentic pipeline "
        "from the given log file."
    ),
)


# ============================================================================
# AGENT PROCESSING FUNCTIONS
# ============================================================================

async def process_agent(file_name, description):
    """
    Process a single agent request for prompt analysis.
    
    Args:
        file_name (str): Path to the log file containing prompts
        description (str): Context or description for the analysis
        
    Returns:
        str: Prompt assessment results from the agent
        
    Process:
        1. Create TextMessage with file name and description
        2. Call agent's on_messages method
        3. Extract and return the response content
        
    Note:
        Wraps parameters in a list and converts to string for message content.
    """
    # Call agent with formatted message
    response = await analyze_prompts_agent.on_messages(
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
    Start the complete agent pipeline for prompt analysis.
    
    This is the main entry point for analyzing prompts from log files.
    
    Args:
        file_path (str): Path to the log file to analyze
        description (str): Context or description for the analysis
        
    Returns:
        str: Complete prompt assessment results
        
    Process:
        1. Invoke process_agent with file path and description
        2. Print formatted results to console
        3. Return results for further processing
        
    Output Format:
        Prints agent name and response with visual separator (*)
        for clear console output visibility.
    """
    # Execute agent processing
    results = await process_agent(
        file_name=file_path, 
        description=description
    )
    
    # Print formatted results
    print('PRINTING AGENTS RESPONSES:')
    print(f'Agent Name: analyze_prompts_agent')
    print(f'Response: {results}')
    print('*' * 100)
    
    return results


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
"""
Example Usage:

# Synchronous execution
import asyncio

# Analyze prompts from a log file
results = asyncio.run(start_agent_pipeline(
    file_path="logs/agent_interactions.json",
    description="Production pipeline analysis for Q4 2024"
))

# Async execution in existing event loop
results = await start_agent_pipeline(
    file_path="logs/agent_interactions.json",
    description="Production pipeline analysis for Q4 2024"
)
"""