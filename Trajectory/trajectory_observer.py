"""
Agent & Tool Trajectory Visualizer
===================================
A Streamlit-based tool for visualizing and analyzing agent interaction trajectories
from JSON interaction logs.

Features:
- Trajectory Extraction: Identifies conversation flows starting from User messages
- Visual Graph Representation: Creates directed graphs showing agent interaction paths
- Metrics Analysis: Summarizes token usage, cost, and latency per trajectory
- Multi-Trajectory Support: Handles multiple conversation threads in one session

Trajectory Definition:
A trajectory is a sequence of agent interactions that starts with a "User" message
and continues until the next "User" message is encountered. This helps visualize
the flow of information through different agents and tools.

Use Cases:
- Debugging multi-agent workflows
- Analyzing agent interaction patterns
- Monitoring system performance and costs
- Optimizing agent routing decisions

Author: [Shivani Kabu & Nikhil Khandelwal]
Date: [01/12/2025]
Version: 1.0
"""

# ============================================================================
# IMPORTS
# ============================================================================
import streamlit as st
import json
import pandas as pd
from graphviz import Digraph


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.title("🤖 Agent & Tool Trajectory Visualizer")
st.markdown("""
Upload a `.json` interaction log.  
This app will identify and visualize agent/tool **trajectories** starting from `User` 
and ending before the next `User`, and summarize token usage and cost.
""")

# File upload widget
uploaded_file = st.file_uploader("📁 Upload interaction JSON file", type="json")


# ============================================================================
# TRAJECTORY EXTRACTION
# ============================================================================

def extract_trajectories(json_data):
    """
    Extract agent interaction trajectories from JSON log data.
    
    A trajectory is defined as a sequence of agent interactions that:
    - Starts with a "User" message
    - Continues through various agents/tools
    - Ends when the next "User" message is encountered
    
    Args:
        json_data (list): List of message entry dictionaries from interaction log
        
    Returns:
        tuple: (trajectories, all_trajectory_blocks)
            - trajectories: List of agent name sequences (e.g., ["User", "Agent1", "Agent2"])
            - all_trajectory_blocks: List of corresponding message entry blocks
            
    Process:
        1. Iterate through all message entries
        2. When "User" is encountered, start a new trajectory
        3. Track agents via 'source' and 'next_speaker' fields
        4. Store both agent names and full message entries
        5. Clean and validate trajectories before returning
        
    Message Entry Structure:
        {
            "source": "AgentName",           # Current speaker
            "content": {                      # May be dict or JSON string
                "next_speaker": "NextAgent"   # Who speaks next
            },
            ...
        }
    """
    st.write("🔍 Starting trajectory extraction...")

    # Storage for results
    trajectories = []              # List of agent name sequences
    all_trajectory_blocks = []     # List of full message entry blocks
    
    # Current trajectory being built
    current_trajectory = []        # Current agent name sequence
    current_block = []            # Current message entry block
    user_count = 0                # Counter for User messages

    # Iterate through all entries in the log
    for i, entry in enumerate(json_data):
        # Skip non-dictionary entries
        if not isinstance(entry, dict):
            continue

        # Extract source (current speaker)
        source = entry.get("source", "").strip()
        
        # Extract and parse content (may be dict or JSON string)
        content_raw = entry.get("content", None)
        content_json = {}

        # Parse content based on its type
        if isinstance(content_raw, dict):
            content_json = content_raw
        elif isinstance(content_raw, str):
            try:
                content_json = json.loads(content_raw)
                if not isinstance(content_json, dict):
                    content_json = {}
            except json.JSONDecodeError:
                content_json = {}
        else:
            content_json = {}

        # Extract next_speaker from content
        next_speaker = content_json.get("next_speaker", "").strip()

        # Check if this is a User message (trajectory boundary)
        if source.lower() == "user":
            user_count += 1
            
            # Save previous trajectory if it exists
            if current_trajectory:
                trajectories.append(current_trajectory)
                all_trajectory_blocks.append(current_block)
            
            # Start new trajectory
            current_trajectory = ["User"]
            current_block = [entry]
            
            # Add next speaker if present
            if next_speaker:
                current_trajectory.append(next_speaker)
        else:
            # Continue building current trajectory
            if current_trajectory:
                # Add source agent if not already in trajectory
                if source and source not in current_trajectory:
                    current_trajectory.append(source)
                
                # Add next_speaker if not already in trajectory
                if next_speaker and next_speaker not in current_trajectory:
                    current_trajectory.append(next_speaker)
                
                # Add entry to current block
                current_block.append(entry)

    # Don't forget the last trajectory
    if current_trajectory:
        trajectories.append(current_trajectory)
        all_trajectory_blocks.append(current_block)

    # Clean trajectories: keep only those that start with "User" and have more than 1 node
    cleaned_trajectories = [
        t for t in trajectories if len(t) > 1 and t[0].lower() == "user"
    ]

    # Display extraction results
    st.write(f"✅ Found {user_count} user message(s).")
    st.write(f"✅ Cleaned and kept {len(cleaned_trajectories)} trajectory(ies).")
    
    return cleaned_trajectories, all_trajectory_blocks


# ============================================================================
# GRAPH VISUALIZATION
# ============================================================================

