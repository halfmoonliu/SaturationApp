import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Interview Concepts Analysis", layout="wide")

st.title("Visualizing Concept Saturation Over Interviews")
st.markdown("This web application visualizes the number of concepts collected from interviews. Researchers can upload their data in CSV format to see how concepts accumulate over the course of interviews to decide whether they reached **concept saturation**, that is, the amount of new concepts gained from new interviews becomes few.")
st.markdown("Upload a CSV file to visualize concept collection over interviews. The CSV file should have at least three columns: *Interview_Number*, *Concepts_Collected*, and *New_Concepts*.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read CSV file
        df = pd.read_csv(uploaded_file)
        
        # Validate columns
        if len(df.columns) < 3:
            st.error("CSV file must have at least 3 columns: Interview Number, Concepts Collected, New Concepts")
        else:
            # Assume first 3 columns are: Interview Number, Concepts Collected, New Concepts
            df.columns = ['Interview_Number', 'Concepts_Collected', 'New_Concepts'] + list(df.columns[3:])
            
            # Convert to numeric
            df['Interview_Number'] = pd.to_numeric(df['Interview_Number'], errors='coerce')
            df['Concepts_Collected'] = pd.to_numeric(df['Concepts_Collected'], errors='coerce')
            df['New_Concepts'] = pd.to_numeric(df['New_Concepts'], errors='coerce')
            
            # Remove rows with NaN values
            df = df.dropna(subset=['Interview_Number', 'Concepts_Collected', 'New_Concepts'])
            
            # Sort by interview number
            df = df.sort_values('Interview_Number')
            
            # Calculate cumulative unique concepts
            df['Cumulative_Unique_Concepts'] = df['New_Concepts'].cumsum()
            
            # Display data preview
            st.subheader("Data Preview")
            st.dataframe(df[['Interview_Number', 'Concepts_Collected', 'New_Concepts', 'Cumulative_Unique_Concepts']])
            
            # Create dual-axis chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add red line for cumulative unique concepts (left y-axis)
            fig.add_trace(
                go.Scatter(
                    x=df['Interview_Number'],
                    y=df['Cumulative_Unique_Concepts'],
                    mode='lines+markers',
                    name='Cumulative Unique Concepts',
                    line=dict(color='red', width=3),
                    marker=dict(size=8)
                ),
                secondary_y=False,
            )
            
            # Add blue bars for concepts collected per interview (right y-axis)
            fig.add_trace(
                go.Bar(
                    x=df['Interview_Number'],
                    y=df['Concepts_Collected'],
                    name='Concepts per Interview',
                    marker_color='blue',
                    opacity=0.7
                ),
                secondary_y=True,
            )
           
            # Calculate the maximum value from both datasets to set same range for both y-axes
            max_cumulative = df['Cumulative_Unique_Concepts'].max()
            max_per_interview = df['Concepts_Collected'].max()
            y_max = max(max_cumulative, max_per_interview) * 1.1  # Add 10% padding

            # Set x-axis title
            fig.update_xaxes(title_text="Interview Number")
            
            # Set y-axes titles
            fig.update_yaxes(title_text="Cumulative Unique Concepts", secondary_y=False, range=[0, y_max])
            fig.update_yaxes(title_text="Concepts per Interview", secondary_y=True, range=[0, y_max])
            
            # Update layout
            fig.update_layout(
                title="Interview Concepts Analysis",
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
                st.metric("Total Unique Concepts", int(df['Cumulative_Unique_Concepts'].iloc[-1]))
            with col3:
                st.metric("Avg Concepts/Interview", f"{df['Concepts_Collected'].mean():.1f}")
            with col4:
                st.metric("Avg New Concepts/Interview", f"{df['New_Concepts'].mean():.1f}")
                
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Please ensure your CSV file has the correct format:\n- Column 1: Interview Number (integer)\n- Column 2: Concepts Collected (integer)\n- Column 3: New Concepts (integer)")
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
    example_df['Cumulative_Unique_Concepts'] = example_df['New_Concepts'].cumsum()
    st.dataframe(example_df)

