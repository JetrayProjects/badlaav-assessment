from agents import Agent, Runner, WebSearchTool
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Make sure to add your OPENAI_API_KEY in the .env file
load_dotenv()

# Initialize the OpenAI Client
# Ensure OPENAI_API_KEY is set in your environment variables
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the Agent
# We use GPT-4o for full multimodal capabilities
agent = Agent(
    name="Multimodal Assistant",
    instructions="You are a helpful AI assistant capable of processing text, audio, images, and PDF files. "
                 "You can search the web and read files to help the user.",
    model="gpt-4o",
    tools=[WebSearchTool()]
)

async def run_agent(input_text: str):
    """
    Simple helper to run the agent with a single text input (non-streaming).
    """
    result = await Runner.run(agent, input_text)
    return result.final_output