def plot_trajectories(trajectories):
    """
    Create a visual graph representation of agent trajectories using Graphviz.
    
    Args:
        trajectories (list): List of agent name sequences
        
    Returns:
        Digraph: Graphviz directed graph object
        
    Visualization Features:
        - Left-to-right layout (rankdir='LR')
        - Each trajectory in its own cluster/subgraph
        - Color-coded trajectories for easy distinction
        - Box-shaped nodes for better readability
        - Directed edges showing flow from one agent to next
        
    Colors:
        Cycles through 6 predefined colors to distinguish trajectories:
        - lightblue, lightgreen, lightcoral, khaki, lightgoldenrod1, lightgrey
    """
    # Initialize directed graph
    dot = Digraph(comment="Agent Flow")
    dot.attr(rankdir='LR', size='16,6')  # Left-to-right, large canvas
    
    # Define color palette for trajectories
    colors = [
        "lightblue", 
        "lightgreen", 
        "lightcoral", 
        "khaki", 
        "lightgoldenrod1", 
        "lightgrey"
    ]

    # Create a subgraph for each trajectory
    for i, trajectory in enumerate(trajectories):
        # Select color (cycle through palette)
        color = colors[i % len(colors)]
        label = f"Trajectory {i+1}"

        # Create cluster subgraph for this trajectory
        with dot.subgraph(name=f"cluster_{i}") as sub:
            # Configure subgraph appearance
            sub.attr(label=label, style='filled', color='white')
            sub.attr(rank='same')

            # Add nodes and edges for this trajectory
            prev_node = None
            for j, node in enumerate(trajectory):
                # Create unique node ID (agent name + trajectory + position)
                node_id = f"{node}_traj{i+1}_{j}"
                
                # Add node with styling
                sub.node(
                    node_id, 
                    label=node,           # Display name
                    style='filled', 
                    fillcolor=color,      # Trajectory color
                    shape='box'           # Box shape for clarity
                )
                
                # Add edge from previous node if it exists
                if prev_node:
                    sub.edge(prev_node, node_id)
                
                prev_node = node_id

    return dot


# ============================================================================
# METRICS SUMMARY
# ============================================================================

def summarize_trajectories(blocks):
    """
    Extract and summarize performance metrics from trajectory message blocks.
    
    Args:
        blocks (list): List of message entry blocks, one per trajectory
        
    Returns:
        pd.DataFrame: Summary table with columns:
            - Trajectory #: Trajectory identifier
            - Total Tokens: Token count for the trajectory
            - Total Cost ($): Cost in dollars for the trajectory
            - Total Latency (sec): Latency in seconds for the trajectory
            
    Metric Extraction:
        Looks for metrics in messages from "Reply_Agent":
        - total_time: Response latency
        - total_tokens: Tokens consumed
        - total_cost: API costs incurred
        
    Note:
        If no Reply_Agent is found or metrics are missing, defaults to 0.
        This assumes Reply_Agent is the final agent that aggregates metrics.
    """
    summary = []
    
    # Process each trajectory block
    for i, traj in enumerate(blocks):
        # Initialize metrics with defaults
        total_latency = 0
        total_tokens = 0
        total_cost = 0
        
        # Search for Reply_Agent message with metrics
        for entry in traj:
            try:
                # Check if this is the Reply_Agent (final aggregator)
                if entry.get("source") == "Reply_Agent":
                    # Extract metrics if present
                    total_latency = entry.get("total_time", 0)
                    total_tokens = entry.get("total_tokens", 0)
                    total_cost = entry.get("total_cost", 0)
            except:
                # If any error occurs, keep defaults (0)
                total_latency = 0
                total_tokens = 0
                total_cost = 0
        
        # Add trajectory summary to list
        summary.append({
            "Trajectory #": f"Trajectory {i+1}",
            "Total Tokens": total_tokens,
            "Total Cost ($)": total_cost,
            "Total Latency (sec)": total_latency
        })
    
    return pd.DataFrame(summary)


# ============================================================================
# MAIN APPLICATION LOGIC
# ============================================================================

if uploaded_file:
    try:
        # ========================================
        # STEP 1: LOAD AND VALIDATE JSON
        # ========================================
        # Read uploaded file
        raw_text = uploaded_file.getvalue().decode("utf-8")
        json_data = json.loads(raw_text)

        # Validate JSON structure (must be a list)
        if not isinstance(json_data, list):
            st.error("❌ JSON root must be a list of message entries.")
            st.stop()

        # Filter to keep only dictionary entries
        json_data = [e for e in json_data if isinstance(e, dict)]
        if not json_data:
            st.error("❌ No valid message entries to process after filtering.")
            st.stop()

        # ========================================
        # STEP 2: EXTRACT TRAJECTORIES
        # ========================================
        trajectories, blocks = extract_trajectories(json_data)

        if not trajectories:
            st.warning("⚠️ No valid trajectories found starting from a 'User' agent.")
        else:
            st.success(f"✅ Found {len(trajectories)} valid trajectory(ies).")
            
            # ========================================
            # STEP 3: VISUALIZE TRAJECTORIES
            # ========================================
            # Create and display graph
            graph = plot_trajectories(trajectories)
            st.graphviz_chart(graph.source)

            # Display textual trajectory paths
            for i, path in enumerate(trajectories):
                st.markdown(f"**Trajectory {i+1}:** " + " → ".join(path))

            # ========================================
            # STEP 4: SHOW METRICS SUMMARY
            # ========================================
            st.subheader("📊 Trajectory Summary")
            df_summary = summarize_trajectories(blocks)
            st.dataframe(df_summary, use_container_width=True)

    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON format: {e}")
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")