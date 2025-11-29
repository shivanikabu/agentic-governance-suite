"""
Agent & Tool Trajectory Optimizer
==================================
A Streamlit-based tool for analyzing and optimizing agent interaction trajectories
using weighted scoring across multiple performance dimensions.

Features:
- Trajectory Extraction: Identifies conversation flows from User messages
- Multi-Factor Scoring: Evaluates trajectories based on customizable weights:
  * Goal Achievement: How well the trajectory accomplishes its objective
  * Cost Efficiency: API costs incurred (lower is better)
  * Latency Efficiency: Response time (faster is better)
- Convergence Analysis: Identifies the optimal trajectory
- Performance Comparison: Ranks all trajectories by weighted score

Scoring Algorithm:
1. Extract metrics (latency, cost, trajectory length) from each trajectory
2. Normalize values to 0-1 scale for fair comparison
3. Apply user-defined weights to each factor
4. Calculate composite Convergence Score (0-100)
5. Rank trajectories by score to identify best performance

Use Cases:
- Optimizing multi-agent workflows
- A/B testing different agent configurations
- Cost-performance trade-off analysis
- Identifying most efficient conversation paths
- Benchmarking agent routing strategies

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
st.title("🤖 Agent & Tool Optimizer")
st.markdown("""
Upload a `.json` interaction log.  
This app will identify and visualize agent/tool **trajectories** starting from `User` 
and ending before the next `User`, and summarize token usage and cost.
""")


# ============================================================================
# WEIGHT CONFIGURATION
# ============================================================================
st.subheader("⚖️ Trajectory Scoring Weights")
st.markdown("Adjust the importance of each factor for trajectory evaluation:")

col1, col2, col3 = st.columns(3)

# Weight slider for Goal Achievement
with col1:
    goal_state_weight = st.slider(
        "🎯 Goal State Weight",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Weight for how well the trajectory achieves the goal state. "
             "Higher trajectory length indicates more goal achievement."
    )

# Weight slider for Cost Efficiency
with col2:
    total_cost_weight = st.slider(
        "💰 Total Cost Weight",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Weight for the total cost of the trajectory. "
             "Higher weight penalizes trajectories with higher API costs."
    )

# Weight slider for Latency Efficiency
with col3:
    total_latency_weight = st.slider(
        "🔢 Total Latency Weight",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Weight for the total latency. "
             "Higher weight penalizes trajectories with longer response times."
    )

# Display current weight configuration
st.info(
    f"**Current Weights:** "
    f"Goal State: {goal_state_weight} | "
    f"Total Cost: {total_cost_weight} | "
    f"Total Latency: {total_latency_weight}"
)

# Validate weight configuration
total_weights = goal_state_weight + total_cost_weight + total_latency_weight
if total_weights == 0:
    st.warning("⚠️ At least one weight must be greater than 0 for meaningful scoring.")
elif total_weights > 1:
    st.warning(
        f"⚠️ Total weights sum to {total_weights:.1f}. "
        "Consider normalizing to sum to 1.0 for better interpretation."
    )

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
            - trajectories: List of agent name sequences
            - all_trajectory_blocks: List of corresponding message entry blocks
            
    Message Entry Structure:
        {
            "source": "AgentName",
            "content": {
                "next_speaker": "NextAgent"
            },
            ...
        }
    """
    st.write("🔍 Starting trajectory extraction...")

    # Storage for results
    trajectories = []              # Agent name sequences
    all_trajectory_blocks = []     # Full message entry blocks
    
    # Current trajectory being built
    current_trajectory = []
    current_block = []
    user_count = 0

    # Iterate through all log entries
    for i, entry in enumerate(json_data):
        # Skip non-dictionary entries
        if not isinstance(entry, dict):
            continue

        # Extract source (current speaker)
        source = entry.get("source", "").strip()
        
        # Parse content (may be dict or JSON string)
        content_raw = entry.get("content", None)
        content_json = {}

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

        # Extract next_speaker
        next_speaker = content_json.get("next_speaker", "").strip()

        # Check for trajectory boundary (User message)
        if source.lower() == "user":
            user_count += 1
            
            # Save previous trajectory
            if current_trajectory:
                trajectories.append(current_trajectory)
                all_trajectory_blocks.append(current_block)
            
            # Start new trajectory
            current_trajectory = ["User"]
            current_block = [entry]
            
            if next_speaker:
                current_trajectory.append(next_speaker)
        else:
            # Continue building current trajectory
            if current_trajectory:
                if source and source not in current_trajectory:
                    current_trajectory.append(source)
                if next_speaker and next_speaker not in current_trajectory:
                    current_trajectory.append(next_speaker)
                current_block.append(entry)

    # Save last trajectory
    if current_trajectory:
        trajectories.append(current_trajectory)
        all_trajectory_blocks.append(current_block)

    # Clean: keep only valid trajectories (start with User, length > 1)
    cleaned_trajectories = [
        t for t in trajectories if len(t) > 1 and t[0].lower() == "user"
    ]

    st.write(f"✅ Found {user_count} user message(s).")
    st.write(f"✅ Cleaned and kept {len(cleaned_trajectories)} trajectory(ies).")
    
    return cleaned_trajectories, all_trajectory_blocks


