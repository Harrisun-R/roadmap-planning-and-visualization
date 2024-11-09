import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set up Streamlit page configuration
st.set_page_config(page_title="Roadmap Planner", page_icon="📅")

# Title and description
st.title("Roadmap Planning and Visualization")
st.write("This tool helps you organize and visualize your product roadmap by allowing you to input phases and milestones with custom start and end dates. The roadmap is displayed as a Gantt chart.")

# Initialize empty DataFrame for roadmap data
if 'roadmap_data' not in st.session_state:
    st.session_state['roadmap_data'] = pd.DataFrame(columns=["Phase", "Milestone", "Start", "End"])

# Sidebar for user inputs
st.sidebar.header("Manage Roadmap Entries")

# Get input for each phase/milestone individually
with st.sidebar.form("roadmap_form"):
    phase = st.text_input("Phase", "Phase 1")
    milestone = st.text_input("Milestone", "Milestone A")
    start_date = st.date_input("Start Date", datetime.today())
    end_date = st.date_input("End Date", datetime.today())
    
    # Button to add the new entry to the roadmap
    add_button = st.form_submit_button("Add to Roadmap")
    
    # Check if the start date is before the end date
    if add_button:
        if start_date <= end_date:
            # Append new entry to the roadmap DataFrame
            new_entry = pd.DataFrame({
                "Phase": [phase],
                "Milestone": [milestone],
                "Start": [pd.to_datetime(start_date)],
                "End": [pd.to_datetime(end_date)]
            })
            st.session_state['roadmap_data'] = pd.concat([st.session_state['roadmap_data'], new_entry], ignore_index=True)
        else:
            st.sidebar.error("End date must be after the start date.")

# Feature to delete an entry
if not st.session_state['roadmap_data'].empty:
    st.sidebar.subheader("Delete a Phase/Milestone")
    # Create a list of unique Phase-Milestone combinations
    entries = st.session_state['roadmap_data'][['Phase', 'Milestone']].apply(lambda x: f"{x['Phase']} - {x['Milestone']}", axis=1).tolist()
    selected_entry = st.sidebar.selectbox("Select Phase-Milestone to delete", entries)
    
    if st.sidebar.button("Delete Selected Entry"):
        # Split the selected entry to get phase and milestone
        phase_to_delete, milestone_to_delete = selected_entry.split(" - ")
        
        # Delete the row from the DataFrame
        st.session_state['roadmap_data'] = st.session_state['roadmap_data'][
            ~((st.session_state['roadmap_data']['Phase'] == phase_to_delete) & 
              (st.session_state['roadmap_data']['Milestone'] == milestone_to_delete))
        ]
        st.sidebar.success(f"Deleted: {selected_entry}")

# Display roadmap data
if not st.session_state['roadmap_data'].empty:
    st.subheader("Roadmap Data")
    st.write(st.session_state['roadmap_data'])

    # Visualize roadmap with Plotly Gantt chart
    fig = px.timeline(
        st.session_state['roadmap_data'], 
        x_start="Start", 
        x_end="End", 
        y="Phase", 
        color="Milestone", 
        title="Product Roadmap"
    )
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(xaxis_title="Timeline", yaxis_title="Phases", template="plotly_white")
    
    # Display Gantt chart
    st.plotly_chart(fig)
else:
    st.write("Please add phases and milestones to visualize the roadmap.")

