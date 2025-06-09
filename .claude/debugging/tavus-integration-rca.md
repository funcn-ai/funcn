# Tavus Integration Root Cause Analysis

## Summary
The video agent service (Tavus integration) has a schema mismatch issue that prevents proper operation. The core issue is that the Tavus API returns responses in a different format than our Pydantic models expect.

## Issues Identified

### 1. Schema Mismatch in list_personas (FIXED)
- **Problem**: Tavus API returns `{"data": [...], "total_count": N}` but our `ProviderPersonaListResponse` schema expects `{"personas": [...]}`
- **Impact**: Causes validation error when listing personas
- **Fix Applied**: Transform the response in `video_agent_service.py` line 506-507:
  ```python
  if isinstance(response_data, dict) and "data" in response_data:
      response_data = {"personas": response_data["data"]}
  ```

### 2. Missing Replica ID for Conversations
- **Problem**: Starting conversations requires a valid `replica_id` which represents a trained voice/video model in Tavus
- **Impact**: Cannot start conversations without a valid replica
- **Current Status**: Need to either:
  - Create a replica through Tavus API
  - Use an existing replica from the account
  - Make replica_id optional in our schema if Tavus supports it

### 3. Potential Schema Mismatches (To Investigate)
- The transformation pattern seen in `list_personas` might be needed for other endpoints
- Need to verify response formats for:
  - `create_persona`
  - `get_persona_details`
  - `start_conversation`

## Testing Results

### ✅ Working:
- Tavus API connectivity and authentication
- Creating personas
- Deleting personas
- Getting persona details

### ❌ Not Working:
- Starting conversations (requires valid replica_id)

## Recommended Actions

1. **Immediate Fix**: Apply the same response transformation pattern to other methods that might have schema mismatches

2. **Replica Management**: 
   - Add a method to list available replicas
   - Store valid replica IDs in configuration
   - Update PersonaConfig to include a default replica_id

3. **Schema Updates**:
   - Review all Pydantic models against actual Tavus API responses
   - Consider creating adapter functions or a middleware layer to transform responses

4. **Testing**:
   - Add integration tests that mock Tavus API responses
   - Create a test fixture with valid replica_id for conversation testing

## Code Changes Made

### File: app/services/conversations/video_agent_service.py
```python
# Line 506-507: Fixed list_personas response transformation
if isinstance(response_data, dict) and "data" in response_data:
    response_data = {"personas": response_data["data"]}
```

## Next Steps

1. Get or create a valid replica_id for testing conversations
2. Apply similar transformations to other API methods if needed
3. Update schemas to match actual Tavus API responses
4. Add comprehensive error handling for replica-related errors
5. Document the replica requirement in README or setup instructions