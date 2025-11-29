"""
AI-Agents Enterprise Toolkit - Main Application
================================================
A comprehensive Streamlit application for managing AI agents across three categories:
1. Governance Oversight Agents - For compliance, performance, and prompt assessment
2. SDLC Guarding Agents - For software development lifecycle support
3. Trajectory Analysis Agents - For analyzing AI agent trajectories

Author: [Shivani Kabu & Nikhil Khandelwal]
Date: [01/07/2025]
Version: 1.0
"""

# ============================================================================
# IMPORTS
# ============================================================================
import sys
import os
import importlib.util
import streamlit as st

# Add parent directory to path for module imports
sys.path.append("../")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def import_module_from_file(module_name, file_path):
    """
    Dynamically import a Python module from a file path.
    
    Args:
        module_name (str): Name to assign to the imported module
        file_path (str): Path to the Python file to import
        
    Returns:
        module: The imported module object, or None if import fails
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def display_coming_soon(agent_name):
    """
    Display a 'Coming Soon' page for agents not yet implemented.
    
    Args:
        agent_name (str): Name of the agent to display in the coming soon message
    """
    st.markdown(f"""
    <div class="coming-soon">
        <div class="coming-soon-icon">🚀</div>
        <h1>COMING SOON!!</h1>
        <p>{agent_name} will be available in future releases</p>
        <p style="margin-top: 30px; font-size: 1.2rem;">Stay tuned for exciting updates! 🎉</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="AI-Agents Enterprise Toolkit",
    page_icon="🧰",
    layout="wide"
)


# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
st.markdown("""
<style>
    /* Import modern font family */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* ========================================
       SIDEBAR STYLING
       ======================================== */
    
    /* Dark theme sidebar background with gradient */
    .stSidebar > div:first-child {
        background: linear-gradient(180deg, #1a1d23 0%, #252a34 100%) !important;
        border-right: 1px solid #404040 !important;
    }
    
    /* Sidebar text styling with Inter font */
    .stSidebar .stMarkdown, .stSidebar .stSelectbox label, .stSidebar .stTextInput label {
        color: #e8eaed !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar header text styling */
    .stSidebar h2, .stSidebar h3 {
        color: #ffffff !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* ========================================
       SECTION HEADERS
       ======================================== */
    
    /* Governance Agents section header - Blue theme */
    .governance-header {
        color: #64b5f6 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 12px !important;
        padding: 8px 0 !important;
        border-bottom: 1px solid rgba(100, 181, 246, 0.2) !important;
    }
    
    /* SDLC Agents section header - Green theme */
    .sdlc-header {
        color: #81c784 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 12px !important;
        padding: 8px 0 !important;
        border-bottom: 1px solid rgba(129, 199, 132, 0.2) !important;
    }
    
    /* Trajectory Analysis section header - Orange theme */
    .trajectory-header {    
        color: #ff9800 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 12px !important;
        padding: 8px 0 !important;
        border-bottom: 1px solid rgba(255, 152, 0, 0.2) !important;
    }
    
    /* ========================================
       BUTTON STYLING
       ======================================== */
    
    /* Default sidebar button styling */
    .stSidebar .stButton > button {
        background: linear-gradient(135deg, #404040 0%, #2d2d2d 100%) !important;
        color: #e8eaed !important;
        border: 1px solid #555555 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Button hover effect */
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #505050 0%, #3d3d3d 100%) !important;
        border-color: #666666 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Primary (selected) button styling */
    .stSidebar .stButton > button[data-baseweb="button"][kind="primary"] {
        background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 100%) !important;
        color: #ffffff !important;
        border: 1px solid #64b5f6 !important;
        box-shadow: 0 3px 6px rgba(100, 181, 246, 0.3) !important;
    }
    
    /* Primary button hover effect */
    .stSidebar .stButton > button[data-baseweb="button"][kind="primary"]:hover {
        background: linear-gradient(135deg, #42a5f5 0%, #2196f3 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(100, 181, 246, 0.4) !important;
    }
    
    /* ========================================
       INPUT FIELDS
       ======================================== */
    
    /* Sidebar text input styling */
    .stSidebar .stTextInput > div > div > input {
        background-color: #2d2d2d !important;
        color: #e8eaed !important;
        border: 1px solid #555555 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        border-radius: 6px !important;
    }
    
    /* Input field focus state */
    .stSidebar .stTextInput > div > div > input:focus {
        border-color: #64b5f6 !important;
        box-shadow: 0 0 0 2px rgba(100, 181, 246, 0.2) !important;
    }
    
    /* ========================================
       OTHER SIDEBAR ELEMENTS
       ======================================== */
    
    /* Sidebar divider styling */
    .stSidebar hr {
        border-color: #404040 !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Success messages in sidebar */
    .stSidebar .stSuccess {
        background: linear-gradient(135deg, rgba(129, 199, 132, 0.15) 0%, rgba(76, 175, 80, 0.1) 100%) !important;
        color: #81c784 !important;
        border: 1px solid rgba(129, 199, 132, 0.3) !important;
        border-radius: 8px !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Info messages in sidebar */
    .stSidebar .stInfo {
        background: linear-gradient(135deg, rgba(100, 181, 246, 0.15) 0%, rgba(33, 150, 243, 0.1) 100%) !important;
        color: #64b5f6 !important;
        border: 1px solid rgba(100, 181, 246, 0.3) !important;
        border-radius: 8px !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Expander styling for jury credentials */
    .stSidebar .stExpander {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%) !important;
        border: 1px solid rgba(255, 152, 0, 0.3) !important;
        border-radius: 8px !important;
        margin: 15px 0 !important;
    }
    
    .stSidebar .stExpander > details > summary {
        color: #ff9800 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        background: transparent !important;
        border: none !important;
    }
    
    .stSidebar .stExpander > details > summary:hover {
        background: rgba(255, 152, 0, 0.1) !important;
    }
    
    /* ========================================
       MAIN CONTENT AREA
       ======================================== */
    
    /* Main content font styling */
    .main .block-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Main title styling */
    h1 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* ========================================
       COMING SOON PAGE
       ======================================== */
    
    /* Coming Soon container styling */
    .coming-soon {
        text-align: center;
        padding: 100px 50px;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
        border-radius: 20px;
        margin: 50px 0;
        border: 2px solid rgba(255, 152, 0, 0.3);
    }
    
    /* Coming Soon title with animation */
    .coming-soon h1 {
        font-size: 4rem !important;
        font-weight: 700 !important;
        color: #ff9800 !important;
        margin-bottom: 20px !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: pulse 2s infinite;
    }
    
    /* Coming Soon description text */
    .coming-soon p {
        font-size: 1.5rem !important;
        color: #ff9800 !important;
        opacity: 0.8;
        margin-top: 20px !important;
    }
    
    /* Coming Soon icon */
    .coming-soon-icon {
        font-size: 5rem;
        margin-bottom: 30px;
        display: block;
    }
    
    /* Pulse animation for Coming Soon title */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
# Initialize all session state variables if they don't exist

# API credentials for main LLM
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

if 'endpoint' not in st.session_state:
    st.session_state.endpoint = ""

# API credentials for jury model (used in specific agents)
if 'jury_api_key' not in st.session_state:
    st.session_state.jury_api_key = ""

if 'jury_endpoint' not in st.session_state:
    st.session_state.jury_endpoint = ""

# Selected application state
if 'selected_app' not in st.session_state:
    st.session_state.selected_app = None

# Section-specific selections for maintaining UI state
if 'governance_selection' not in st.session_state:
    st.session_state.governance_selection = None

if 'sdlc_selection' not in st.session_state:
    st.session_state.sdlc_selection = None

if 'trajectory_selection' not in st.session_state:
    st.session_state.trajectory_selection = None

# Track which section is currently active
if 'active_section' not in st.session_state:
    st.session_state.active_section = None


# ============================================================================
# MAIN TITLE
# ============================================================================
st.markdown("<h1 style='text-align: center;'>AI-Agents Enterprise Toolkit</h1>", unsafe_allow_html=True)


# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================
with st.sidebar:
    st.header("Configuration")
    
    # ========================================
    # API CREDENTIALS INPUT
    # ========================================
    
    # Main LLM API Key input
    api_key = st.text_input("🔑 LLM API Key", type="password", value=st.session_state.api_key)
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
        # Set environment variables for Azure OpenAI
        os.environ["AZURE_API_KEY"] = api_key
        os.environ["AZURE_OPENAI_API_KEY"] = api_key
    
    # Main LLM Endpoint input
    endpoint = st.text_input("🌐 LLM Endpoint", value=st.session_state.endpoint)
    if endpoint != st.session_state.endpoint:
        st.session_state.endpoint = endpoint
        os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint

    # Jury Model Credentials (optional, expandable)
    with st.expander("⚖️ Jury Model Credentials", expanded=False):
        jury_api_key = st.text_input(
            "🔑 Jury LLM API Key", 
            type="password", 
            value=st.session_state.jury_api_key, 
            key="jury_api_input"
        )
        if jury_api_key != st.session_state.jury_api_key:
            st.session_state.jury_api_key = jury_api_key
            os.environ["JURY_AZURE_API_KEY"] = jury_api_key
            os.environ["JURY_AZURE_OPENAI_API_KEY"] = jury_api_key
        
        jury_endpoint = st.text_input(
            "🌐 Jury LLM Endpoint", 
            value=st.session_state.jury_endpoint, 
            key="jury_endpoint_input"
        )
        if jury_endpoint != st.session_state.jury_endpoint:
            st.session_state.jury_endpoint = jury_endpoint
            os.environ["JURY_AZURE_OPENAI_ENDPOINT"] = jury_endpoint

    # ========================================
    # GOVERNANCE AGENTS SECTION
    # ========================================
    st.markdown('<p class="governance-header">🏛️ Governance Oversight Agents</p>', unsafe_allow_html=True)
    
    governance_options = [
        "CoreOps Agent",
        "Prompt Assessment Agent", 
        "Performance Agent",
        "Compliance Agent"
    ]
    
    # Create buttons for each governance agent
    governance_cols = st.columns(1)
    with governance_cols[0]:
        for i, option in enumerate(governance_options):
            if st.button(
                option, 
                key=f"gov_btn_{i}",
                use_container_width=True,
                type="primary" if st.session_state.governance_selection == option else "secondary"
            ):
                # Clear other section selections when governance is selected
                st.session_state.sdlc_selection = None
                st.session_state.trajectory_selection = None
                # Set governance selection
                st.session_state.governance_selection = option
                st.session_state.selected_app = option
                st.session_state.active_section = "governance"
                st.rerun()
    
    st.divider()
    
    # ========================================
    # SDLC AGENTS SECTION
    # ========================================
    st.markdown('<p class="sdlc-header">⚙️ SDLC Guarding Agent</p>', unsafe_allow_html=True)
    
    sdlc_options = [
        "Technical Specs Analysis",
        "Architecture Evaluation",
        "Code Evals",
        "Test Coverage",
        "Documentation Generation"
    ]
    
    # Create buttons for each SDLC agent
    sdlc_cols = st.columns(1)
    with sdlc_cols[0]:
        for i, option in enumerate(sdlc_options):
            if st.button(
                option,
                key=f"sdlc_btn_{i}",
                use_container_width=True,
                type="primary" if st.session_state.sdlc_selection == option else "secondary"
            ):
                # Clear other section selections when SDLC is selected
                st.session_state.governance_selection = None
                st.session_state.trajectory_selection = None
                # Set SDLC selection
                st.session_state.sdlc_selection = option
                st.session_state.selected_app = option
                st.session_state.active_section = "sdlc"
                st.rerun()

    st.divider()
    
    # ========================================
    # TRAJECTORY AGENTS SECTION
    # ========================================
    st.markdown('<p class="trajectory-header">🚀 Trajectory Analysis Agent</p>', unsafe_allow_html=True)
    
    trajectory_options = [
        "Trajectory Observer Agent",
        "Trajectory Optimizing Agent",
    ]
    
    # Create buttons for each trajectory agent
    trajectory_cols = st.columns(1)
    with trajectory_cols[0]:
        for i, option in enumerate(trajectory_options):
            if st.button(
                option,
                key=f"trajectory_btn_{i}",
                use_container_width=True,
                type="primary" if st.session_state.trajectory_selection == option else "secondary"
            ):
                # Clear other section selections when trajectory is selected
                st.session_state.governance_selection = None
                st.session_state.sdlc_selection = None
                # Set trajectory selection
                st.session_state.trajectory_selection = option
                st.session_state.selected_app = option
                st.session_state.active_section = "trajectory"
                st.rerun()

    # ========================================
    # SELECTION STATUS DISPLAY
    # ========================================
    st.divider()
    
    if st.session_state.selected_app:
        st.success(f"**Selected:** {st.session_state.selected_app}")
    else:
        st.info("Please select an agent to begin")


# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

# Check if API credentials are provided
if st.session_state.api_key and st.session_state.endpoint:
    
    if st.session_state.selected_app:
        # ========================================
        # LOAD AND DISPLAY SELECTED AGENT
        # ========================================
        
        # Governance Agents
        if st.session_state.selected_app == "CoreOps Agent":  
            try:
                coreops_agent_app = import_module_from_file(
                    "Governance.st_coreops_agent", 
                    "Governance/st_coreops_agent.py"
                )
            except Exception as e:
                st.error(f"Error loading CoreOps Agent: {str(e)}")

        elif st.session_state.selected_app == "Prompt Assessment Agent":  
            try:
                prompt_agent_app = import_module_from_file(
                    "Governance.st_prompt_assessment_agent", 
                    "Governance/st_prompt_assessment_agent.py"
                )
            except Exception as e:
                st.error(f"Error loading Prompt Assessment Agent: {str(e)}")

        elif st.session_state.selected_app == "Performance Agent":  
            try:
                performance_agent_app = import_module_from_file(
                    "Governance.st_performance_agent", 
                    "Governance/st_performance_agent.py"
                )
            except Exception as e:
                st.error(f"Error loading Performance Agent: {str(e)}")

        elif st.session_state.selected_app == "Compliance Agent":  
            try:
                compliance_agent_app = import_module_from_file(
                    "Governance.st_compliance_agent", 
                    "Governance/st_compliance_agent.py"
                )
            except Exception as e:
                st.error(f"Error loading Compliance Agent: {str(e)}")

        # SDLC Agents
        elif st.session_state.selected_app == "Architecture Evaluation":
            try:
                architecture_agent_app = import_module_from_file(
                    "Auditor.architecture_agent", 
                    "Auditor/architecture_agent.py"
                )
            except Exception as e:
                st.error(f"Error loading Architecture Evaluation Agent: {str(e)}")
        
        elif st.session_state.selected_app == "Technical Specs Analysis":
            try:
                tech_specs_agent_app = import_module_from_file(
                    "Auditor.tech_specs_agent", 
                    "Auditor/tech_specs_agent.py"
                )
            except Exception as e:
                st.error(f"Error loading Technical Specs Analysis Agent: {str(e)}")
        
        elif st.session_state.selected_app == "Code Evals":
            try:
                code_review_agent_app = import_module_from_file(
                    "Auditor.code_reviewer", 
                    "Auditor/code_reviewer.py"
                )
            except Exception as e:
                st.error(f"Error loading Code Evals Agent: {str(e)}")

        elif st.session_state.selected_app == "Test Coverage":
            try:
                test_coverage_agent_app = import_module_from_file(
                    "Auditor.test_coverage", 
                    "Auditor/test_coverage.py"
                )
            except Exception as e:
                st.error(f"Error loading Test Coverage Agent: {str(e)}")

        elif st.session_state.selected_app == "Documentation Generation":
            try:
                doc_gen_agent_app = import_module_from_file(
                    "Auditor.document_generation", 
                    "Auditor/document_generation.py"
                )
            except Exception as e:
                st.error(f"Error loading Documentation Generation Agent: {str(e)}")

        # Trajectory Agents
        elif st.session_state.selected_app == "Trajectory Observer Agent":
            try:
                trajectory_observer_app = import_module_from_file(
                    "Trajectory.trajectory_observer", 
                    "Trajectory/trajectory_observer.py"
                )
            except Exception as e:
                st.error(f"Error loading Trajectory Observer Agent: {str(e)}")

        elif st.session_state.selected_app == "Trajectory Optimizing Agent":
            try:
                trajectory_optimizing_app = import_module_from_file(
                    "Trajectory.trajectory_optimizing", 
                    "Trajectory/trajectory_optimizing.py"
                )
            except Exception as e:
                st.error(f"Error loading Trajectory Optimizing Agent: {str(e)}")
    
    else:
        # ========================================
        # WELCOME PAGE (No agent selected)
        # ========================================
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h2>Welcome to AI-Agents Enterprise Toolkit</h2>
            <p style='font-size: 18px; color: #666;'>
                Select an agent from the sidebar to get started with your enterprise AI workflows.
            </p>
            <br>
            <div style='display: flex; justify-content: center; gap: 30px; margin-top: 30px;'>
                <div style='text-align: center;'>
                    <h3>🏛️ Governance Agents</h3>
                    <p>Manage AI governance, compliance, and performance monitoring</p>
                </div>
                <div style='text-align: center;'>
                    <h3>⚙️ SDLC Agents</h3>
                    <p>Support software development lifecycle with AI-powered tools</p>
                </div>
                <div style='text-align: center;'>
                    <h3>🚀 Trajectory Agents</h3>
                    <p>Analyze and evaluate AI agent trajectories and performance</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # ========================================
    # CONFIGURATION REQUIRED PAGE
    # ========================================
    st.warning("Please enter your LLM API Key and Endpoint in the sidebar to use the applications.")
    
    # Show configuration help
    with st.expander("Configuration Help"):
        st.markdown("""
        **Required Configuration:**
        
        1. **LLM API Key**: Your API key for the language model service
        2. **LLM Endpoint**: The endpoint URL for your language model service
        
        **Optional Configuration:**
        
        - **Jury Model Credentials**: Some agents use a separate "jury" model for evaluation
          - These can be configured in the expandable section in the sidebar
        
        Once both required fields are filled, you can select and use any of the available agents.
        
        **Available Agent Categories:**
        
        - **Governance Oversight Agents**: CoreOps, Prompt Assessment, Performance, and Compliance
        - **SDLC Guarding Agents**: Technical Specs, Architecture, Code Review, Testing, and Documentation
        - **Trajectory Analysis Agents**: Observer and Optimization agents for AI trajectories
        """)