# Weather Hello Agent ☀️🤖

A minimal demo of an **MCP tool server** (weather + greetings) and a
**LangChain agent** that calls those tools.

## Features
- MCP server built with `fastmcp`
- Two example tools  
  - `/get_today_weather` → summary string  
  - `/greet` → “Hello <name>”
- LangChain agent that auto-discovers and calls the tools

## Quick start

```bash
git clone https://github.com/<you>/weather-hello-agent.git
cd weather-hello-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # put your keys here
python -m weatherhello.basic_server &  # run in background
python -m weatherhello.basic_agent     # talk to the agent
```

## Support me
Buy me a coffee at https://coff.ee/josjen
