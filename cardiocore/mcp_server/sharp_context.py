# OWNER: Binula
# DAY:   3
# PURPOSE: SHARP context middleware for Prompt Opinion integration
#
# Prompt Opinion sends patient context via HTTP headers:
#   X-FHIR-Server-URL   â€” URL of the FHIR server for this patient
#   X-FHIR-Access-Token â€” Bearer token for FHIR server access
#   X-Patient-Id        â€” Patient identifier
#
# This middleware extracts those headers and makes them available
# to all request handlers via get_sharp_context().
#
# Usage in a FastAPI endpoint:
#   from mcp_server.sharp_context import get_sharp_context
#   ctx = get_sharp_context()
#   if ctx.has_fhir:
#       # fetch patient data from ctx.fhir_server_url

# TODO: Binula implements this on Day 3
# See implementation guide for full code
