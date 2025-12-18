import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Interview Themes Analysis", layout="wide")

st.title("Visualizing Theme Saturation Over Interviews")
st.markdown("This web application visualizes the number of Themes collected from interviews. Researchers can upload their data in CSV format to see how Themes accumulate over the course of interviews to decide whether they reached **theme saturation**, that is, the amount of new Themes gained from new interviews becomes few.")
st.markdown("Upload a CSV file to visualize theme collection over interviews. The CSV file should have at least three columns: *Interview_Number*, *Themes_Collected*, and *New_Themes*.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read CSV file
        df = pd.read_csv(uploaded_file)
        
        # Validate columns
        if len(df.columns) < 3:
            st.error("CSV file must have at least 3 columns: Interview Number, Themes Collected, New Themes")
        else:
            # Assume first 3 columns are: Interview Number, Themes Collected, New Themes
            df.columns = ['Interview_Number', 'Themes_Collected', 'New_Themes'] + list(df.columns[3:])
            
            # Convert to numeric
            df['Interview_Number'] = pd.to_numeric(df['Interview_Number'], errors='coerce')
            df['Themes_Collected'] = pd.to_numeric(df['Themes_Collected'], errors='coerce')
            df['New_Themes'] = pd.to_numeric(df['New_Themes'], errors='coerce')
            
            # Remove rows with NaN values
            df = df.dropna(subset=['Interview_Number', 'Themes_Collected', 'New_Themes'])
            
            # Sort by interview number
            df = df.sort_values('Interview_Number')
            
            # Calculate cumulative unique Themes
            df['Cumulative_Unique_Themes'] = df['New_Themes'].cumsum()
            
            # Display data preview
            st.subheader("Data Preview")
            st.dataframe(df[['Interview_Number', 'Themes_Collected', 'New_Themes', 'Cumulative_Unique_Themes']])
            
            # Create dual-axis chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add red line for cumulative unique Themes (left y-axis)
            fig.add_trace(
                go.Scatter(
                    x=df['Interview_Number'],
                    y=df['Cumulative_Unique_Themes'],
                    mode='lines+markers',
                    name='Cumulative Unique Themes',
                    line=dict(color='red', width=3),
                    marker=dict(size=8)
                ),
                secondary_y=False,
            )
            
            # Add blue bars for Themes collected per interview (right y-axis)
            fig.add_trace(
                go.Bar(
                    x=df['Interview_Number'],
                    y=df['Themes_Collected'],
                    name='Themes per Interview',
                    marker_color='blue',
                    opacity=0.7
                ),
                secondary_y=True,
            )
           
            # Calculate the maximum value from both datasets to set same range for both y-axes
            max_cumulative = df['Cumulative_Unique_Themes'].max()
            max_per_interview = df['Themes_Collected'].max()
            y_max = max(max_cumulative, max_per_interview) * 1.1  # Add 10% padding

            # Set x-axis title
            fig.update_xaxes(title_text="Interview Number")
            
            # Set y-axes titles
            fig.update_yaxes(title_text="Cumulative Unique Themes", secondary_y=False, range=[0, y_max])
            fig.update_yaxes(title_text="Themes per Interview", secondary_y=True, range=[0, y_max])
            
            # Update layout
            fig.update_layout(
                title="Interview Themes Analysis",
                height=600,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Display chart
            st.subheader("Visualization")
            st.plotly_chart(fig, use_container_width=True)
            
            # Display summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Interviews", len(df))
            with col2:
                st.metric("Total Unique Themes", int(df['Cumulative_Unique_Themes'].iloc[-1]))
            with col3:
                st.metric("Avg Themes/Interview", f"{df['Themes_Collected'].mean():.1f}")
            with col4:
                st.metric("Avg New Themes/Interview", f"{df['New_Themes'].mean():.1f}")
                
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Please ensure your CSV file has the correct format:\n- Column 1: Interview Number (integer)\n- Column 2: Themes Collected (integer)\n- Column 3: New Themes (integer)")
else:
    st.info("👆 Please upload a CSV file to get started")
    
    # Show example format
    st.subheader("Expected CSV Format")
    example_data = {
        'Interview_Number': [1, 2, 3, 4, 5],
        'Concepts_Collected': [10, 15, 12, 18, 14],
        'New_Concepts': [10, 8, 5, 10, 6]
    }
    example_df = pd.DataFrame(example_data)
    example_df['Cumulative_Unique_Themes'] = example_df['New_Themes'].cumsum()
    st.dataframe(example_df)

