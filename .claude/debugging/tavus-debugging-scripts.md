# Tavus Integration Debugging Scripts

This directory contains scripts for debugging and testing the Tavus video agent service integration.

## Scripts

### 1. `test_tavus_integration.py`
Basic connectivity and API testing script that:
- Tests Tavus API connectivity and authentication
- Lists existing personas and searches for replica IDs
- Tests persona creation/deletion lifecycle
- Attempts conversation flow (if replica ID available)

### 2. `test_conversation_flow.py`
Comprehensive conversation flow testing with pre-filled test data that simulates the full API flow.

**Features:**
- Pre-configured test persona and user data
- Valid replica ID: `r9fa0878977a`
- Safety controls to prevent accidental API usage
- Command-line options for different test scenarios

**Usage:**
```bash
# Run with Doppler (required for environment variables)
source .venv/bin/activate
doppler run --project cvi-backend-template --config dev -- python scripts/debugging/test_conversation_flow.py

# Options:
# --skip-persona     Skip persona creation (use mock data)
# --skip-conversation Skip conversation start (default - saves API credits)
# --full-test        Run full test including conversation (COSTS API CREDITS!)
```

**Default Behavior (SAFE MODE):**
- Creates a test persona
- Sets up all required configurations
- SKIPS actual conversation start
- Cleans up persona

**Test Data:**
- Persona: "Test Sales Agent Tim"
- Replica ID: `r9fa0878977a` (valid stock replica)
- User: John Doe from Example Corp
- Conversation: 3-minute test call

## Important Notes

1. **API Credits**: Starting conversations costs API credits. The scripts default to SAFE MODE which skips conversation start.

2. **Replica IDs**: Conversations require valid replica IDs. The test script includes a valid stock replica ID.

3. **Environment**: Always run with Doppler for proper environment configuration:
   ```bash
   doppler run --project cvi-backend-template --config dev -- python <script>
   ```

4. **Multi-tenancy**: The scripts simulate multi-tenant context with test tenant/service IDs.

## Discovered Issues

See `tavus-integration-rca.md` for root cause analysis of issues found:
- Schema mismatches between Tavus API and our models
- Replica ID requirements
- Response transformation needs

## Linear Tracking

All issues are tracked in the [Tavus Integration Debugging](https://linear.app/greyhaven/project/tavus-integration-debugging-1ed347f2f962) project.