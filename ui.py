import streamlit as st
import asyncio
import base64
import os
from dotenv import load_dotenv
from agents import Runner
from api.agent import agent
from openai import AsyncOpenAI
import mimetypes

# Load environment variables
load_dotenv()

# Initialize OpenAI Client for Transcription
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Multimodal Agent", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

def read_file_as_base64(file) -> str:
    return base64.b64encode(file.read()).decode("utf-8")

async def transcribe_audio(file) -> str:
    transcript = await client.audio.transcriptions.create(
        model="whisper-1", 
        file=file
    )
    return transcript.text

async def get_agent_response(user_input, file_uploads=None):
    # Add user message to history
    message_content = []
    
    if user_input:
        message_content.append({"type": "input_text", "text": user_input})
        
    if file_uploads:
        for uploaded_file in file_uploads:
            # Reset file pointer
            uploaded_file.seek(0)
            
            if uploaded_file.type.startswith("image"):
                base64_data = read_file_as_base64(uploaded_file)
                message_content.append({
                    "type": "input_image",
                    "image_url": f"data:{uploaded_file.type};base64,{base64_data}"
                })
            elif uploaded_file.type == "application/pdf":
                base64_data = read_file_as_base64(uploaded_file)
                message_content.append({
                    "type": "input_file",
                    "file_data": f"data:application/pdf;base64,{base64_data}",
                    "filename": uploaded_file.name
                })
            elif uploaded_file.type.startswith("audio"):
                # Transcribe audio
                transcript = await transcribe_audio(uploaded_file)
                # Append transcript to text
                if user_input:
                    message_content[0]["text"] += f"\n\n[Audio Transcript]: {transcript}"
                else:
                    message_content.append({"type": "input_text", "text": f"[Audio Transcript]: {transcript}"})

    # Add to history
    st.session_state.history.append({"role": "user", "content": message_content})
    
    # Run Agent
    result = await Runner.run(agent, st.session_state.history)
    
    # Add assistant response to history
    st.session_state.history.append({"role": "assistant", "content": result.final_output})
    return result.final_output

# UI Layout
st.title("🤖 Multimodal AI Agent")

# Chat Area
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        # Display content properly
        content = msg["content"]
        if isinstance(content, str):
            st.write(content)
        elif isinstance(content, list):
            for item in content:
                if item["type"] == "input_text":
                    st.write(item["text"])
                elif item["type"] == "input_image":
                    st.image(item["image_url"])
                elif item["type"] == "input_file":
                    st.write(f"📎 PDF: {item['filename']}")

if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

# Input Area
# We use a popover to simulate the "plus" icon for attachments
with st.popover("➕ Attach files"):
    uploaded_files = st.file_uploader(
        "Upload Images, Audio, or PDFs", 
        type=["png", "jpg", "jpeg", "mp3", "wav", "m4a", "pdf"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.file_uploader_key}"
    )

user_input = st.chat_input("Type your message here...")

if user_input or (uploaded_files and st.button("Send Files")):
    # Check if we should process
    if user_input or uploaded_files:
        with st.chat_message("user"):
            if user_input:
                st.write(user_input)
            if uploaded_files:
                st.write(f"Attached {len(uploaded_files)} files")
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = asyncio.run(get_agent_response(user_input, uploaded_files if uploaded_files else None))
                st.write(response)
                
                # Clear the file uploader for next time
                st.session_state.file_uploader_key += 1
                st.rerun()