# ============================================================================
# TRAJECTORY SCORING
# ============================================================================

def calculate_trajectory_scores(blocks, goal_weight, cost_weight, latency_weight):
    """
    Calculate weighted convergence scores for trajectories.
    
    Scoring Methodology:
    1. Extract raw metrics (latency, cost, length) for each trajectory
    2. Normalize metrics to 0-1 scale for fair comparison
    3. Apply user-defined weights to each normalized metric
    4. Calculate composite Convergence Score (0-100)
    
    Args:
        blocks (list): List of message entry blocks (one per trajectory)
        goal_weight (float): Weight for goal achievement (0-1)
        cost_weight (float): Weight for cost efficiency (0-1)
        latency_weight (float): Weight for latency efficiency (0-1)
        
    Returns:
        pd.DataFrame: Scoring table with columns:
            - Trajectory: Trajectory number
            - Goal Achievement: Normalized goal score (0-100)
            - Cost Efficiency: Normalized cost score (0-100, higher is better)
            - Latency Efficiency: Normalized latency score (0-100, higher is better)
            - Convergence Score: Weighted composite score (0-100)
            
    Normalization Details:
        - Goal: Trajectory length / 5 (longer = more complex = better goal achievement)
        - Cost: 1 - (cost / max_cost) (lower cost = higher efficiency)
        - Latency: 1 - (latency / max_latency) (lower latency = higher efficiency)
        
    Note:
        Default max values are used as baselines but updated if actual values exceed them.
    """
    scores = []
    
    # Default maximum values for normalization
    max_latency = 1000  # Default max latency in seconds
    max_cost = 0.625    # Default max cost in dollars
    
    # ========================================
    # STEP 1: EXTRACT RAW METRICS
    # ========================================
    trajectory_metrics = []
    for traj in blocks:
        total_latency = 0
        total_cost = 0
        trajectory_length = len(traj)
        
        # Extract metrics from Reply_Agent (final aggregator)
        for entry in traj:
            try:
                if entry.get("source") == "Reply_Agent":
                    # Extract and sum latency
                    latency = entry.get("total_time", 0)
                    if latency:
                        total_latency += float(latency)
                    
                    # Extract and sum cost
                    cost = entry.get("total_cost", 0)
                    if cost:
                        total_cost += float(cost)
            except (ValueError, TypeError):
                # Skip invalid entries
                pass
        
        trajectory_metrics.append({
            'length': trajectory_length,
            'latency': total_latency,
            'cost': total_cost
        })
    
    # ========================================
    # STEP 2: CALCULATE DYNAMIC MAX VALUES
    # ========================================
    # Update max values based on actual data if needed
    if trajectory_metrics:
        actual_max_latency = max(m['latency'] for m in trajectory_metrics)
        actual_max_cost = max(m['cost'] for m in trajectory_metrics)
        
        # Use the greater of default or actual max
        max_latency = max(max_latency, actual_max_latency) if actual_max_latency > 0 else max_latency
        max_cost = max(max_cost, actual_max_cost) if actual_max_cost > 0 else max_cost
    
    # ========================================
    # STEP 3: CALCULATE NORMALIZED SCORES
    # ========================================
    for i, metrics in enumerate(trajectory_metrics):
        # Normalize cost (inverse: lower cost = higher score)
        norm_cost = (1 - (metrics['cost'] / max_cost)) if max_cost > 0 else 1
        
        # Normalize latency (inverse: lower latency = higher score)
        norm_latency = (1 - (metrics['latency'] / max_latency)) if max_latency > 0 else 1
        
        # Normalize goal achievement (longer trajectory = more complex = better)
        # Cap at 1.0 when length >= 5
        norm_goal = min(metrics['length'] / 5, 1)
        
        # ========================================
        # STEP 4: CALCULATE WEIGHTED SCORE
        # ========================================
        total_weight = goal_weight + cost_weight + latency_weight
        if total_weight > 0:
            weighted_score = (
                norm_goal * goal_weight +
                norm_cost * cost_weight +
                norm_latency * latency_weight
            ) / total_weight * 100  # Scale to 0-100
        else:
            weighted_score = 0
        
        # Store results
        scores.append({
            "Trajectory": i + 1,
            "Goal Achievement": round(norm_goal * 100, 1),
            "Cost Efficiency": round(norm_cost * 100, 1),
            "Latency Efficiency": round(norm_latency * 100, 1),
            "Convergence Score": round(weighted_score, 1),
        })
    
    return pd.DataFrame(scores)


