"""
Automated Test Coverage Analysis Tool
======================================
A Streamlit-based tool that analyzes GitHub repositories for test coverage
using Repomix and LLM-powered insights.

Test Coverage Analysis Includes:
- Identification of untested components and modules
- Suggestions for additional test cases
- Test quality assessment
- Testing strategy recommendations
- Gap analysis in current test suite

Additional Capabilities:
- Code Review (architecture, security, performance, dependencies, quality)
- Documentation Generation (API docs, developer guides, architecture)

Features:
- GitHub repository integration via Repomix
- LLM-powered test coverage analysis using Azure OpenAI GPT-4o
- Comprehensive test gap identification
- Testing strategy recommendations
- Analysis history tracking

Author: [Shivani Kabu & Nikhil Khandelwal]
Date: [01/12/2025]
Version: 1.0
"""

# ============================================================================
# IMPORTS
# ============================================================================
import streamlit as st
import subprocess
import re
import os
from dotenv import load_dotenv
from Auditor.system_messages import agent_system_messages
# LangChain imports for LLM integration
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================
# Load environment variables from .env file
load_dotenv()

# Set Azure OpenAI credentials from environment
os.environ['AZURE_OPENAI_API_KEY'] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ['AZURE_OPENAI_ENDPOINT'] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ['OPENAI_API_VERSION'] = os.getenv("AZURE_OPENAI_API_VERSION")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_valid_github_url(url):
    """
    Validate GitHub repository URL format.
    
    Args:
        url (str): GitHub repository URL to validate
        
    Returns:
        bool: True if URL matches GitHub repository pattern, False otherwise
        
    Valid Formats:
        - https://github.com/username/repository
        - http://github.com/username/repository
        - https://github.com/username/repository/
        
    Invalid Formats:
        - github.com/username/repository (missing protocol)
        - https://github.com/username (missing repository)
        - https://gitlab.com/username/repo (different platform)
    """
    pattern = r'^https?://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9._-]+(/)?$'
    return re.match(pattern, url) is not None


def run_repomix(github_url):
    """
    Execute Repomix CLI to convert GitHub repository into XML format.
    
    Repomix aggregates the entire repository structure and source code
    into a single XML file optimized for LLM processing and analysis.
    
    Args:
        github_url (str): Valid GitHub repository URL
        
    Returns:
        tuple: (success: bool, message: str)
            - success: True if Repomix executed successfully
            - message: stdout on success, error message on failure
            
    Output:
        Creates 'repomix-output.xml' in the current directory containing:
        - Complete file structure
        - All source code files
        - Configuration files
        - Documentation files
        
    Requirements:
        - Node.js installed on the system
        - Repomix CLI installed globally or at specified path
        
    System-Specific Configuration:
        Update repomix_cli path based on your system:
        - Linux/macOS: /path/to/.nvm/versions/node/vX.X.X/bin/repomix
        - Windows: C:\\Users\\Username\\AppData\\Roaming\\npm\\node_modules\\repomix\\bin\\repomix.cjs
    """
    try:
        # Repomix CLI path configuration
        # Windows path (commented):
        # repomix_cli = r"C:\Users\NikhilKhandelwal3\AppData\Roaming\npm\node_modules\repomix\bin\repomix.cjs"
        
        # Linux path (active):
        repomix_cli = r"/home/ubuntu/.nvm/versions/node/v22.16.0/bin/repomix"

        # Execute Repomix with remote repository flag
        result = subprocess.run([
            "node",              # Node.js executable
            repomix_cli,         # Repomix CLI script path
            "--remote",          # Flag to process remote repository
            github_url,          # GitHub repository URL
        ], check=True, capture_output=True, text=True)
        
        return True, result.stdout
        
    except subprocess.CalledProcessError as e:
        # Repomix execution failed (non-zero exit code)
        return False, f"Error executing repomix: {e.stderr}"
    
    except FileNotFoundError:
        # Node.js or Repomix CLI not found in system PATH
        return False, "Error: 'repomix' command not found."


def read_xml_file(file_path):
    """
    Read and return content from XML file generated by Repomix.
    
    Args:
        file_path (str): Path to the XML file (typically 'repomix-output.xml')
        
    Returns:
        str or None: XML file content if exists, None otherwise
        
    Note:
        The XML file contains structured representation of the entire codebase,
        making it ideal for LLM analysis of test coverage, architecture, etc.
    """
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return None


# ============================================================================
# PROMPT GENERATION
# ============================================================================

