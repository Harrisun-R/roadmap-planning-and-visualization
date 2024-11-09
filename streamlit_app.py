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
st.write("Organize and visualize your product roadmap with custom phases, milestones, and timeline options.")

# Initialize roadmap data
if 'roadmap_data' not in st.session_state:
    st.session_state['roadmap_data'] = pd.DataFrame(columns=["ID", "Phase", "Milestone", "Start", "End", "Color", "Notes", "Dependencies"])

# Sidebar for user inputs
st.sidebar.header("Add New Entry to Roadmap")

with st.sidebar.form("roadmap_form"):
    phase = st.text_input("Phase", "Phase 1")
    milestone = st.text_input("Milestone", "Milestone A")
    start_date = st.date_input("Start Date", datetime.today())
    end_date = st.date_input("End Date", datetime.today())
    color = st.color_picker("Select Milestone Color", "#00aaff")
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
    
    # Draw dependencies (arrows)
    for _, row in filtered_data.iterrows():
        if row["Dependencies"]:
            for dep in row["Dependencies"]:
                dep_row = filtered_data[filtered_data['Milestone'] == dep]
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
