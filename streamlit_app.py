# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------
import streamlit as st
import pandas as pd
conn = st.connection("snowflake")
session = conn.session()
# ---------------------------------------------------------
# Page configuration
# This must appear before other Streamlit display commands.
# ---------------------------------------------------------

st.set_page_config(
    page_title="Search ServiceNow Tickets",
    page_icon="🔎",
    layout="wide"
)
# ---------------------------------------------------------
# Snowflake session
# ---------------------------------------------------------
session = get_active_session()
# ---------------------------------------------------------
# Page title and description
# ---------------------------------------------------------
st.title("🔎 Search ServiceNow Tickets")

st.write(
    """
    This app is linked to ServiceNow data in Snowflake. The report is
    designed to provide rapid visibility into support incidents, helping
    engineers and support teams identify, investigate, and resolve tickets
    more efficiently.
    """
)
# ---------------------------------------------------------
# Retrieve incidents from the Snowflake view
# ---------------------------------------------------------
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

try:
    incident_df = session.sql(incident_query).to_pandas()

except Exception as error:
    st.error("The incident data could not be retrieved from Snowflake.")
    st.exception(error)
    st.stop()
# ---------------------------------------------------------
# Handle an empty result
# ---------------------------------------------------------

if incident_df.empty:
    st.warning("No ServiceNow incidents were returned by the view.")
    st.stop()
# ---------------------------------------------------------
# Rename columns for display
# ---------------------------------------------------------
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
# ---------------------------------------------------------
# First dataframe: incident summary
# ---------------------------------------------------------
st.header("ServiceNow Incidents")

st.write(
    "Select a row to view the incident description and work notes."
)

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


incident_selection = st.dataframe(
    incident_list_df,
    hide_index=True,
    use_container_width=True,
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
        "State": st.column_config.TextColumn(
            "State"
        ),
        "Assigned To": st.column_config.TextColumn(
            "Assigned To"
        ),
        "Short Description": st.column_config.TextColumn(
            "Short Description",
            width="large"
        ),
        "Incident Link": st.column_config.LinkColumn(
            "Open Incident",
            display_text="Open in ServiceNow"
        )
    }
)


# ---------------------------------------------------------
# Second dataframe: selected incident details
# ---------------------------------------------------------

selected_rows = incident_selection.selection.rows

if selected_rows:

    selected_index = selected_rows[0]

    selected_incident_number = incident_list_df.iloc[
        selected_index
    ]["Inc Number"]

    incident_detail_df = incident_df.loc[
        incident_df["Inc Number"] == selected_incident_number,
        [
            "Opened Date",
            "Inc Number",
            "Description",
            "Work Notes",
            "Incident Link"
        ]
    ].copy()

    st.subheader(
        f"Incident Details: {selected_incident_number}"
    )

    st.dataframe(
        incident_detail_df,
        hide_index=True,
        use_container_width=True,
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
    st.info(
        "Select an incident in the table above to display its details."
    )
