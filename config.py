from dotenv import load_dotenv
load_dotenv() 

"""Central config for Backlog Factory."""
import os
import openai
from mcp.server.fastmcp import FastMCP

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

OPENAI_API_KEY = openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set (environment or .env).")

mcp = FastMCP("WeatherHello")   # single, shared instance
tool = mcp.tool     
