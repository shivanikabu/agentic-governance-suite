"""
LLM Utility Module
==================
A utility module providing simplified access to Azure OpenAI GPT-4o model
through LangChain integration.

Features:
- Single function interface for LLM calls
- Azure OpenAI integration via LangChain
- Environment-based configuration
- GPT-4o model access
- Simple message-response pattern

Use Cases:
- Quick prototyping with LLMs
- Simple text generation tasks
- Ad-hoc queries and analysis
- Testing and experimentation
- Integration into existing tools

Model:
- GPT-4o: Advanced reasoning and generation capabilities
- Suitable for complex tasks requiring deep understanding

Author: [Shivani Kabu & Nikhil Khandelwal]
Date: [01/12/2025]
Version: 1.0
"""

# ============================================================================
# IMPORTS
# ============================================================================
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI


# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================
# Load environment variables from .env file
# This loads Azure OpenAI credentials and configuration
load_dotenv()


# ============================================================================
# LLM UTILITY FUNCTION
# ============================================================================

def gpt_llm_call(message):
    """
    Make a single call to Azure OpenAI GPT-4o model.
    
    This is a convenience function that provides a simple interface for
    interacting with the GPT-4o model through Azure OpenAI. It handles
    environment configuration and returns the model's text response.
    
    Args:
        message (str or list): The message to send to the model
            - str: Simple text prompt
            - list: List of message dicts for conversational context
                    [{"role": "user", "content": "Your message"}]
    
    Returns:
        str: The model's text response
        
    Model Configuration:
        - Model: gpt-4o
        - Provider: Azure OpenAI
        - Temperature: Default (typically 0.7 for balanced creativity)
        - Max Tokens: Default (model's context window)
        
    Environment Variables Required:
        - AZURE_OPENAI_API_KEY: Your Azure OpenAI API key
        - AZURE_OPENAI_ENDPOINT: Your Azure OpenAI endpoint URL
        - AZURE_OPENAI_API_VERSION: API version (e.g., "2024-08-01-preview")
        
    Example Usage:
        Simple text prompt:
        >>> response = gpt_llm_call("Explain quantum computing in simple terms")
        >>> print(response)
        
        Conversational context:
        >>> messages = [
        ...     {"role": "system", "content": "You are a helpful assistant"},
        ...     {"role": "user", "content": "What is AI?"}
        ... ]
        >>> response = gpt_llm_call(messages)
        
    Note:
        - This function sets environment variables on each call
        - For production use, consider caching the LLM instance
        - No error handling is implemented; exceptions will propagate
        - Uses default model parameters (temperature, max_tokens, etc.)
        
    Limitations:
        - No streaming support
        - No token usage tracking
        - No conversation history management
        - No retry logic for transient failures
        - Environment variables set on every call (not optimal for high-frequency use)
        
    For Production Use:
        Consider using the more robust agent systems (PerformanceAgent,
        ComplianceAgent, etc.) which provide better error handling,
        logging, and configuration management.
    """
    # Set Azure OpenAI environment variables
    # Note: These are set on every call. For better performance,
    # consider setting these once at module level or caching the LLM instance
    os.environ['AZURE_OPENAI_API_KEY'] = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ['AZURE_OPENAI_ENDPOINT'] = os.getenv("AZURE_OPENAI_ENDPOINT")
    os.environ['OPENAI_API_VERSION'] = os.getenv("AZURE_OPENAI_API_VERSION")
    
    # Initialize Azure OpenAI Chat model
    # Uses GPT-4o for advanced reasoning capabilities
    llm = AzureChatOpenAI(model="gpt-4o")
    
    # Invoke the model with the provided message
    # LangChain handles the API call and response parsing
    response = llm.invoke(message)
    
    # Return the text content of the response
    return response.content


# ============================================================================
# ENHANCED UTILITY FUNCTION (OPTIONAL)
# ============================================================================

