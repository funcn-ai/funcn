# Frontend API Contract for CVI Conversations

This document describes the API contract between the frontend and backend for starting and managing CVI conversations.

## Prerequisites

1. **Authentication**: Frontend must be authenticated and have a valid API key
2. **Persona Configuration**: A persona config must exist in the database with:
   - Valid `provider_persona_id` (from Tavus)
   - Valid `provider_replica_id` (from Tavus)
   - Associated with the user's tenant/service

## Starting a Conversation

### Endpoint
```
POST /api/v1/conversations/start-conversation
```

### Request Headers
```
Authorization: Bearer <api_key>
Content-Type: application/json
```

### Request Body
```json
{
  "persona_config_id": "string",  // Required: ID of the persona config to use
  "overrides": {                  // Optional: Override persona defaults
    "conversation_name": "string",
    "conversational_context": "string", 
    "custom_greeting": "string",
    "properties": {
      "max_call_duration": 300,   // seconds
      "enable_recording": true,
      "enable_transcription": true,
      // Other Tavus-specific properties
    }
  }
}
```

### Response (Success - 200 OK)
```json
{
  "provider_conversation_id": "c966da19d15f5424",
  "conversation_url": "https://tavus.daily.co/c966da19d15f5424",
  "daily_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Response (Error - 404 Not Found)
```json
{
  "detail": "Persona configuration with id 'invalid-id' not found."
}
```

### Response (Error - 502 Bad Gateway)
```json
{
  "detail": "Invalid response from CVI provider."
}
```

## Example Frontend Integration

### 1. Minimal Request (Using All Defaults)
```javascript
const response = await fetch('/api/v1/conversations/start-conversation', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    persona_config_id: 'sales-agent-tim-v1'
  })
});

const data = await response.json();
// Use data.conversation_url to join the video call
// Use data.daily_token for Daily.co authentication
```

### 2. Request with Overrides
```javascript
const response = await fetch('/api/v1/conversations/start-conversation', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    persona_config_id: 'sales-agent-tim-v1',
    overrides: {
      conversation_name: 'Demo Call with John Doe',
      conversational_context: 'John is interested in our enterprise plan. Focus on scalability features.',
      custom_greeting: 'Hi John! Great to connect with you today.',
      properties: {
        max_call_duration: 1800,  // 30 minutes
        enable_recording: true
      }
    }
  })
});
```

## Getting Conversation Details

### Endpoint
```
GET /api/v1/conversations/{provider_conversation_id}
```

### Response
```json
{
  "conversation_id": "c966da19d15f5424",
  "status": "active",  // active, ended, error
  "created_at": "2025-06-04T22:15:24.738392Z",
  "ended_at": null,
  "error": null
}
```

## Ending a Conversation

### Endpoint
```
POST /api/v1/conversations/{provider_conversation_id}/end
```

### Response
```
204 No Content
```

## WebSocket Updates (Real-time)

### Endpoint
```
WebSocket: ws://localhost:8000/api/v1/conversations/ws/{provider_conversation_id}
```

### Events
```json
{
  "event_type": "status_update",
  "conversation_id": "c966da19d15f5424",
  "status": "ended",
  "timestamp": "2025-06-04T22:20:15.123Z"
}
```

## Server-Sent Events (Alternative to WebSocket)

### Endpoint
```
GET /api/v1/conversations/{provider_conversation_id}/events
```

### Event Stream
```
event: status_update
data: {"conversation_id": "c966da19d15f5424", "status": "ended"}

event: transcript_ready
data: {"conversation_id": "c966da19d15f5424", "transcript_url": "..."}
```

## Error Handling

### Common Error Codes
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (invalid/missing API key)
- `404` - Not Found (persona config or conversation not found)
- `500` - Internal Server Error
- `502` - Bad Gateway (CVI provider error)

### Error Response Format
```json
{
  "detail": "Human-readable error message"
}
```

## Important Notes

1. **Persona Config IDs**: These must be pre-configured in the database. Frontend should fetch available personas from `/api/v1/personas` endpoint.

2. **Daily Token**: The `daily_token` is used to authenticate with Daily.co video service. It's pre-configured for the conversation room.

3. **Conversation URL**: This is the actual video call URL. Frontend should redirect or embed this URL for the video experience.

4. **Callbacks**: The backend handles Tavus webhooks automatically. Frontend doesn't need to worry about webhook configuration.

5. **Multi-tenancy**: The API automatically scopes requests to the authenticated user's tenant/service.

## Testing with cURL

### Start Conversation
```bash
curl -X POST http://localhost:8000/api/v1/conversations/start-conversation \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "persona_config_id": "test-sales-agent-1",
    "overrides": {
      "conversation_name": "Test Call",
      "custom_greeting": "Hello! This is a test."
    }
  }'
```

### Get Details
```bash
curl http://localhost:8000/api/v1/conversations/c966da19d15f5424 \
  -H "Authorization: Bearer your-api-key"
```

### End Conversation
```bash
curl -X POST http://localhost:8000/api/v1/conversations/c966da19d15f5424/end \
  -H "Authorization: Bearer your-api-key"
```