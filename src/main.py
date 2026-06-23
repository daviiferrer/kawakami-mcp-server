import argparse
import os


def main() -> None:
    parser = argparse.ArgumentParser(description="Kawakami MCP Server")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "streamable-http"])
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.transport == "streamable-http":
        print(
            f"MCP Kawakami rodando em http://{args.host}:{args.port}/mcp (Streamable HTTP)",
            flush=True,
        )

    from src.server import create_mcp

    mcp = create_mcp(host=args.host, port=args.port)
    mcp.settings.log_level = os.environ.get("KWK_LOG_LEVEL", "ERROR").lower()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