def gpt_llm_call_with_config(message, temperature=0.7, max_tokens=None):
    """
    Enhanced LLM call with configurable parameters.
    
    This is an improved version that allows customization of model parameters
    and provides better control over the generation behavior.
    
    Args:
        message (str or list): The message to send to the model
        temperature (float, optional): Controls randomness (0.0-2.0)
            - 0.0: Deterministic, focused responses
            - 0.7: Balanced (default)
            - 1.0-2.0: More creative, diverse responses
        max_tokens (int, optional): Maximum tokens in response
            - None: Use model's default
            - Specify to limit response length
    
    Returns:
        str: The model's text response
        
    Example Usage:
        # Deterministic output for consistent results
        >>> response = gpt_llm_call_with_config(
        ...     "Explain AI", 
        ...     temperature=0.0
        ... )
        
        # Creative writing
        >>> response = gpt_llm_call_with_config(
        ...     "Write a poem about technology",
        ...     temperature=1.5
        ... )
        
        # Limited response length
        >>> response = gpt_llm_call_with_config(
        ...     "Summarize quantum computing",
        ...     max_tokens=100
        ... )
    """
    # Set environment variables
    os.environ['AZURE_OPENAI_API_KEY'] = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ['AZURE_OPENAI_ENDPOINT'] = os.getenv("AZURE_OPENAI_ENDPOINT")
    os.environ['OPENAI_API_VERSION'] = os.getenv("AZURE_OPENAI_API_VERSION")
    
    # Initialize with custom parameters
    llm = AzureChatOpenAI(
        model="gpt-4o",
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    response = llm.invoke(message)
    return response.content


# ============================================================================
# SINGLETON PATTERN (RECOMMENDED FOR PRODUCTION)
# ============================================================================

class GPTLLMClient:
    """
    Singleton LLM client for efficient reuse.
    
    This class implements a singleton pattern to avoid reinitializing
    the LLM client on every call, improving performance for high-frequency use.
    
    Example Usage:
        >>> client = GPTLLMClient.get_instance()
        >>> response1 = client.call("First question")
        >>> response2 = client.call("Second question")
    """
    
    _instance = None
    _llm = None
    
    @classmethod
    def get_instance(cls):
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the LLM client."""
        if GPTLLMClient._instance is not None:
            raise Exception("This is a singleton class. Use get_instance()")
        
        # Set environment variables once
        os.environ['AZURE_OPENAI_API_KEY'] = os.getenv("AZURE_OPENAI_API_KEY")
        os.environ['AZURE_OPENAI_ENDPOINT'] = os.getenv("AZURE_OPENAI_ENDPOINT")
        os.environ['OPENAI_API_VERSION'] = os.getenv("AZURE_OPENAI_API_VERSION")
        
        # Initialize LLM once
        self._llm = AzureChatOpenAI(model="gpt-4o")
    
    def call(self, message, temperature=0.7, max_tokens=None):
        """
        Make an LLM call using the cached client.
        
        Args:
            message (str or list): Message to send
            temperature (float): Controls randomness
            max_tokens (int): Maximum response tokens
            
        Returns:
            str: Model response
        """
        # Update parameters if needed
        if temperature != 0.7 or max_tokens is not None:
            self._llm.temperature = temperature
            if max_tokens:
                self._llm.max_tokens = max_tokens
        
        response = self._llm.invoke(message)
        return response.content


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Example Usage Patterns:

# Example 1: Simple query
response = gpt_llm_call("What is machine learning?")
print(response)

# Example 2: With conversation context
messages = [
    {"role": "system", "content": "You are a Python expert"},
    {"role": "user", "content": "Explain list comprehensions"}
]
response = gpt_llm_call(messages)

# Example 3: Using enhanced version with custom temperature
response = gpt_llm_call_with_config(
    "Generate creative ideas for a tech startup",
    temperature=1.2
)

# Example 4: Deterministic output for testing
response = gpt_llm_call_with_config(
    "Summarize this text: ...",
    temperature=0.0
)

# Example 5: Using singleton for multiple calls (recommended)
client = GPTLLMClient.get_instance()
response1 = client.call("First question")
response2 = client.call("Second question")
response3 = client.call("Third question")

# Example 6: Error handling wrapper
def safe_llm_call(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            return gpt_llm_call(message)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Retry {attempt + 1}/{max_retries} after error: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

# Example 7: Integration with other tools
def analyze_with_llm(data):
    prompt = f"Analyze this data and provide insights: {data}"
    analysis = gpt_llm_call(prompt)
    return analysis
"""