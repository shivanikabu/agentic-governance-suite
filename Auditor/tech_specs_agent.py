"""
AI Technical Specification Document Analysis System
===================================================
A multi-agent system for comprehensive analysis of technical specification documents.
Uses a two-agent approach for thorough review and validation:

1. Review Agent: Analyzes technical specifications across multiple dimensions
2. Evaluator Agent: Validates and enhances the review for completeness

Analysis Dimensions:
- Purpose and clarity assessment
- Functional requirements evaluation
- Technical architecture review
- Security and compliance verification
- Testing strategy validation
- Resource requirements analysis
- Risk identification and mitigation
- Code-level details examination
- Scalability and performance considerations
- Maintainability assessment

Output:
- Saves original specification to 'technical_specification_input.txt'
- Saves analysis results to 'technical_specification_analysis.txt'
- These files are used by other tools (e.g., Code Review) for validation

Author: [Shivani Kabu & Nikhil Khandelwal]
Date: [01/12/2025]
Version: 1.0
"""

# ============================================================================
# IMPORTS
# ============================================================================
import streamlit as st
import tempfile
import os
import asyncio
import fitz  # PyMuPDF for PDF processing
from Auditor.system_messages import agent_system_messages

# Autogen framework imports
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_core.models import ChatCompletionClient
from autogen_core import CancellationToken


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def read_pdf(file_path):
    """
    Extract text content from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text content from all pages, with page breaks
        
    Note:
        Uses PyMuPDF (fitz) to extract text page by page.
        Each page's content is separated by double newlines.
    """
    text = ""
    with fitz.open(file_path) as pdf:
        for page_num, page in enumerate(pdf, start=1):
            page_text = page.get_text()
            text += f"\n\n{page_text}"
    return text


# ============================================================================
# AGENT INITIALIZATION
# ============================================================================

def initialize_agents(model_client):
    """
    Initialize the two-agent system for technical specification analysis.
    
    Args:
        model_client: ChatCompletionClient instance for LLM communication
        
    Returns:
        list: List of initialized agents in execution order:
              [Review Agent, Evaluator Agent]
    
    Agent Flow:
        1. Review Agent: Performs comprehensive technical specification review
        2. Evaluator Agent: Validates and enhances the review, ensuring completeness
        
    Termination:
        The Evaluator Agent signals completion by responding with "TERMINATE"
        when the review is comprehensive and covers all perspectives.
    """
    
    # ========================================
    # AGENT 1: REVIEW AGENT
    # ========================================
    # Performs comprehensive technical specification analysis
    review_agent_sys = agent_system_messages['tech_review_agent_sys'] 

    # ========================================
    # AGENT 2: EVALUATOR AGENT
    # ========================================
    # Validates and enhances the technical specification review
    evaluator_agent_sys = agent_system_messages['tech_evaluator_agent_sys']

    # ========================================
    # CREATE AGENT INSTANCES
    # ========================================
    review_agent = AssistantAgent(
        "Review_Agent",
        model_client=model_client,
        system_message=review_agent_sys,
    )

    evaluator_agent = AssistantAgent(
        "Evaluator_Agent",  # Fixed: was "Evaluator_Agent_sys"
        model_client=model_client,
        system_message=evaluator_agent_sys,
    )

    # Return agents in execution order
    return [
        review_agent,      # Step 1: Review technical specification
        evaluator_agent    # Step 2: Evaluate and enhance the review
    ]


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

async def run_analysis(tech_content):
    """
    Execute the multi-agent technical specification analysis workflow.
    
    Args:
        tech_content (str): Text content extracted from technical specification PDF
        
    Returns:
        str: Final analysis results from the Evaluator Agent
        
    Workflow:
        1. Configure Azure OpenAI model client
        2. Initialize two-agent system (Review + Evaluator)
        3. Create text message with specification content
        4. Execute round-robin group chat with agents
        5. Return final evaluation results
        
    Configuration:
        - Model: GPT-4o via Azure OpenAI
        - Temperature: 0.0 for consistent, deterministic outputs
        - Max turns: 4 (allows 2 rounds for each agent)
        
    Note:
        Returns the second-to-last message (-2), which is the
        Evaluator Agent's comprehensive final assessment.
    """
    
    # ========================================
    # CONFIGURE AZURE OPENAI CLIENT
    # ========================================
    oai_config = {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "model": "gpt-4o",
        "azure_deployment": "gpt-4o",
        "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "api_type": "azure",
        "api_version": "2024-08-01-preview",
        "temperature": 0.0,  # Deterministic outputs for consistent analysis
    }
    
    llm_config = {
        "provider": "AzureOpenAIChatCompletionClient",
        "config": oai_config
    }
    
    # Initialize model client for agent communication
    model_client = ChatCompletionClient.load_component(llm_config)
    
    # ========================================
    # INITIALIZE AGENT TEAM
    # ========================================
    agents = initialize_agents(model_client)
    
    # ========================================
    # CONFIGURE TERMINATION
    # ========================================
    # Agents signal completion by including "TERMINATE" in their response
    termination = TextMentionTermination("TERMINATE")
    
    # ========================================
    # CREATE GROUP CHAT
    # ========================================
    # Round-robin ensures agents take turns in order
    # Max turns = 4 allows 2 rounds for each of the 2 agents
    group_chat = RoundRobinGroupChat(
        agents, 
        termination_condition=termination, 
        max_turns=4
    )
    
    # ========================================
    # EXECUTE ANALYSIS
    # ========================================
    # Create text message with specification content
    task_message = TextMessage(
        content=f'Technical Specification Document:\n\n{tech_content}', 
        source='user'
    )
    
    # Run the analysis and capture results
    response = await Console(group_chat.run_stream(task=[task_message]))
    
    # Return the Evaluator Agent's final assessment
    # -2 is the second-to-last message (before TERMINATE)
    return response.messages[-2].content


# ============================================================================
# STREAMLIT UI
# ============================================================================

# ========================================
# PAGE HEADER
# ========================================
st.title("AI - Technical Specification Document Analysis")
st.write("Upload your Technical Specification Document (PDF) to get a comprehensive analysis")

# ========================================
# SESSION STATE INITIALIZATION
# ========================================
# Track current agent (for potential future use)
if 'current_agent' not in st.session_state:
    st.session_state.current_agent = 0

# Store analysis results
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# ========================================
# FILE UPLOAD SECTION
# ========================================
col1, col2 = st.columns(2)

with col1:
    sow_file = st.file_uploader(
        "Upload Technical Specification (PDF)", 
        type=['pdf']
    )

# ========================================
# ANALYSIS EXECUTION
# ========================================
if sow_file:
    if st.button("Start Analysis"):
        
        # Create temporary file for uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_sow:
            tmp_sow.write(sow_file.getvalue())
            tmp_sow_path = tmp_sow.name
        
        # Extract text content from PDF
        sow_content = read_pdf(tmp_sow_path)

        # Execute analysis with progress indicator
        with st.spinner("Analyzing Technical Specification Document..."):
            # Run async analysis in sync context
            final_response = asyncio.run(
                run_analysis(sow_content)
            )
            
            # ========================================
            # SAVE RESULTS TO FILES
            # ========================================
            # These files are used by other tools for validation
            
            # Save original specification content
            with open("data/technical_specification_input.txt", "w") as f:
                f.write(sow_content)
            
            # Save analysis results
            with open("data/technical_specification_analysis.txt", "w") as f:
                f.write(final_response)
            
            # Clean up temporary PDF file
            os.unlink(tmp_sow_path)
            
            # ========================================
            # DISPLAY RESULTS
            # ========================================
            st.markdown(final_response)