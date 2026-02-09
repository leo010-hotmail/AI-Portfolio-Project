from azure.data.tables import TableServiceClient, TableEntity
import datetime
import uuid
import streamlit as st

# Load connection string from secrets
connection_string = st.secrets["azure"]["table_connection_string"]
table_name = st.secrets["azure"]["table_name"]

# Initialize service client
service = TableServiceClient.from_connection_string(conn_str=connection_string)
table_client = service.get_table_client(table_name=table_name)

# Create table if it doesn't exist
try:
    table_client.create_table()
except:
    pass

def log_message(role: str, message: str, session_id: str = None):
    """
    Logs a chat message to Azure Table Storage.

    role: 'user' or 'assistant'
    message: message content
    session_id: optional, to group messages from the same session
    """
    if not session_id:
        session_id = "default"

    entity = TableEntity()
    entity["PartitionKey"] = session_id  # group by session
    entity["RowKey"] = str(uuid.uuid4())  # unique ID
    entity["Timestamp"] = datetime.datetime.utcnow()
    entity["Role"] = role
    entity["Message"] = message

    table_client.create_entity(entity=entity)
