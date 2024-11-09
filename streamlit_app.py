import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
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
st.write("Organize and visualize your product roadmap with custom phases, milestones, and timeline options.")

# Initialize roadmap data
if 'roadmap_data' not in st.session_state:
    st.session_state['roadmap_data'] = pd.DataFrame(columns=["ID", "Phase", "Milestone", "Start", "End", "Color", "Notes", "Dependencies"])

# Function to generate a random color in hex format
def generate_random_color():
    return f"#{''.join([random.choice('0123456789ABCDEF') for _ in range(6)])}"

# Sidebar for user inputs
st.sidebar.header("Add or Edit Roadmap Entry")

# Allow user to add a new roadmap item
with st.sidebar.form("roadmap_form"):
    phase = st.text_input("Phase", "Phase 1")
    milestone = st.text_input("Milestone", "Milestone A")
    start_date = st.date_input("Start Date", datetime.today())
    end_date = st.date_input("End Date", datetime.today())
    color = st.color_picker("Select Milestone Color", generate_random_color())
    notes = st.text_area("Notes (Optional)", "Additional information or links")

    # Dependencies selection
    all_milestones = st.session_state['roadmap_data']['Milestone'].unique().tolist()
    dependencies = st.multiselect("Select Dependencies (Optional)", all_milestones, default=[])
    
    add_button = st.form_submit_button("Add to Roadmap")
    
    # Enhanced Validation
    if add_button:
        # Check for overlapping dates for the same phase
        overlapping = st.session_state['roadmap_data'][
            (st.session_state['roadmap_data']['Phase'] == phase) & 
            ((st.session_state['roadmap_data']['Start'] < end_date) & 
             (st.session_state['roadmap_data']['End'] > start_date))
        ]
        
        if not overlapping.empty:
            st.sidebar.error("Dates overlap with an existing milestone in the same phase.")
        else:
            # Check for duplicate phase-milestone combination
            duplicate = st.session_state['roadmap_data'][
                (st.session_state['roadmap_data']['Phase'] == phase) & 
                (st.session_state['roadmap_data']['Milestone'] == milestone)
            ]
            
            if not duplicate.empty:
                st.sidebar.error("Duplicate Phase-Milestone combination found!")
            else:
                # Add the new entry if no errors
                new_entry = pd.DataFrame({
                    "ID": [str(uuid.uuid4())],  # Unique ID for deletion and filtering
                    "Phase": [phase],
                    "Milestone": [milestone],
                    "Start": [pd.to_datetime(start_date)],
                    "End": [pd.to_datetime(end_date)],
                    "Color": [color],
                    "Notes": [notes],
                    "Dependencies": [dependencies]
                })
                st.session_state['roadmap_data'] = pd.concat([st.session_state['roadmap_data'], new_entry], ignore_index=True)

# Option to edit an entry's dates
if not st.session_state['roadmap_data'].empty:
    st.sidebar.subheader("Edit an Entry's Dates")
    entries = st.session_state['roadmap_data'][['Phase', 'Milestone', 'ID']].apply(lambda x: f"{x['Phase']} - {x['Milestone']}", axis=1).tolist()
    selected_entry_edit = st.sidebar.selectbox("Select Entry to Edit", entries)
    
    if selected_entry_edit:
        entry_id = st.session_state['roadmap_data'][st.session_state['roadmap_data'][['Phase', 'Milestone']].apply(lambda x: f"{x['Phase']} - {x['Milestone']}", axis=1) == selected_entry_edit].iloc[0]["ID"]
        start_date_edit = st.sidebar.date_input("Edit Start Date", value=st.session_state['roadmap_data'].loc[st.session_state['roadmap_data']['ID'] == entry_id, 'Start'].iloc[0])
        end_date_edit = st.sidebar.date_input("Edit End Date", value=st.session_state['roadmap_data'].loc[st.session_state['roadmap_data']['ID'] == entry_id, 'End'].iloc[0])
        
        if st.sidebar.button("Save Date Changes"):
            st.session_state['roadmap_data'].loc[st.session_state['roadmap_data']['ID'] == entry_id, 'Start'] = start_date_edit
            st.session_state['roadmap_data'].loc[st.session_state['roadmap_data']['ID'] == entry_id, 'End'] = end_date_edit
            st.sidebar.success(f"Updated dates for: {selected_entry_edit}")

# Option to delete an entry
if not st.session_state['roadmap_data'].empty:
    st.sidebar.subheader("Delete a Phase/Milestone")
    selected_entry_delete = st.sidebar.selectbox("Select Entry to Delete", entries)
    
    if st.sidebar.button("Delete Selected Entry"):
        entry_id_delete = st.session_state['roadmap_data'][st.session_state['roadmap_data'][['Phase', 'Milestone']].apply(lambda x: f"{x['Phase']} - {x['Milestone']}", axis=1) == selected_entry_delete].iloc[0]["ID"]
        st.session_state['roadmap_data'] = st.session_state['roadmap_data'][st.session_state['roadmap_data']['ID'] != entry_id_delete]
        st.sidebar.success(f"Deleted: {selected_entry_delete}")

# Display roadmap data
if not st.session_state['roadmap_data'].empty:
    st.subheader("Roadmap Data")
    st.write(st.session_state['roadmap_data'].drop(columns=["ID"]))

    # Visualize roadmap with Plotly Gantt chart
    fig = px.timeline(
        st.session_state['roadmap_data'], 
        x_start="Start", 
        x_end="End", 
        y="Phase", 
        color="Milestone", 
        title="Product Roadmap",
        hover_data=["Notes"]
    )
    
    # Draw dependencies (arrows)
    for _, row in st.session_state['roadmap_data'].iterrows():
        if row["Dependencies"]:
            for dep in row["Dependencies"]:
                dep_row = st.session_state['roadmap_data'][st.session_state['roadmap_data']['Milestone'] == dep]
                if not dep_row.empty:
                    dep_start = dep_row.iloc[0]["End"]
                    fig.add_annotation(
                        x=dep_start, 
                        y=row["Phase"], 
                        ax=row["Start"], 
                        ay=row["Phase"], 
                        xref="x", 
                        yref="y", 
                        axref="x", 
                        ayref="y", 
                        showarrow=True, 
                        arrowhead=2, 
                        arrowsize=1,
                        arrowwidth=2,
                        bgcolor="red",
                        font=dict(color="red", size=12)
                    )

    fig.update_traces(marker_color=st.session_state['roadmap_data']["Color"], selector=dict(type="scatter"))
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
