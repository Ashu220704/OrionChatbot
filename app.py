import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage,AIMessageChunk
from graphcode import graph,connection
import uuid
import sqlite3
import base64
from voice.audioutils import save_uploaded_audio,delete_audio
from voice.speechtotext import speech_to_text

# ----------------------------------------------------
# SQLite Connection
# ----------------------------------------------------

cursor = connection.cursor()


# ----------------------------------------------------
# Page
# ----------------------------------------------------

st.set_page_config(page_title="DeepCosmo")
# Load image
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_base64("images/n.jpg")   # Your image file

 

st.title("🌌  Orion")


# ----------------------------------------------------
# Session state
# ----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages =[]


if "current_thread" not in st.session_state:
    st.session_state.current_thread = "current_thread"
    print(st.session_state)

# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------

st.sidebar.title("💬 Conversations")

# ----------------------------------------------------
# New conversation button
# ----------------------------------------------------


if st.sidebar.button("➕ New Conversation"):
    thread_id = str(uuid.uuid4())

    cursor.execute("""
        SELECT COUNT(*)
        FROM Conversations
    """)

    count = cursor.fetchone()[0]

    conversation_name = f"Conversation {count + 1}"

    cursor.execute("""
        INSERT INTO Conversations(ThreadId, Title)
        VALUES (?, ?)
    """, (thread_id, conversation_name))

    st.session_state.current_thread = thread_id

    if "messages" in st.session_state:
        del st.session_state.messages

    st.rerun()
    print(st.session_state)

st.sidebar.divider()
# ----------------------------------------------------
# Existing conversations
# ----------------------------------------------------
cursor.execute("""
    SELECT ThreadId,
           Title
    FROM Conversations
    ORDER BY CreatedOn DESC
""")

rows = cursor.fetchall()

for thread_id, conversation_name in rows:
    if st.sidebar.button(conversation_name,key=thread_id):
        st.session_state.current_thread = thread_id

        st.write(f"Clicked Thread : {thread_id}")
        print(f"Clicked Thread : {thread_id}")

        if "messages" in st.session_state:
            del st.session_state.messages
        st.rerun()

st.sidebar.write("Current Thread")

st.sidebar.code(st.session_state.current_thread)

st.sidebar.divider()

# =====================================================
# config
# =====================================================

config = {
    "configurable": {
        "thread_id": st.session_state.current_thread
        }
    }

# =====================================================
# Load Messages from LangGraph
# =====================================================

state = graph.get_state(config=config)

st.session_state.messages = []

if state is not None:

    values = state.values

    if values and "messages" in values:

        for msg in values["messages"]:

            if isinstance(msg, HumanMessage):
                role = "user"

            elif isinstance(msg, AIMessage):
                role = "assistant"

            else:
                continue

            st.session_state.messages.append(
                {
                    "role": role,
                    "content": msg.content
                }
            )
            
# =====================================================
# Display Messages
# =====================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

# =====================================================
# Chat Input
# =====================================================

question = ""

user_input = st.chat_input("Ask me anything",accept_audio=True)

if not user_input:
    
    st.stop()

# =====================================================
# User typed a message
# =====================================================

if user_input.text:
    question = user_input.text.strip()

elif user_input.audio:
    with st.spinner("Transcribing audio..."):
        audio_path = save_uploaded_audio(user_input.audio)
        question = speech_to_text(audio_path)

        delete_audio(audio_path)

# =====================================================
# Empty speech check
# =====================================================   

if not question:
    st.warning("⚠️ Couldn't recognize your speech,please try again.")

    st.stop() 
# =====================================================
# Show  User Message
# =====================================================   
with st.chat_message("user"):

    st.write(question)

st.session_state.messages.append(
    {
        "role": "user",
        "content": question
    }
)


# =====================================================
# Assistant message
# =====================================================

with st.chat_message("assistant"):

    response_placeholder = st.empty()

    status = st.status("🤖 Agent Execution",expanded=True)

    answer = ""

    used_tools = []

    previous_node = ""

    for message , metadata in graph.stream(
        {
            "messages":[
                HumanMessage(content=question)
            ]
        },
        config=config,
        stream_mode="messages"
    ):

        node = metadata.get("langgraph_node","")

        # ---------------------------------------
        # Node Transition
        # ---------------------------------------

        if node != previous_node:
            if node == "chatbot":
                if previous_node == "":
                    status.write ("🤖 Chatbot Node")
                else:
                    status.write("🤖 Returning to Chatbot")

            elif node =="tools":
                status.write("🛠️ Tool Node")

            previous_node = node

        # ---------------------------------------
        # Tool Calls
        # ---------------------------------------

        if isinstance(message,ToolMessage):
            tool = message.name.replace("_"," ").title()

            if tool not in  used_tools:
                used_tools.append(tool)

                status.write(f"🔧 Calling **{tool}**")
                status.write(f"✅ {tool} Finished")

            # ---------------------------------------
        # AI Streaming
        # ---------------------------------------

        elif isinstance(message,(AIMessageChunk,AIMessage)):
            if message.content:
                if isinstance(message.content,str):
                    answer +=  message.content

                else:
                    answer += "".join(
                        part.get("text","")
                        for part in message.content
                        if isinstance(part,dict)
                    )

                response_placeholder.markdown(answer)


    # ---------------------------------------
    # Finish
    # ---------------------------------------

    status.write("🏁 Execution Complete")

    status.update(
        label=f"✅ Completed ({len(used_tools)} tool(s))",
        state="complete",
        expanded=False,
    )

st.session_state.messages.append(
    {
        "role": "assistant",
        "content": answer
    }
)    