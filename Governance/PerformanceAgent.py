"""
Performance Assessment Agent System
====================================
A specialized agent for analyzing and evaluating the performance of agentic
pipelines through comprehensive log analysis.

Features:
- Performance Metrics Extraction: Analyzes latency, throughput, and efficiency
- Bottleneck Identification: Pinpoints slow operations and agents
- Resource Usage Analysis: Monitors token consumption and API costs
- Trend Analysis: Identifies performance patterns over time
- Custom Agent Implementation: Extends base CustomAgent class
- Asynchronous Processing: Efficient async/await pattern
- Tool Integration: Uses AgenticTools for comprehensive performance analysis

Performance Metrics Analyzed:
- Response time and latency per agent
- Token consumption rates
- API call costs and efficiency
- Message processing throughput
- Agent-to-agent handoff times
- Error rates and retry patterns
- Resource utilization (tokens per operation)
- Queue times and processing delays
- End-to-end conversation duration
- Tool execution times

Performance Issues Detected:
- High latency agents or operations
- Inefficient token usage
- Cost optimization opportunities
- Bottlenecks in agent chains
- Retry storms and failure cascades
- Suboptimal routing decisions
- Memory or resource constraints
- Slow tool executions

Use Cases:
- Production performance monitoring
- Capacity planning and scaling decisions
- Cost optimization analysis
- SLA compliance verification
- Performance regression detection
- Agent efficiency benchmarking
- Root cause analysis for slow responses
- Performance trend tracking

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
    Configure and initialize the ChatCompletionClient for performance analysis.
    
    Model Configuration:
        - Model: GPT-4o for advanced reasoning and pattern recognition
        - Temperature: 0.0 for deterministic, consistent analysis
        - Provider: Azure OpenAI
        - API Version: Loaded from environment variables
        
    Returns:
        ChatCompletionClient: Configured model client for agent use
        
    Note:
        Uses deterministic output (temp=0.0) to ensure consistent
        performance measurements and threshold comparisons across
        multiple runs. This is critical for reliable performance
        monitoring and alerting on SLA violations.
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

# Initialize agentic tools for performance assessment
agentic_tools = AgenticTools()


# ============================================================================
# CUSTOM AGENT IMPLEMENTATION
# ============================================================================

class PerformanceAgent(CustomAgent):
    """
    Custom agent for analyzing performance of agentic pipelines.
    
    This agent processes log files to extract performance metrics,
    identify bottlenecks, detect inefficiencies, and provide actionable
    recommendations for optimization.
    
    Analysis Categories:
    
    1. Latency Analysis:
       - Response times per agent
       - End-to-end conversation duration
       - Agent handoff delays
       - Tool execution times
       
    2. Resource Efficiency:
       - Token usage per operation
       - API call costs
       - Token-to-value ratio
       - Resource waste identification
       
    3. Throughput Analysis:
       - Messages processed per second
       - Concurrent operation handling
       - Queue depths and wait times
       - System capacity utilization
       
    4. Error Impact:
       - Retry overhead
       - Error recovery times
       - Failure cascade detection
       - Error rate trends
       
    5. Optimization Opportunities:
       - Caching recommendations
       - Agent consolidation suggestions
       - Routing improvements
       - Cost reduction strategies
    
    Output Includes:
        - Performance scores and ratings
        - Bottleneck identification
        - Specific optimization recommendations
        - Trend analysis and patterns
        - SLA compliance status
        - Comparative benchmarks
        
    Inherits from:
        CustomAgent: Base class for custom agent implementations
        
    Methods:
        on_messages: Main message processing handler for performance assessment
        
    Message Format:
        Expects messages with content as string representation of list:
        "[file_path, description]"
        - file_path: Path to log file to analyze
        - description: Context or specific performance aspects to evaluate
    """
    
    async def on_messages(
        self, 
        messages: Sequence[ChatMessage], 
        cancellation_token: CancellationToken
    ) -> Response:
        """
        Process incoming messages and perform performance assessment.
        
        Args:
            messages (Sequence[ChatMessage]): Incoming message sequence
            cancellation_token (CancellationToken): Token for async cancellation
            
        Returns:
            Response: Agent response containing performance analysis results
            
        Process:
            1. Extract user message content (last message in sequence)
            2. Parse message content to get file path and description
            3. Use AgenticTools to perform comprehensive performance analysis
            4. Return assessment results wrapped in Response object
            
        Assessment Output Structure:
            - Performance Summary:
              * Overall performance score (0-100)
              * SLA compliance status
              * Key metrics snapshot
              
            - Detailed Metrics:
              * Average/P50/P95/P99 latencies
              * Token usage statistics
              * Cost breakdown
              * Throughput rates
              
            - Bottleneck Analysis:
              * Slowest agents/operations
              * High-cost operations
              * Resource-intensive components
              * Critical path analysis
              
            - Recommendations:
              * Quick wins for optimization
              * Long-term improvements
              * Cost reduction opportunities
              * Scaling suggestions
              
            - Trends:
              * Performance degradation alerts
              * Improving/degrading patterns
              * Anomaly detection
              
        Note:
            Uses ast.literal_eval to safely parse string representation
            of the message content list.
        """
        # Extract the last message (most recent user input)
        user_message = ast.literal_eval(messages[-1].content)
        
        # Perform performance assessment using agentic tools
        # user_message[0]: file path to log file
        # 'file': indicates input is a file (vs direct text)
        final_output = agentic_tools.performance_assessment_processing(
            user_message[0],  # file_path
            'file'            # input_type
        )
        
        # Return response wrapped in Response object
        return Response(
            chat_message=TextMessage(
                content=final_output, 
                source='PerformanceAgent'
            )
        )


# ============================================================================
# AGENT INSTANTIATION
# ============================================================================

# Create instance of PerformanceAgent
performance_agent = PerformanceAgent(
    name="PerformanceAgent",
    description=(
        "You are a PerformanceAgent. "
        "Your task is to identify the performance of the Agentic pipeline "
        "from the given log file."
    ),
)


# ============================================================================
# AGENT PROCESSING FUNCTIONS
# ============================================================================

async def process_agent(file_name, description):
    """
    Process a single agent request for performance assessment.
    
    Args:
        file_name (str): Path to the log file to analyze
        description (str): Context or specific performance aspects to evaluate
                          Examples:
                          - "Production performance analysis for Q4"
                          - "Identify slow agents causing SLA violations"
                          - "Cost optimization opportunities"
                          - "Compare against baseline performance"
        
    Returns:
        str: Performance assessment results including metrics, bottlenecks,
             and optimization recommendations
        
    Process:
        1. Create TextMessage with file name and description
        2. Call agent's on_messages method
        3. Extract and return the performance analysis results
        
    Note:
        Wraps parameters in a list and converts to string for message content.
        This format is expected by the agent's message parser.
    """
    # Call agent with formatted message
    response = await performance_agent.on_messages(
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
    Start the complete agent pipeline for performance assessment.
    
    This is the main entry point for analyzing agentic pipeline performance.
    
    Args:
        file_path (str): Path to the log file to analyze
        description (str): Context or specific performance requirements
        
    Returns:
        str: Complete performance assessment including:
             - Performance scores and ratings
             - Detailed latency, cost, and throughput metrics
             - Bottleneck identification with severity levels
             - Root cause analysis
             - Actionable optimization recommendations
             - Trend analysis and predictions
             - SLA compliance status
        
    Process:
        1. Invoke process_agent with file path and description
        2. Print formatted results to console for immediate review
        3. Return results for further processing, alerting, or visualization
        
    Output Format:
        Prints agent name and response with visual separator (*)
        for clear console output visibility. Results can be parsed
        for integration with monitoring dashboards and alerting systems.
        
    Integration Examples:
        - Parse results and push to performance dashboard
        - Trigger alerts on SLA violations or performance degradation
        - Store metrics in time-series database
        - Generate performance reports
        - Compare against historical baselines
    """
    # Execute performance assessment
    results = await process_agent(
        file_name=file_path, 
        description=description
    )
    
    # Print formatted results
    print('PRINTING AGENTS RESPONSES:')
    print(f'Agent Name: performance_agent')
    print(f'Response: {results}')
    print('*' * 100)
    
    return results


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Example Usage:

