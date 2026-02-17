import asyncio
import os
import base64
import mimetypes
from pathlib import Path
from dotenv import load_dotenv
from agents import Runner
from api.agent import agent
import traceback

from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI Client for Transcription
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_file_as_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

async def transcribe_audio(file_path: str) -> str:
    print("(transcribing audio...) ", end="", flush=True)
    with open(file_path, "rb") as audio_file:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    print("Done.")
    return transcript.text

async def parse_input(user_input: str):
    """
    Parses user input for special commands like /image, /audio, /pdf.
    Returns the formatted input for the agent (str or list[dict]).
    """
    parts = user_input.split()
    if not parts:
        return user_input

    command = parts[0].lower()
    if command in ["/image", "/audio", "/pdf"] and len(parts) >= 2:
        file_path = parts[1]
        remaining_text = " ".join(parts[2:])
        
        try:
            if not os.path.exists(file_path):
                print(f"Error: File not found at {file_path}")
                return user_input

            content_items = []
            
            # Add text if present
            if remaining_text:
                content_items.append({"type": "input_text", "text": remaining_text})

            if command == "/image":
                base64_data = read_file_as_base64(file_path)
                # Detect mime type or default to png
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = "image/png"
                    
                content_items.append({
                    "type": "input_image", 
                    "image_url": f"data:{mime_type};base64,{base64_data}"
                })
                return [{"role": "user", "content": content_items}]
                
            elif command == "/audio":
                # Transcribe audio using OpenAI Whisper
                transcript_text = await transcribe_audio(file_path)
                
                # Format as a user text message with context
                full_text = f"[Audio Transcript]: {transcript_text}"
                if remaining_text:
                    full_text = f"{remaining_text}\n\n{full_text}"
                    
                return full_text
                
            elif command == "/pdf":
                 base64_data = read_file_as_base64(file_path)
                 content_items.append({
                    "type": "input_file",
                    "file_data": f"data:application/pdf;base64,{base64_data}",
                    "filename": Path(file_path).name
                })
                 return [{"role": "user", "content": content_items}]

        except Exception as e:
            print(f"Error processing file: {e}")
            traceback.print_exc()
            return user_input

    return user_input

async def main():
    print("CLI Chat Agent (type 'quit' to exit)")
    print("Commands: /image <path> [text], /audio <path> [text], /pdf <path> [text]")
    print()
    history = []
    
    while True:
        try:
            user_input = input("\nUser: ")
        except EOFError:
            break
            
        if user_input.lower() in ["quit", "exit"]:
            break
        
        if not user_input.strip():
            continue

        # Parse input for files
        agent_input = await parse_input(user_input)
        

        if isinstance(agent_input, list):
             # parsed input is a list of dicts with role/content
             history.extend(agent_input)
        else:
             history.append({"role": "user", "content": agent_input})
        
        print("Assistant: ", end="", flush=True)
        
        try:
            print("(thinking...) ", end="", flush=True)
            
            # We pass the agent and the FULL history to the runner
            result = await Runner.run(agent, history)
            
            response_text = result.final_output
            print(f"\rAssistant: {response_text}")
        
            history.append({"role": "assistant", "content": response_text})

        except Exception as e:
            print(f"\nError: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
