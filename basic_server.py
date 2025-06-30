from config import mcp                    # grab the shared instance
import tools.weather, tools.greetings       # noqa: E402  register the tools

if __name__ == "__main__":
    print("🔗 Basic server running on stdio …")
    mcp.run(transport="stdio")