# Example 1: Basic performance analysis
import asyncio

results = asyncio.run(start_agent_pipeline(
    file_path="logs/production_2024_q4.json",
    description="Overall performance assessment for production pipeline"
))

# Example 2: SLA compliance check
results = asyncio.run(start_agent_pipeline(
    file_path="logs/customer_conversations.json",
    description="Verify SLA compliance - response time < 2s, P95 < 5s"
))

# Check for violations
if "SLA VIOLATION" in results:
    send_alert_to_ops_team(results)

# Example 3: Cost optimization analysis
results = asyncio.run(start_agent_pipeline(
    file_path="logs/high_cost_conversations.json",
    description="Identify cost optimization opportunities and inefficient token usage"
))

# Example 4: Bottleneck identification
results = asyncio.run(start_agent_pipeline(
    file_path="logs/slow_conversations.json",
    description="Identify performance bottlenecks causing user complaints"
))

# Example 5: Async execution with threshold monitoring
async def monitor_performance_with_alerts(file_path):
    results = await start_agent_pipeline(
        file_path=file_path,
        description="Performance monitoring with alerting"
    )
    
    # Parse results and check thresholds
    if "CRITICAL" in results or "P95 latency" in results:
        await send_urgent_alert(results)
    
    if "cost increase" in results.lower():
        await notify_finance_team(results)
    
    return results

