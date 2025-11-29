"""
AI Architecture Diagram Analysis & Validation System
====================================================
A multi-agent system that analyzes architecture diagrams and technical specifications
using a three-agent approach:
1. Cloud Classification Agent - Identifies the target cloud platform
2. Architecture Review Agent - Analyzes architecture with platform-specific insights
3. Evaluator Agent - Validates and enhances the analysis

Features:
- Cloud platform classification (Azure/AWS/GCP)
- Architecture diagram analysis
- Technical specification validation
- Platform-specific recommendations
- Multi-agent collaborative review

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
from PIL import Image
from io import BytesIO
import fitz  # PyMuPDF for PDF processing
from Auditor.system_messages import agent_system_messages

# Autogen framework imports
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import MultiModalMessage
from autogen_core import Image as AutogenImage
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
        str: Extracted text content from all pages
        
    Note:
        Uses PyMuPDF (fitz) to extract text page by page
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
    Initialize the three-agent system for architecture analysis.
    
    Args:
        model_client: ChatCompletionClient instance for LLM communication
        
    Returns:
        list: List of initialized agents in execution order:
              [Cloud Classification Agent, Architecture Review Agent, Evaluator Agent]
    
    Agent Flow:
        1. Cloud Classification Agent identifies the target cloud platform
        2. Architecture Review Agent analyzes with platform-specific context
        3. Evaluator Agent validates and enhances the combined analysis
    """
    
    # ========================================
    # AGENT 1: CLOUD CLASSIFICATION AGENT
    # ========================================
    # Identifies the target cloud platform from architecture diagram    
    cloud_classification_agent_sys = agent_system_messages['cloud_classification_agent_sys']
    
    # ========================================
    # AGENT 2: ARCHITECTURE REVIEW AGENT
    # ========================================
    # Performs comprehensive architecture analysis with platform-specific insights
    arch_review_agent_sys = agent_system_messages['arch_review_agent_sys']

    # ========================================
    # AGENT 3: EVALUATOR AGENT
    # ========================================
    # Validates and enhances the analysis from both previous agents
    evaluator_agent_sys = agent_system_messages['evaluator_agent_sys']

    # ========================================
    # CREATE AGENT INSTANCES
    # ========================================
    cloud_classification_agent = AssistantAgent(
        "Cloud_Classification_Agent",
        model_client=model_client,
        system_message=cloud_classification_agent_sys,
    )

    arch_review_agent = AssistantAgent(
        "Architecture_Review_Agent",
        model_client=model_client,
        system_message=arch_review_agent_sys,
    )

    evaluator_agent = AssistantAgent(
        "Evaluator_Agent",
        model_client=model_client,
        system_message=evaluator_agent_sys,
    )

    # Return agents in execution order
    return [
        cloud_classification_agent,  # Step 1: Classify cloud platform
        arch_review_agent,          # Step 2: Review architecture with context
        evaluator_agent             # Step 3: Evaluate and enhance
    ]


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

async def run_analysis(tech_spec_content, arch_diagram_image):
    """
    Execute the multi-agent architecture analysis workflow.
    
    Args:
        tech_spec_content (str): Text content extracted from technical specification PDF
        arch_diagram_image: File-like object containing the architecture diagram image
        
    Returns:
        str: Combined analysis results from Architecture Review and Evaluator agents
        
    Workflow:
        1. Configure Azure OpenAI model client
        2. Initialize three-agent system
        3. Create multi-modal message with spec text and diagram image
        4. Execute round-robin group chat with agents
        5. Return final analysis results
        
    Note:
        - Uses GPT-4o model via Azure OpenAI
        - Temperature set to 0.0 for consistent, deterministic outputs
        - Max turns set to 6 to accommodate three-agent conversation
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
    # PREPARE MULTI-MODAL INPUT
    # ========================================
    # Convert uploaded image to AutogenImage format
    pil_image = Image.open(arch_diagram_image)
    img = AutogenImage(pil_image)    
    
    # Create message containing both text (spec) and image (diagram)
    multi_modal_message = MultiModalMessage(
        content=[
            f"Technical Specification Document:\n{tech_spec_content}\n\n\nAI Architecture Diagram", 
            img
        ], 
        source="user"
    )

    # ========================================
    # EXECUTE MULTI-AGENT ANALYSIS
    # ========================================
    # Configure termination condition (agents signal completion with "TERMINATE")
    termination = TextMentionTermination("TERMINATE")
    
    # Create round-robin group chat (agents take turns in order)
    # Max turns = 6 allows 2 rounds for each of the 3 agents
    group_chat = RoundRobinGroupChat(
        agents, 
        termination_condition=termination, 
        max_turns=6
    )
    
    # Run the analysis and capture results
    response = await Console(group_chat.run_stream(task=multi_modal_message))
    
    # Return the last two agent responses (Architecture Review + Evaluator)
    # -3 is Architecture Review Agent, -2 is Evaluator Agent
    return response.messages[-3].content + "\n\n" + response.messages[-2].content


# ============================================================================
# STREAMLIT UI
# ============================================================================

# Page title and description
st.title("AI - Architecture Diagram Analysis & Validation")
st.write(
    "Upload your Technical Specification Document and Architecture Diagram "
    "to get a comprehensive analysis with cloud platform classification"
)

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
    spec_file = st.file_uploader(
        "Upload Technical Specification Document (PDF)", 
        type=['pdf']
    )

with col2:
    arch_diagram_file = st.file_uploader(
        "Upload Architecture Diagram", 
        type=['png', 'jpg', 'jpeg']
    )

# ========================================
# ANALYSIS EXECUTION
# ========================================
if spec_file and arch_diagram_file:
    if st.button("Start Analysis"):
        
        # Create temporary files for processing
        # Technical specification PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_spec:
            tmp_spec.write(spec_file.getvalue())
            tmp_spec_path = tmp_spec.name
        
        # Architecture diagram image
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=os.path.splitext(arch_diagram_file.name)[1]
        ) as tmp_arch:
            tmp_arch.write(arch_diagram_file.getvalue())
            tmp_arch_path = tmp_arch.name
        
        # Extract text from specification PDF
        spec_content = read_pdf(tmp_spec_path)
        
        # Execute analysis with progress indicator
        with st.spinner("Classifying cloud platform and analyzing architecture..."):
            # Run async analysis in sync context
            final_response = asyncio.run(
                run_analysis(spec_content, arch_diagram_file)
            )
            
            # Clean up temporary files
            os.unlink(tmp_spec_path)
            os.unlink(tmp_arch_path)

            # Display results
            st.subheader("Analysis Results")
            st.markdown(final_response)