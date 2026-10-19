"""
Your MCP server. ← UNIT 4, MILESTONE 1

Right now your tools only exist inside your own program. Nothing else can reach
them. MCP is an agreed shape you wrap a tool in so that anything speaking the
same protocol can call it — your agent today, a different agent tomorrow,
someone else's app after that.

`search_listings` and `compare_prices` are registered below. `search_listings`
is the first MCP tool; `compare_prices` is the second and exposes the existing
price-summary function through the same protocol.

    python mcp_server.py        starts the server (it will just sit there — that's right)
    python mcp_client.py        asks the server what it offers

─────────────────────────────────────────────────────────────────────────────
Both registered functions publish descriptions and typed inputs through MCP.
`search_listings` accepts a description plus optional size and price ceiling;
`compare_prices` accepts a list of listing dictionaries. Their implementations
remain in `tools.py`, and the server returns their native list and summary-dict
shapes. `agent.py::run_agent` calls them through `mcp_client.call_tool()`.
─────────────────────────────────────────────────────────────────────────────
"""

from mcp.server.fastmcp import FastMCP

from tools import (
    compare_prices as _compare_prices_impl,
    search_listings as _search_listings_impl,
)

# log_level="WARNING" keeps the server from printing an INFO line for every
# request. Without it your terminal fills with "Processing request of type
# CallToolRequest" and the output you actually care about scrolls away.
mcp = FastMCP("fitfindr", log_level="WARNING")


@mcp.tool()
def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """Find listings matching keywords, with optional exact size and inclusive price filters.

    Returns listing dictionaries with id, title, description, category,
    style_tags, size, condition, price, colors, brand, and platform. Returns
    an empty list when no listings match.
    """
    return _search_listings_impl(description, size, max_price)


@mcp.tool()
def compare_prices(listings: list[dict]) -> dict:
    """Summarize matching listings with count, lowest, highest, and average price.

    For an empty list, returns count 0 and None for lowest, highest, and average.
    """
    return _compare_prices_impl(listings)
#
# Two notes on the block above.
#
# The registered name is the *function* name — so the block above registers
# "search_listings", which is exactly what call_tool("search_listings", ...)
# asks for. That is also why the import at the top of this file brings the real
# implementation in under an alias: without it, the registered function and the
# one it calls would be the same name, and the tool would call itself.
#
# FastMCP builds the input schema from your type hints, which is why the hints
# are not optional here. `description: str` becomes a required string;
# `max_price: float | None = None` becomes an optional number. Getting these
# wrong is the most common reason a call is rejected.


if __name__ == "__main__":
    mcp.run()