# Example 6: Batch performance analysis
async def batch_performance_analysis(log_files):
    tasks = [
        start_agent_pipeline(file_path, "Batch performance analysis")
        for file_path in log_files
    ]
    results = await asyncio.gather(*tasks)
    
    # Aggregate findings
    all_bottlenecks = []
    for i, result in enumerate(results):
        if "bottleneck" in result.lower():
            all_bottlenecks.append({
                'file': log_files[i],
                'analysis': result
            })
    
    return all_bottlenecks

log_files = [
    "logs/agent_pipeline_1.json",
    "logs/agent_pipeline_2.json",
    "logs/agent_pipeline_3.json"
]
bottlenecks = asyncio.run(batch_performance_analysis(log_files))

# Example 7: Continuous performance monitoring
async def continuous_performance_monitor(log_directory, interval_seconds=300):
    baseline_metrics = {}
    
    while True:
        for log_file in get_recent_logs(log_directory):
            results = await start_agent_pipeline(
                file_path=log_file,
                description="Continuous performance monitoring"
            )
            
            # Extract metrics (assuming results contain structured data)
            current_metrics = extract_metrics(results)
            
            # Compare with baseline
            if baseline_metrics:
                degradation = compare_metrics(baseline_metrics, current_metrics)
                if degradation > 20:  # 20% degradation threshold
                    await alert_performance_degradation(log_file, degradation)
            else:
                baseline_metrics = current_metrics
            
            # Push to monitoring system
            await push_to_datadog(current_metrics)
        
        await asyncio.sleep(interval_seconds)

# Example 8: Performance comparison across versions
async def compare_versions(v1_logs, v2_logs):
    v1_results = await start_agent_pipeline(
        file_path=v1_logs,
        description="Performance baseline - Version 1.0"
    )
    
    v2_results = await start_agent_pipeline(
        file_path=v2_logs,
        description="Performance comparison - Version 2.0"
    )
    
    # Generate comparison report
    comparison = generate_comparison_report(v1_results, v2_results)
    print(comparison)
    
    return comparison

# Example 9: Performance optimization workflow
async def optimize_pipeline(log_file):
    # Step 1: Initial assessment
    initial_results = await start_agent_pipeline(
        log_file,
        "Identify optimization opportunities"
    )
    
    # Step 2: Extract recommendations
    recommendations = parse_recommendations(initial_results)
    
    # Step 3: Apply optimizations (manual or automated)
    apply_optimizations(recommendations)
    
    # Step 4: Verify improvements
    post_opt_results = await start_agent_pipeline(
        log_file,
        "Verify optimization impact"
    )
    
    return {
        'before': initial_results,
        'after': post_opt_results,
        'recommendations': recommendations
    }
"""