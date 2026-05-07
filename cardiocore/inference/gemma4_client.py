# OWNER: Teammate A
# DAY:   2
# PURPOSE: HTTP client for the vLLM Gemma 4 server running on Instance A
#
# This module is called by all MCP tools to get clinical reasoning from Gemma 4.
# Teammate A writes the full implementation here.
#
# Expected interface (do not change function names):
#
#   from inference.gemma4_client import get_client
#   client = get_client()
#   text = client.chat(system_prompt, user_text, images_b64=[...])
#   result = client.parse_json(text)
#   ok = client.healthy()

# TODO: Teammate A implements this on Day 2
# See implementation guide for full code

def get_client():
    raise NotImplementedError("Teammate A: implement gemma4_client.py on Day 2")
