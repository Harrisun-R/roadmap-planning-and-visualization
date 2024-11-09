import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# Set up Streamlit page configuration
st.set_page_config(page_title="Roadmap Planner", page_icon="📅")

# Placeholder for your name and LinkedIn profile
NAME = "Harrisun Raj Mohan"
LINKEDIN_URL = "https://www.linkedin.com/in/harrisun-raj-mohan/"

# Title and description
st.title("Roadmap Planning and Visualization")
st.write(f"Developed by {NAME}")
st.write(f"[Connect on LinkedIn]({LINKEDIN_URL})")
st.write("This tool helps you organize and visualize your product roadmap by allowing you to input phases and milestones with custom start and end dates. The roadmap is displayed as a Gantt chart.")

# Initialize roadmap data
if 'roadmap_data' not in st.session_state:
    st.session_state['roadmap_data'] = pd.DataFrame(columns=["ID", "Phase", "Milestone", "Start", "End", "Color", "Notes"])

# Sidebar for user inputs
st.sidebar.header("Add New Entry to Roadmap")

with st.sidebar.form("roadmap_form"):
    phase = st.text_input("Phase", "Phase 1")
    milestone = st.text_input("Milestone", "Milestone A")
    start_date = st.date_input("Start Date", datetime.today())
    end_date = st.date_input("End Date", datetime.today())
    color = st.color_picker("Select Milestone Color", "#00aaff")
    notes = st.text_area("Notes (Optional)", "Additional information or links")
    
    add_button = st.form_submit_button("Add to Roadmap")
    
    if add_button:
        if start_date <= end_date:
            new_entry = pd.DataFrame({
                "ID": [str(uuid.uuid4())],  # Unique ID for deletion and filtering
                "Phase": [phase],
                "Milestone": [milestone],
                "Start": [pd.to_datetime(start_date)],
                "End": [pd.to_datetime(end_date)],
                "Color": [color],
                "Notes": [notes]
            })
            st.session_state['roadmap_data'] = pd.concat([st.session_state['roadmap_data'], new_entry], ignore_index=True)
        else:
            st.sidebar.error("End date must be after the start date.")

# Option to delete an entry
if not st.session_state['roadmap_data'].empty:
    st.sidebar.subheader("Delete a Phase/Milestone")
    entries = st.session_state['roadmap_data'][['Phase', 'Milestone', 'ID']].apply(lambda x: f"{x['Phase']} - {x['Milestone']}", axis=1).tolist()
    selected_entry = st.sidebar.selectbox("Select Entry to Delete", entries)
    
    if st.sidebar.button("Delete Selected Entry"):
        entry_id = st.session_state['roadmap_data'][st.session_state['roadmap_data'][['Phase', 'Milestone']].apply(lambda x: f"{x['Phase']} - {x['Milestone']}", axis=1) == selected_entry].iloc[0]["ID"]
        st.session_state['roadmap_data'] = st.session_state['roadmap_data'][st.session_state['roadmap_data']['ID'] != entry_id]
        st.sidebar.success(f"Deleted: {selected_entry}")

# Search and Filter Capabilities
st.sidebar.subheader("Search & Filter Roadmap")
search_query = st.sidebar.text_input("Search by Phase or Milestone")
filtered_data = st.session_state['roadmap_data']
if search_query:
    filtered_data = filtered_data[filtered_data['Phase'].str.contains(search_query, case=False) | filtered_data['Milestone'].str.contains(search_query, case=False)]

# Export and Import Options
if not st.session_state['roadmap_data'].empty:
    csv_data = st.session_state['roadmap_data'].drop(columns=["ID"]).to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Download Roadmap as CSV", csv_data, "roadmap.csv", "text/csv")

uploaded_file = st.sidebar.file_uploader("Upload a Roadmap CSV", type=["csv"])
if uploaded_file is not None:
    uploaded_data = pd.read_csv(uploaded_file)
    uploaded_data['ID'] = [str(uuid.uuid4()) for _ in range(len(uploaded_data))]
    st.session_state['roadmap_data'] = pd.concat([st.session_state['roadmap_data'], uploaded_data], ignore_index=True)
    st.sidebar.success("Roadmap data imported successfully.")

# Display roadmap data
if not filtered_data.empty:
    st.subheader("Roadmap Data")
    st.write(filtered_data.drop(columns=["ID"]))

    # Visualize roadmap with Plotly Gantt chart
    fig = px.timeline(
        filtered_data, 
        x_start="Start", 
        x_end="End", 
        y="Phase", 
        color="Milestone", 
        title="Product Roadmap",
        hover_data=["Notes"]
    )
    fig.update_traces(marker_color=filtered_data["Color"], selector=dict(type="scatter"))
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(
        xaxis_title="Timeline", 
        yaxis_title="Phases", 
        template="plotly_white",
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True)
        )
    )
    # Display Gantt chart
    st.plotly_chart(fig)
else:
    st.write("Please add phases and milestones to visualize the roadmap.")
