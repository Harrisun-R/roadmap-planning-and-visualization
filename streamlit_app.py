import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set up Streamlit page configuration
st.set_page_config(page_title="Roadmap Planner", page_icon="📅")

# LinkedIn profile
Name = "Harrisun Raj Mohan"
LinkedIn_URL = "https://www.linkedin.com/in/harrisun-raj-mohan/"
# Title and description
st.title("Roadmap Planning and Visualization")
st.write(f"Developed by {Name}")
st.write(f"[Connect on LinkedIn]({LinkedIn_URL})")
st.write("This tool helps you organize and visualize your product roadmap by allowing you to input phases and milestones. The roadmap is displayed as a Gantt chart.")

# Sidebar for user inputs
st.sidebar.header("Input Roadmap Details")

# Get input for phases and milestones
phases = st.sidebar.text_area("Enter phases (one per line)", "Phase 1\nPhase 2\nPhase 3")
milestones = st.sidebar.text_area("Enter milestones (one per line)", "Milestone A\nMilestone B\nMilestone C")
start_date = st.sidebar.date_input("Start Date", datetime.today())
end_date = st.sidebar.date_input("End Date", datetime.today())

# Initialize empty DataFrame for roadmap data
roadmap_data = pd.DataFrame(columns=["Phase", "Milestone", "Start", "End"])

# Add button to add a phase/milestone
if st.sidebar.button("Add to Roadmap"):
    phases_list = phases.split("\n")
    milestones_list = milestones.split("\n")
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    for phase, milestone in zip(phases_list, milestones_list):
        roadmap_data = roadmap_data.append({"Phase": phase, "Milestone": milestone, "Start": start, "End": end}, ignore_index=True)

# Display roadmap data
if not roadmap_data.empty:
    st.subheader("Roadmap Data")
    st.write(roadmap_data)

    # Visualize roadmap with Plotly Gantt chart
    fig = px.timeline(roadmap_data, x_start="Start", x_end="End", y="Phase", color="Milestone", title="Product Roadmap")
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(xaxis_title="Timeline", yaxis_title="Phases", template="plotly_white")
    
    # Display Gantt chart
    st.plotly_chart(fig)
else:
    st.write("Please add phases and milestones to visualize the roadmap.")
