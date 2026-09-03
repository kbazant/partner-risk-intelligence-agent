import contextlib
import os
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import FastMCP

from app.mcp_tools import TOOL_NAMES, register_mcp_tools

from mcp.server.transport_security import TransportSecuritySettings


APP_NAME = os.getenv("APP_NAME", "Orion Devices Partner Risk MCP")
APP_ENV = os.getenv("APP_ENV", "local")


def csv_env(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


MCP_ALLOWED_HOSTS = csv_env(
    "MCP_ALLOWED_HOSTS",
    "127.0.0.1:*,localhost:*,[::1]:*",
)

MCP_ALLOWED_ORIGINS = csv_env(
    "MCP_ALLOWED_ORIGINS",
    "http://127.0.0.1:*,http://localhost:*,http://[::1]:*",
)

mcp = FastMCP(
    name=APP_NAME,
    host="0.0.0.0",
    stateless_http=True,
    json_response=True,
    streamable_http_path="/",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=MCP_ALLOWED_HOSTS,
        allowed_origins=MCP_ALLOWED_ORIGINS,
    ),
)


register_mcp_tools(mcp)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start the MCP session manager for Streamable HTTP.
    """
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title=APP_NAME,
    version="0.2.0",
    description="Local MCP server for the Orion Devices Partner Risk Ranking Agent.",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, Any]:
    """
    Simple local health check.

    This is a normal FastAPI endpoint, not an MCP tool.
    """

    return {
        "status": "ok",
        "service": APP_NAME,
        "environment": APP_ENV,
        "phase": "Phase 8 - MCP tools",
        "mcp_endpoint": "/mcp",
        "tools_registered": TOOL_NAMES,
    }


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(
        {
            "message": "Orion Devices Partner Risk MCP server is running locally.",
            "health": "/health",
            "mcp": "/mcp",
            "tools_registered": TOOL_NAMES,
        }
    )


app.mount("/mcp", mcp.streamable_http_app())