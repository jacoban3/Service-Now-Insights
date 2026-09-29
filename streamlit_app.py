# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
import requests
#from snowflake.snowpark.functions import col

import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
# Write directly to the app
session = get_active_session()
# Show app title and description.
st.set_page_config(page_title="Search Service Now Tickets", page_icon="🔎")
st.title("🔎 Search Service Now Tickets")
st.write(
    """
    This app is linked to Service Now data in Snowflake. The report is designed to provide rapid visibility into support incidents, helping engineers and support teams identify, 
    investigate, and resolve tickets more efficiently. The goal is to reduce the time spent searching for information and increase the time spent resolving issues, 
    ultimately improving operational efficiency and support outcomes.
    """
)

# Create a random Pandas dataframe with existing tickets.
if "df" not in st.session_state:

    # Set seed for reproducibility.
    np.random.seed(42)

import streamlit as st
from snowflake.snowpark.context import get_active_session

session = get_active_session()

st.header("ServiceNow Incidents")

# Pull the incident data from the Snowflake view.
incident_query = """
SELECT
    INCIDENT_NUMBER,
    OPENED_DATE,
    CLOSED_DATE,
    STATE,
    ASSIGNED_TO,
    SHORT_DESCRIPTION,
    DESCRIPTION,
    WORK_NOTES,
    "IncidentURL" AS INCIDENT_URL
FROM SNOWFLAKE_LEARNING_DB.CORE.VW_ODS_SERVICENOW_INCIDENTS
ORDER BY OPENED_DATE DESC
"""

incident_df = session.sql(incident_query).to_pandas()

# Rename the columns for display.
incident_df = incident_df.rename(
    columns={
        "OPENED_DATE": "Opened Date",
        "CLOSED_DATE": "Closed Date",
        "INCIDENT_NUMBER": "Inc Number",
        "STATE": "State",
        "ASSIGNED_TO": "Assigned To",
        "SHORT_DESCRIPTION": "Short Description",
        "DESCRIPTION": "Description",
        "WORK_NOTES": "Work Notes",
        "INCIDENT_URL": "Incident Link"
    }
)

# -----------------------------
# First dataframe: incident list
# -----------------------------

incident_list_df = incident_df[
    [
        "Opened Date",
        "Closed Date",
        "Inc Number",
        "State",
        "Assigned To",
        "Short Description",
        "Incident Link"
    ]
].copy()

st.write("Select an incident to view its description and work notes.")

incident_selection = st.dataframe(
    incident_list_df,
    hide_index=True,
    width="stretch",
    height=400,
    on_select="rerun",
    selection_mode="single-row",
    key="incident_list",
    column_order=[
        "Opened Date",
        "Closed Date",
        "Inc Number",
        "State",
        "Assigned To",
        "Short Description",
        "Incident Link"
    ],
    column_config={
        "Opened Date": st.column_config.DateColumn(
            "Opened Date",
            format="MM/DD/YYYY"
        ),
        "Closed Date": st.column_config.DateColumn(
            "Closed Date",
            format="MM/DD/YYYY"
        ),
        "Inc Number": st.column_config.TextColumn(
            "Inc Number"
        ),
        "Incident Link": st.column_config.LinkColumn(
            "Open Incident",
            display_text="Open in ServiceNow"
        )
    }
)

# -----------------------------
# Second dataframe: selected row
# -----------------------------

selected_rows = incident_selection.selection.rows

if selected_rows:

    selected_index = selected_rows[0]

    selected_incident_number = incident_list_df.iloc[
        selected_index
    ]["Inc Number"]

    incident_detail_df = incident_df[
        incident_df["Inc Number"] == selected_incident_number
    ][
        [
            "Opened Date",
            "Inc Number",
            "Description",
            "Work Notes",
            "Incident Link"
        ]
    ].copy()

    st.subheader(f"Incident Details: {selected_incident_number}")

    st.dataframe(
        incident_detail_df,
        hide_index=True,
        width="stretch",
        column_order=[
            "Opened Date",
            "Inc Number",
            "Description",
            "Work Notes",
            "Incident Link"
        ],
        column_config={
            "Opened Date": st.column_config.DateColumn(
                "Opened Date",
                format="MM/DD/YYYY"
            ),
            "Inc Number": st.column_config.TextColumn(
                "Inc Number"
            ),
            "Description": st.column_config.TextColumn(
                "Description",
                width="large"
            ),
            "Work Notes": st.column_config.TextColumn(
                "Work Notes",
                width="large"
            ),
            "Incident Link": st.column_config.LinkColumn(
                "Open Incident",
                display_text="Open in ServiceNow"
            )
        }
    )

else:
    st.info("Select a row above to view the incident details.")
