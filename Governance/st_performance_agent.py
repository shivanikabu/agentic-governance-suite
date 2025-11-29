"""
Performance Agent Application
=============================
A Streamlit application for AI governance and performance assessment.
Evaluates AI responses against key metrics including hallucination detection, accuracy,
consistency, latency, failure rate, and protected material checks to ensure responsible
AI deployment.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import sys
sys.path.append("../")  # Add parent directory to Python path for module imports

import asyncio
import time
import streamlit as st
from Governance.PerformanceAgent import start_agent_pipeline


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
# Configure the main page title
st.markdown(
    "<h1 style='font-size: 32px; text-align: center;'>Performance Agent</h1>",
    unsafe_allow_html=True
)

# Display application description and instructions
# Note: Fixed typo in original text (removed stray 's' before 'Select')
st.markdown("""
This platform enables AI governance and responsible AI assessment by analyzing agentic 
architectures and chatbot interactions. Users can upload a log file and describe their 
agentic system to initiate the evaluation process.  

This assessment is conducted using a specialized agent:

**Performance Assessment Agent** – The Performance Assessment Agent systematically 
evaluates AI responses against key metrics such as hallucination detection, accuracy, 
consistency, latency, failure rate, and protected material checks. It provides structured 
performance reports, highlighting critical insights and improvement areas for responsible 
AI deployment.

Select a log file, provide a brief architecture description (optional), and run the 
assessment to receive an in-depth analysis of AI agent performance.
""", unsafe_allow_html=True)


# ============================================================================
# LAYOUT CONFIGURATION
# ============================================================================
# Create three-column layout: input selection (left), spacer (middle), description (right)
col1, spacer, col2 = st.columns([1, 0.3, 2])


# ============================================================================
# LEFT PANE - LOG FILE SELECTION
# ============================================================================
with col1:
    # Add vertical spacing
    st.write("\n\n\n")
    
    # Log file selection dropdown
    st.markdown(
        "<p style='font-size: 24px; font-weight: bold;'>Select a log file for analysis</p>",
        unsafe_allow_html=True
    )
    option = st.selectbox(
        label='',  # Empty label as header is defined above
        options=(
            'Session_id_1.json',
            'Session_id_2.json'
        )
    )


# ============================================================================
# RIGHT PANE - ARCHITECTURE DESCRIPTION
# ============================================================================
with col2:
    # Add vertical spacing to align with left pane
    st.write("\n\n\n")
    
    # Architecture description input
    st.markdown(
        "<p style='font-size: 24px; font-weight: bold;'>Enter a description of Agentic Architecture</p>",
        unsafe_allow_html=True
    )
    description = st.text_area(label="")


# ============================================================================
# VISUAL SEPARATOR
# ============================================================================
# Add vertical line separator between left and right panes
with spacer:
    st.markdown("""
    <div style="border-left: 2px solid #D3D3D3; height: 100%; margin-left: 20px;"></div>
    """, unsafe_allow_html=True)


# ============================================================================
# ASSESSMENT BUTTON STYLING
# ============================================================================
# Apply custom CSS to increase button font size
st.markdown(
    """
    <style>
    div.stButton > button {
        font-size: 40px !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================================
# ASSESSMENT EXECUTION
# ============================================================================
if st.button("Run Assessment"):
    # Create placeholder for status updates
    status_placeholder = st.empty()
    
    # Display progress message
    status_placeholder.markdown(
        "<p style='font-size: 20px;'>Assessment Evaluation in progress ...</p>",
        unsafe_allow_html=True
    )
    
    # Simulate processing time (can be removed if not needed)
    time.sleep(3)
    
    # Clear status message
    status_placeholder.empty()
    
    # Execute the Performance agent pipeline asynchronously
    # Passes selected log file and architecture description to the agent
    agents_response = asyncio.run(start_agent_pipeline(f'data/{option}', description))
    
    # Display performance assessment results
    st.write(agents_response)