# ============================================================================
# METRICS SUMMARY (Legacy - Currently Unused)
# ============================================================================

def summarize_trajectories(blocks):
    """
    Generate basic metrics summary for trajectories.
    
    Note: This function is currently not used in the main flow.
    The calculate_trajectory_scores function provides more comprehensive metrics.
    
    Args:
        blocks (list): List of message entry blocks
        
    Returns:
        pd.DataFrame: Summary with total tokens and costs per trajectory
    """
    summary = []
    for i, traj in enumerate(blocks):
        total_tokens = 0
        total_cost = 0.0
        
        for entry in traj:
            # Extract tokens
            try:
                tokens = int(entry.get("total_tokens", 0))
            except:
                tokens = 0
            
            # Extract cost
            cost_str = str(entry.get("Total_Cost", "0")).replace("$", "").strip()
            try:
                cost = float(cost_str)
            except:
                cost = 0.0
            
            total_tokens += tokens
            total_cost += cost

        summary.append({
            "Trajectory #": f"Trajectory {i+1}",
            "Total Tokens": total_tokens,
            "Total Cost ($)": round(total_cost, 4)
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
        raw_text = uploaded_file.getvalue().decode("utf-8")
        json_data = json.loads(raw_text)

        # Validate JSON structure
        if not isinstance(json_data, list):
            st.error("❌ JSON root must be a list of message entries.")
            st.stop()

        # Filter to dictionary entries only
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

            # Display trajectory paths
            for i, path in enumerate(trajectories):
                st.markdown(f"**Trajectory {i+1}:** " + " → ".join(path))

            # ========================================
            # STEP 3: CALCULATE AND DISPLAY SCORES
            # ========================================
            st.subheader("🏆 Convergence Trajectory Scoring")
            
            # Calculate weighted scores
            df_scores = calculate_trajectory_scores(
                blocks, 
                goal_state_weight, 
                total_cost_weight, 
                total_latency_weight
            )
            
            # Sort by Convergence Score (highest = best)
            df_scores = df_scores.sort_values("Convergence Score", ascending=False)
            st.dataframe(df_scores, use_container_width=True)
            
            # ========================================
            # STEP 4: HIGHLIGHT BEST TRAJECTORY
            # ========================================
            best_trajectory = df_scores.iloc[0]
            st.success(
                f"🥇 **Best Trajectory:** Trajectory {best_trajectory['Trajectory']} "
                f"with a Convergence score of {best_trajectory['Convergence Score']}"
            )

    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON format: {e}")
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")