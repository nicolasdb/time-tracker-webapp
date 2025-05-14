"""
Visualization utilities for time tracking data.
"""
import logging
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

logger = logging.getLogger(__name__)

def create_test_chart(data_df: pd.DataFrame = None) -> go.Figure:
    """
    Create a chart visualization of RFID event data.
    If no data is provided, creates a sample chart with dummy data.
    
    Args:
        data_df: DataFrame containing event data (optional)
        
    Returns:
        go.Figure: A Plotly figure object
    """
    try:
        # If we have actual data and it has the right structure, use it
        if data_df is not None and not data_df.empty and 'event_type' in data_df.columns:
            # Count events by type
            event_counts = data_df['event_type'].value_counts().reset_index()
            event_counts.columns = ['event_type', 'count']
            
            # Create a bar chart of event types
            fig = px.bar(
                event_counts,
                x='event_type',
                y='count',
                title="RFID Events by Type",
                labels={"event_type": "Event Type", "count": "Count"},
                color='event_type',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
        else:
            # Create dummy data for sample visualization
            event_types = ["tap_in", "tap_out", "register", "error"]
            counts = [12, 10, 3, 1]
            
            # Create a simple bar chart
            fig = px.bar(
                x=event_types,
                y=counts,
                title="Sample RFID Event Distribution",
                labels={"x": "Event Type", "y": "Count"},
                color=event_types,
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
        
        # Update layout
        fig.update_layout(
            title_font_size=20,
            xaxis_title_font_size=16,
            yaxis_title_font_size=16,
            legend_title_font_size=16
        )
        
        return fig
    except Exception as e:
        logger.error(f"Failed to create chart: {str(e)}")
        # Return empty figure on error
        return go.Figure()

def format_tag_data(event_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Format RFID event data from Supabase for visualization.
    
    Args:
        event_data: List of event objects from Supabase
        
    Returns:
        pd.DataFrame: Formatted data ready for visualization
    """
    try:
        if not event_data:
            return pd.DataFrame()
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(event_data)
        
        # Check if we have timestamp column and convert to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            # Use 24-hour format for time
            df['time'] = df['timestamp'].dt.strftime('%H:%M:%S')
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
        
        # Create a more readable display format
        try:
            # Select and reorder columns for better display
            display_columns = ['event_type', 'uid_tag', 'uid_device', 'date', 'time']
            available_columns = [col for col in display_columns if col in df.columns]
            
            # Add any other columns that exist but weren't in our preferred list
            for col in df.columns:
                if col not in available_columns and col != 'timestamp':
                    available_columns.append(col)
                    
            return df[available_columns]
        except Exception as e:
            logger.warning(f"Error formatting columns: {str(e)}")
            return df
            
    except Exception as e:
        logger.error(f"Failed to format event data: {str(e)}")
        return pd.DataFrame()