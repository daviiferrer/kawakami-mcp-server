import argparse
import logging

from src.config import settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Kawakami MCP Server")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "streamable-http"])
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    args = parser.parse_args()

    logging.basicConfig(level=settings.log_level)
    logger = logging.getLogger(__name__)
    if args.transport == "streamable-http":
        logger.info("MCP Kawakami em http://%s:%s/mcp", args.host, args.port)

    from src.server import create_mcp

    mcp = create_mcp(host=args.host, port=args.port)
    mcp.settings.log_level = settings.log_level.lower()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
