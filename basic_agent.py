# interactive_agent_client.py  –  prompt-less version
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import config

TOOL_AGENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI assistant. "
            "When necessary, call the provided tools to get information "
            "before answering the user."
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),   # <-- required!
    ]
)

async def main() -> None:
    # 1️⃣  Launch the MCP server in a subprocess (stdio transport)
    client = MultiServerMCPClient(
        {
            "weatherhello": {
                "command": "python",
                "args": ["mcp_server.py"],   # your server launcher
                "transport": "stdio",
            }
        }
    )

    # 2️⃣  Discover the MCP tools
    tools = await client.get_tools()

    # 3️⃣  Build the agent WITHOUT passing a prompt
    llm   = ChatOpenAI(model=config.OPENAI_MODEL,api_key=config.OPENAI_API_KEY)    # any function-calling model
    core = create_openai_tools_agent(llm, tools, TOOL_AGENT_PROMPT)
    agent = AgentExecutor(agent=core, tools=tools, verbose=True)

    # 4️⃣  Interactive loop
    loop = asyncio.get_running_loop()
    print("🔗 Connected – type a question (exit/quit to leave)")
    while True:
        user_q = await loop.run_in_executor(None, input, "\nYou: ")
        if user_q.strip().lower() in {"exit", "quit"}:
            break
        try:
            result = await agent.ainvoke({"input": user_q})
            print("Assistant:", result["output"])
        except Exception as err:
            print("⚠️ ", err)

    await client.aclose()
    print("Good-bye!")


if __name__ == "__main__":
    asyncio.run(main())