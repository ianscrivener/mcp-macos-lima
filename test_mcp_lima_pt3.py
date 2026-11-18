import asyncio
import json
import time
from mcp_lima.server import create_server

async def main():
    server = create_server()
    client_name = "gemini"
    timestamp = int(time.time())
    instance_name = f"mcp-delete-test-{client_name}-{timestamp}"
    
    results = {}
    try:
        # Start (creates implicitly)
        await server.call_tool("lima_start", {"instance": instance_name})
        
        # Restart
        restart_res = await server.call_tool("lima_restart", {"instance": instance_name})
        results['lima_restart'] = restart_res.structured_content
        
        # Stop & Delete
        await server.call_tool("lima_stop", {"instance": instance_name})
        await server.call_tool("lima_delete", {"instance": instance_name, "confirm": True})
    except Exception as e:
        results['lima_restart_error'] = str(e)

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