def get_prompt(task_type):
    """
    Generate LLM prompt template based on selected analysis task.
    
    Args:
        task_type (str): Type of analysis to perform
            - "Code Review": Comprehensive code analysis
            - "Test Coverage": Test coverage and gap analysis (default for this tool)
            - "Documentation Generation": Generate project documentation
            
    Returns:
        ChatPromptTemplate: Configured LangChain prompt template
        
    Raises:
        ValueError: If task_type is not recognized
        
    Note:
        Each prompt is carefully structured to guide the LLM toward
        producing actionable, detailed analysis with specific file references.
    """
    
    # ========================================
    # CODE REVIEW PROMPT
    # ========================================
    if task_type == "Code Review":
        return ChatPromptTemplate.from_template(agent_system_messages['code_reviewer_agent_sys'])
    
    # ========================================
    # TEST COVERAGE PROMPT (Primary for this tool)
    # ========================================
    elif task_type == "Test Coverage":
        return ChatPromptTemplate.from_template(agent_system_messages['test_coverage_agent_sys'])
    
    # ========================================
    # DOCUMENTATION GENERATION PROMPT
    # ========================================
    elif task_type == "Documentation Generation":
        return ChatPromptTemplate.from_template(agent_system_messages['documentation_agent_sys'])

    else:
        raise ValueError(f"Unknown task type: {task_type}")


# ============================================================================
# LLM ANALYSIS
# ============================================================================

def analyze_with_llm(xml_content, task_type):
    """
    Analyze codebase XML using Azure OpenAI LLM.
    
    Args:
        xml_content (str): XML representation of codebase from Repomix
        task_type (str): Type of analysis to perform
        
    Returns:
        str: LLM-generated analysis results
        
    Process:
        1. Retrieve appropriate prompt template for the task
        2. Initialize Azure OpenAI GPT-4o model
        3. Create LangChain processing chain (prompt | LLM)
        4. Invoke the chain with XML content
        5. Extract and return the text response
        
    Model Selection:
        GPT-4o is used for:
        - Superior code understanding and analysis
        - Better pattern recognition in test suites
        - More accurate gap identification
        - Comprehensive testing strategy recommendations
    """
    # Get task-specific prompt template
    prompt = get_prompt(task_type)

    # Initialize Azure OpenAI model
    # GPT-4o provides advanced reasoning for test coverage analysis
    llm = AzureChatOpenAI(model="gpt-4o")
    
    # Create LangChain processing chain
    # The | operator chains prompt formatting with LLM invocation
    chain = prompt | llm
    
    # Execute analysis
    response = chain.invoke({"xml_content": xml_content})
    
    return response.content


# ============================================================================
# STREAMLIT UI
# ============================================================================

# ========================================
# CONFIGURATION
# ========================================
# Set the default task type for this tool
task_type = "Test Coverage"

# ========================================
# PAGE HEADER
# ========================================
st.title(f"{task_type} Tool")
st.write(
    f"Enter a GitHub repository URL to analyze the codebase for **{task_type.lower()}**."
)

# ========================================
# INPUT SECTION
# ========================================
github_url = st.text_input(
    "GitHub Repository URL", 
    placeholder="https://github.com/username/repository"
)

# ========================================
# ANALYSIS EXECUTION
# ========================================
if st.button(f"Run {task_type}"):
    # Validate user input
    if not github_url:
        st.error("GitHub URL is required.")
    elif not is_valid_github_url(github_url):
        st.error("Please enter a valid GitHub URL (e.g., https://github.com/username/repository).")
    else:
        # Step 1: Execute Repomix to generate XML
        with st.spinner("Running Repomix analysis..."):
            success, output = run_repomix(github_url)

        if success:
            st.success(f"{task_type} XML generated successfully!")

            # Step 2: Read the generated XML file
            xml_path = "repomix-output.xml"
            xml_content = read_xml_file(xml_path)

            if xml_content:
                # Step 3: Analyze with LLM
                with st.spinner("Analyzing test coverage with LLM..."):
                    analysis = analyze_with_llm(xml_content, task_type)
                
                # Step 4: Display results
                st.markdown(f"### {task_type} Analysis")
                st.markdown(analysis)
            else:
                st.warning("repomix-output.xml file not found.")
        else:
            # Display Repomix execution error
            st.error(output)

# ========================================
# HISTORY TRACKER
# ========================================
# Initialize session state for URL history
if 'history' not in st.session_state:
    st.session_state.history = []

# Add current URL to history (avoid consecutive duplicates)
if github_url and (not st.session_state.history or github_url != st.session_state.history[-1]):
    st.session_state.history.append(github_url)

# Display history in expandable section
if st.session_state.history:
    with st.expander("Previous URLs"):
        # Show most recent URLs first
        for url in reversed(st.session_state.history):
            st.write(url)