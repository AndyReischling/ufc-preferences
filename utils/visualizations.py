"""
Visualization functions for fighter stats.
Uses Plotly for interactive charts compatible with Streamlit.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def create_radar_chart(fighter_stats, fighter_name="Fighter", comparison_stats=None, comparison_name="Average"):
    """
    Create a radar chart for fighter statistics.
    
    Args:
        fighter_stats: Dictionary with stat names and normalized values (0-1)
        fighter_name: Name of the fighter
        comparison_stats: Optional dictionary for comparison (e.g., cluster average)
        comparison_name: Name for comparison stats
    
    Returns:
        Plotly figure object
    """
    if not fighter_stats:
        return None
    
    # Define stat categories and labels
    stat_categories = {
        'Striking': ['strikes_per_min', 'strike_accuracy'],
        'Strike Targeting': ['head_strike_ratio', 'body_strike_ratio', 'leg_strike_ratio'],
        'Grappling': ['takedown_accuracy', 'control_time_ratio'],
        'Clinch': ['clinch_time_ratio']
    }
    
    # Flatten categories for radar chart
    categories = []
    values = []
    comparison_values = []
    
    for category, stat_names in stat_categories.items():
        for stat_name in stat_names:
            if stat_name in fighter_stats:
                # Create readable label
                label = stat_name.replace('_', ' ').title()
                categories.append(label)
                values.append(fighter_stats[stat_name])
                
                if comparison_stats and stat_name in comparison_stats:
                    comparison_values.append(comparison_stats[stat_name])
                else:
                    comparison_values.append(0)
    
    if len(categories) == 0:
        return None
    
    # Create radar chart
    fig = go.Figure()
    
    # Add fighter stats
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=fighter_name,
        line_color='rgb(255, 107, 53)'  # UFC orange
    ))
    
    # Add comparison if provided
    if comparison_stats and any(v > 0 for v in comparison_values):
        fig.add_trace(go.Scatterpolar(
            r=comparison_values,
            theta=categories,
            fill='toself',
            name=comparison_name,
            line_color='rgb(100, 100, 100)',
            opacity=0.5
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title=f"{fighter_name} - Fighting Style Radar",
        height=500
    )
    
    return fig


def create_stat_bar_chart(fighter_stats, stat_names=None, fighter_name="Fighter", comparison_stats=None):
    """
    Create a bar chart comparing fighter stats.
    
    Args:
        fighter_stats: Dictionary with stat names and values
        stat_names: List of stat names to include (if None, uses all)
        fighter_name: Name of the fighter
        comparison_stats: Optional dictionary for comparison
    
    Returns:
        Plotly figure object
    """
    if not fighter_stats:
        return None
    
    if stat_names is None:
        stat_names = list(fighter_stats.keys())
    
    # Prepare data
    fighter_values = [fighter_stats.get(stat, 0) for stat in stat_names]
    comparison_values = [comparison_stats.get(stat, 0) if comparison_stats else None for stat in stat_names]
    
    # Create readable labels
    labels = [stat.replace('_', ' ').title() for stat in stat_names]
    
    fig = go.Figure()
    
    # Add fighter bars
    fig.add_trace(go.Bar(
        x=labels,
        y=fighter_values,
        name=fighter_name,
        marker_color='rgb(255, 107, 53)'
    ))
    
    # Add comparison bars if provided
    if comparison_stats:
        fig.add_trace(go.Bar(
            x=labels,
            y=comparison_values,
            name="Comparison",
            marker_color='rgb(150, 150, 150)',
            opacity=0.7
        ))
    
    fig.update_layout(
        title=f"{fighter_name} - Key Statistics",
        xaxis_title="Statistic",
        yaxis_title="Value",
        barmode='group',
        height=400
    )
    
    return fig


def create_stat_comparison_chart(fighter_stats_list, fighter_names, stat_name):
    """
    Create a bar chart comparing a single stat across multiple fighters.
    
    Args:
        fighter_stats_list: List of stat dictionaries
        fighter_names: List of fighter names
        stat_name: Name of stat to compare
    
    Returns:
        Plotly figure object
    """
    if len(fighter_stats_list) != len(fighter_names):
        return None
    
    values = [stats.get(stat_name, 0) for stats in fighter_stats_list]
    
    fig = go.Figure(data=[
        go.Bar(
            x=fighter_names,
            y=values,
            marker_color='rgb(255, 107, 53)'
        )
    ])
    
    stat_label = stat_name.replace('_', ' ').title()
    fig.update_layout(
        title=f"Comparison: {stat_label}",
        xaxis_title="Fighter",
        yaxis_title=stat_label,
        height=400
    )
    
    return fig

