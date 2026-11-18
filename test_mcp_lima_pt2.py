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

    # 4. Info (corrected to not pass 'instance')
    try:
        info_res = await server.call_tool("lima_info", {})
        results['lima_info'] = info_res.structured_content
    except Exception as e:
        results['lima_info'] = str(e)

    # test lima_edit
    try:
        # Create
        await server.call_tool("lima_create", {"instance": instance_name, "template": "default"})
        
        # Edit
        edit_res = await server.call_tool("lima_edit", {"instance": instance_name, "memory": "2GiB"})
        results['lima_edit'] = edit_res.structured_content
        
        # Stop & Delete
        await server.call_tool("lima_stop", {"instance": instance_name})
        await server.call_tool("lima_delete", {"instance": instance_name, "confirm": True})
    except Exception as e:
        results['lima_edit_error'] = str(e)

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
