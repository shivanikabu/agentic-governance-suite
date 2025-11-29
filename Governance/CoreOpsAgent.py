"""
CoreOps Agent System
====================
A specialized agent for extracting and analyzing core operational details
from agentic pipeline conversation logs.

Features:
- Conversation Metadata Extraction: Retrieves basic conversation details
- Chat Flow Analysis: Analyzes conversation structure and patterns
- Operational Metrics: Extracts key performance indicators
- Custom Agent Implementation: Extends base CustomAgent class
- Asynchronous Processing: Efficient async/await pattern
- JSON Output: Returns structured data for easy integration
- Tool Integration: Uses AgenticTools for comprehensive log processing

Core Details Extracted:
- Conversation metadata (participants, timestamps, duration)
- Message flow and sequence analysis
- Agent interaction patterns
- Turn-taking statistics
- Response times and latencies
- Token usage per conversation
- Cost breakdown by agent
- Error and exception tracking
- Conversation state transitions

Use Cases:
- Operational monitoring and dashboards
- Conversation flow analysis
- Performance benchmarking
- Cost tracking and attribution
- Debugging conversation issues
- Quality assurance and testing
- Usage analytics and reporting
- Capacity planning

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
    Configure and initialize the ChatCompletionClient for CoreOps analysis.
    
    Model Configuration:
        - Model: GPT-4o for advanced reasoning and data extraction
        - Temperature: 0.0 for deterministic, consistent analysis
        - Provider: Azure OpenAI
        - API Version: Loaded from environment variables
        
    Returns:
        ChatCompletionClient: Configured model client for agent use
        
    Note:
        Uses deterministic output (temp=0.0) to ensure consistent
        operational metrics across multiple runs of the same logs.
        This is critical for reliable monitoring and alerting.
    """
    # Azure OpenAI configuration
    oai_config = {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "model": "gpt-4o",
        "azure_deployment": "gpt-4o",
        "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "api_type": "azure",
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
        "temperature": 0.0,  # Deterministic for consistent metrics
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

# Initialize agentic tools for core operations processing
agentic_tools = AgenticTools()


# ============================================================================
# CUSTOM AGENT IMPLEMENTATION
# ============================================================================

class CoreOpsAgent(CustomAgent):
    """
    Custom agent for extracting core operational details from conversation logs.
    
    This agent processes log files to extract essential conversation metadata,
    metrics, and operational details that are crucial for monitoring and
    analyzing agentic system performance.
    
    Extracted Information Includes:
        - Conversation participants and roles
        - Message counts and distribution
        - Timestamps and duration
        - Token usage and costs
        - Agent interaction patterns
        - Response latencies
        - Error occurrences
        - State transitions
        - Tool usage statistics
        
    Output Format:
        Returns structured JSON data containing all extracted operational
        details, making it easy to integrate with monitoring systems,
        dashboards, and analytics pipelines.
        
    Inherits from:
        CustomAgent: Base class for custom agent implementations
        
    Methods:
        on_messages: Main message processing handler for core ops extraction
        
    Message Format:
        Expects messages with content as string representation of list:
        "[file_path, description]"
        - file_path: Path to log file to analyze
        - description: Context or specific details to extract
    """
    
    async def on_messages(
        self, 
        messages: Sequence[ChatMessage], 
        cancellation_token: CancellationToken
    ) -> Response:
        """
        Process incoming messages and extract core operational details.
        
        Args:
            messages (Sequence[ChatMessage]): Incoming message sequence
            cancellation_token (CancellationToken): Token for async cancellation
            
        Returns:
            Response: Agent response containing structured operational data
            
        Process:
            1. Extract user message content (last message in sequence)
            2. Parse message content to get file path and description
            3. Use AgenticTools to process log and extract core details
            4. Serialize results to JSON for structured output
            5. Return JSON-formatted results wrapped in Response object
            
        Output Structure (JSON):
            {
                "conversation_id": "...",
                "participants": [...],
                "start_time": "...",
                "end_time": "...",
                "duration_seconds": 123,
                "total_messages": 45,
                "messages_by_agent": {...},
                "total_tokens": 12345,
                "total_cost": 0.234,
                "average_response_time": 1.23,
                "errors": [...],
                "tools_used": [...],
                ...
            }
            
        Note:
            - Uses ast.literal_eval to safely parse string representation
            - Returns JSON string for easy serialization and storage
            - user_message[0]: file path
            - user_message[1]: description/context
        """
        # Extract the last message (most recent user input)
        user_message = ast.literal_eval(messages[-1].content)
        
        # Perform core operations processing using agentic tools
        # user_message[0]: file path to log file
        # user_message[1]: description or context
        # 'file': indicates input is a file (vs direct text)
        final_output = agentic_tools.core_ops_processing(
            user_message[0],  # file_path
            user_message[1],  # description
            'file'            # input_type
        )
        
        # Serialize output to JSON and return wrapped in Response
        return Response(
            chat_message=TextMessage(
                content=json.dumps(final_output),  # Structured JSON output
                source='CoreOpsAgent'
            )
        )


# ============================================================================
# AGENT INSTANTIATION
# ============================================================================

# Create instance of CoreOpsAgent
core_ops_agent = CoreOpsAgent(
    name="CoreOpsAgent",
    description=(
        "You are a CoreOpsAgent. "
        "Your task is to fetch the basic details about the Chat Conversation "
        "from the given log file."
    ),
)


# ============================================================================
# AGENT PROCESSING FUNCTIONS
# ============================================================================

async def process_agent(file_name, description):
    """
    Process a single agent request for core operations analysis.
    
    Args:
        file_name (str): Path to the log file to analyze
        description (str): Context or specific details to extract
                          Examples:
                          - "Production conversation metrics"
                          - "Extract cost breakdown by agent"
                          - "User interaction patterns analysis"
        
    Returns:
        str: JSON string containing core operational details
        
    Process:
        1. Create TextMessage with file name and description
        2. Call agent's on_messages method
        3. Extract and return the JSON response
        
    Note:
        Wraps parameters in a list and converts to string for message content.
        Returns JSON string that can be parsed for further processing.
    """
    # Call agent with formatted message
    response = await core_ops_agent.on_messages(
        [TextMessage(
            content=str([file_name, description]), 
            source="user"
        )],
        cancellation_token=CancellationToken(),
    )
    
    # Extract and return response content (JSON string)
    return response.chat_message.content


async def start_agent_pipeline(file_path, description):
    """
    Start the complete agent pipeline for core operations extraction.
    
    This is the main entry point for extracting operational details from logs.
    
    Args:
        file_path (str): Path to the log file to analyze
        description (str): Context or specific extraction requirements
        
    Returns:
        str: JSON string containing complete operational details:
             - Conversation metadata
             - Performance metrics
             - Cost breakdown
             - Error tracking
             - Usage statistics
        
    Process:
        1. Invoke process_agent with file path and description
        2. Print formatted results to console for immediate review
        3. Return JSON results for further processing, storage, or visualization
        
    Output Format:
        Prints agent name and response with visual separator (*)
        for clear console output visibility. The response is a JSON string
        that can be parsed and integrated with monitoring systems.
        
    Integration Examples:
        - Parse JSON and push to monitoring dashboard
        - Store in database for historical analysis
        - Trigger alerts based on thresholds
        - Generate reports and visualizations
    """
    # Execute core operations processing
    results = await process_agent(
        file_name=file_path, 
        description=description
    )
    
    # Print formatted results
    print('PRINTING AGENTS RESPONSES:')
    print(f'Agent Name: core_ops_agent')
    print(f'Response: {results}')
    print('*' * 100)
    
    return results


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Example Usage:

# Example 1: Basic operational metrics extraction
import asyncio
import json

results_json = asyncio.run(start_agent_pipeline(
    file_path="logs/production_chat_2024_q4.json",
    description="Extract core operational metrics for monitoring dashboard"
))

# Parse JSON results
results = json.loads(results_json)
print(f"Total messages: {results['total_messages']}")
print(f"Total cost: ${results['total_cost']}")

# Example 2: Cost analysis by agent
results_json = asyncio.run(start_agent_pipeline(
    file_path="logs/expensive_conversation.json",
    description="Detailed cost breakdown by agent and operation"
))

results = json.loads(results_json)
for agent, cost in results['cost_by_agent'].items():
    print(f"{agent}: ${cost}")

# Example 3: Performance monitoring
results_json = asyncio.run(start_agent_pipeline(
    file_path="logs/slow_conversation.json",
    description="Extract latency and performance metrics"
))

results = json.loads(results_json)
if results['average_response_time'] > 2.0:
    print("WARNING: Average response time exceeds threshold!")

# Example 4: Async execution in existing event loop
async def analyze_and_store(file_path, db_connection):
    results_json = await start_agent_pipeline(
        file_path=file_path,
        description="Core metrics for database storage"
    )
    
    results = json.loads(results_json)
    
    # Store in database
    await db_connection.insert_metrics(results)
    
    # Check for anomalies
    if results['errors'] and len(results['errors']) > 0:
        await send_alert(results['errors'])
    
    return results

# Example 5: Batch processing for multiple conversations
async def batch_analyze(log_files):
    tasks = [
        start_agent_pipeline(file_path, "Batch operational analysis")
        for file_path in log_files
    ]
    results = await asyncio.gather(*tasks)
    
    # Parse all results
    parsed_results = [json.loads(r) for r in results]
    
    # Aggregate metrics
    total_cost = sum(r['total_cost'] for r in parsed_results)
    total_tokens = sum(r['total_tokens'] for r in parsed_results)
    
    print(f"Batch totals - Cost: ${total_cost}, Tokens: {total_tokens}")
    
    return parsed_results

log_files = [
    "logs/conversation_1.json",
    "logs/conversation_2.json",
    "logs/conversation_3.json"
]
batch_results = asyncio.run(batch_analyze(log_files))

# Example 6: Real-time monitoring integration
async def monitor_conversations(log_directory):
    while True:
        for log_file in get_new_logs(log_directory):
            results_json = await start_agent_pipeline(
                file_path=log_file,
                description="Real-time monitoring metrics"
            )
            
            results = json.loads(results_json)
            
            # Push to monitoring system
            metrics_client.push({
                'timestamp': results['end_time'],
                'duration': results['duration_seconds'],
                'cost': results['total_cost'],
                'tokens': results['total_tokens'],
                'errors': len(results['errors'])
            })
        
        await asyncio.sleep(60)  # Check every minute
"""