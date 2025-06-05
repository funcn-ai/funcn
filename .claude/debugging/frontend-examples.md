# Frontend Integration Examples

This document provides example code for integrating with the CVI conversation API from various frontend frameworks.

## React/Next.js Example

```typescript
// hooks/useConversation.ts
import { useState } from 'react';

interface ConversationOverrides {
  conversation_name?: string;
  conversational_context?: string;
  custom_greeting?: string;
  properties?: {
    max_call_duration?: number;
    enable_recording?: boolean;
    enable_transcription?: boolean;
  };
}

interface ConversationResponse {
  provider_conversation_id: string;
  conversation_url: string;
  daily_token: string;
}

export function useConversation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversation, setConversation] = useState<ConversationResponse | null>(null);

  const startConversation = async (
    personaConfigId: string,
    overrides?: ConversationOverrides
  ) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/conversations/start-conversation', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          persona_config_id: personaConfigId,
          ...(overrides && { overrides }),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start conversation');
      }

      const data: ConversationResponse = await response.json();
      setConversation(data);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const endConversation = async (conversationId: string) => {
    try {
      const response = await fetch(`/api/v1/conversations/${conversationId}/end`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
        },
      });

      if (!response.ok && response.status !== 204) {
        throw new Error('Failed to end conversation');
      }
      
      setConversation(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  };

  return {
    conversation,
    loading,
    error,
    startConversation,
    endConversation,
  };
}

// components/ConversationStarter.tsx
import { useConversation } from '@/hooks/useConversation';

export function ConversationStarter() {
  const { startConversation, loading, error } = useConversation();
  
  const handleStartCall = async () => {
    try {
      const conversation = await startConversation('sales-agent-tim-v1', {
        conversation_name: 'Sales Demo Call',
        custom_greeting: 'Hi there! Ready to learn about our product?',
        properties: {
          max_call_duration: 1800, // 30 minutes
          enable_recording: true,
        }
      });
      
      // Redirect to video call
      window.open(conversation.conversation_url, '_blank');
    } catch (err) {
      console.error('Failed to start conversation:', err);
    }
  };
  
  return (
    <div>
      <button 
        onClick={handleStartCall} 
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded"
      >
        {loading ? 'Starting...' : 'Start Video Call'}
      </button>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  );
}
```

## Vue 3 Example

```vue
<!-- ConversationManager.vue -->
<template>
  <div>
    <button 
      @click="startCall" 
      :disabled="loading"
      class="btn btn-primary"
    >
      {{ loading ? 'Starting...' : 'Start Video Call' }}
    </button>
    
    <div v-if="error" class="alert alert-error mt-4">
      {{ error }}
    </div>
    
    <div v-if="conversation" class="mt-4">
      <p>Conversation ID: {{ conversation.provider_conversation_id }}</p>
      <a :href="conversation.conversation_url" target="_blank" class="btn btn-link">
        Join Call
      </a>
      <button @click="endCall" class="btn btn-secondary">
        End Call
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface ConversationResponse {
  provider_conversation_id: string;
  conversation_url: string;
  daily_token: string;
}

const loading = ref(false);
const error = ref<string | null>(null);
const conversation = ref<ConversationResponse | null>(null);

const apiKey = import.meta.env.VITE_API_KEY;
const personaConfigId = 'sales-agent-tim-v1';

async function startCall() {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch('/api/v1/conversations/start-conversation', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        persona_config_id: personaConfigId,
        overrides: {
          conversation_name: 'Vue Demo Call',
          conversational_context: 'User is testing from Vue application',
        }
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to start conversation');
    }
    
    conversation.value = await response.json();
    
    // Auto-open in new tab
    window.open(conversation.value.conversation_url, '_blank');
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unknown error';
  } finally {
    loading.value = false;
  }
}

async function endCall() {
  if (!conversation.value) return;
  
  try {
    const response = await fetch(
      `/api/v1/conversations/${conversation.value.provider_conversation_id}/end`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
        },
      }
    );
    
    if (!response.ok && response.status !== 204) {
      throw new Error('Failed to end conversation');
    }
    
    conversation.value = null;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to end call';
  }
}
</script>
```

## Plain JavaScript Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>CVI Conversation Demo</title>
</head>
<body>
  <h1>CVI Conversation Demo</h1>
  
  <div id="controls">
    <button id="startBtn" onclick="startConversation()">Start Video Call</button>
    <button id="endBtn" onclick="endConversation()" style="display:none;">End Call</button>
  </div>
  
  <div id="status"></div>
  <div id="error" style="color: red;"></div>

  <script>
    const API_KEY = 'your-api-key-here';
    const PERSONA_CONFIG_ID = 'sales-agent-tim-v1';
    let currentConversation = null;
    
    async function startConversation() {
      const statusEl = document.getElementById('status');
      const errorEl = document.getElementById('error');
      const startBtn = document.getElementById('startBtn');
      const endBtn = document.getElementById('endBtn');
      
      statusEl.textContent = 'Starting conversation...';
      errorEl.textContent = '';
      startBtn.disabled = true;
      
      try {
        const response = await fetch('/api/v1/conversations/start-conversation', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            persona_config_id: PERSONA_CONFIG_ID,
            overrides: {
              conversation_name: 'JavaScript Demo Call',
              custom_greeting: 'Hello from vanilla JavaScript!',
              properties: {
                max_call_duration: 600, // 10 minutes
              }
            }
          })
        });
        
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to start conversation');
        }
        
        currentConversation = await response.json();
        
        statusEl.innerHTML = `
          Conversation started!<br>
          ID: ${currentConversation.provider_conversation_id}<br>
          <a href="${currentConversation.conversation_url}" target="_blank">Join Call</a>
        `;
        
        startBtn.style.display = 'none';
        endBtn.style.display = 'inline-block';
        
        // Auto-open the call
        window.open(currentConversation.conversation_url, '_blank');
        
      } catch (error) {
        errorEl.textContent = `Error: ${error.message}`;
        startBtn.disabled = false;
      }
    }
    
    async function endConversation() {
      if (!currentConversation) return;
      
      const statusEl = document.getElementById('status');
      const errorEl = document.getElementById('error');
      const startBtn = document.getElementById('startBtn');
      const endBtn = document.getElementById('endBtn');
      
      try {
        const response = await fetch(
          `/api/v1/conversations/${currentConversation.provider_conversation_id}/end`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${API_KEY}`,
            }
          }
        );
        
        if (!response.ok && response.status !== 204) {
          throw new Error('Failed to end conversation');
        }
        
        statusEl.textContent = 'Conversation ended.';
        currentConversation = null;
        
        startBtn.style.display = 'inline-block';
        startBtn.disabled = false;
        endBtn.style.display = 'none';
        
      } catch (error) {
        errorEl.textContent = `Error: ${error.message}`;
      }
    }
  </script>
</body>
</html>
```

## Daily.co Integration Example

Once you have the `conversation_url` and `daily_token`, you can embed the video call:

```javascript
// Using Daily.co iframe
import DailyIframe from '@daily-co/daily-js';

async function joinCall(conversationUrl, dailyToken) {
  const callFrame = DailyIframe.createFrame({
    iframeStyle: {
      position: 'fixed',
      top: '0',
      left: '0',
      width: '100%',
      height: '100%',
    },
    showLeaveButton: true,
  });
  
  await callFrame.join({
    url: conversationUrl,
    token: dailyToken,
  });
  
  // Listen for events
  callFrame.on('participant-joined', (event) => {
    console.log('Participant joined:', event.participant);
  });
  
  callFrame.on('participant-left', (event) => {
    console.log('Participant left:', event.participant);
  });
  
  callFrame.on('left-meeting', () => {
    callFrame.destroy();
  });
}
```

## Error Handling Best Practices

```typescript
interface APIError {
  detail: string;
}

async function handleAPICall<T>(
  url: string,
  options: RequestInit
): Promise<T> {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error: APIError = await response.json();
      
      switch (response.status) {
        case 401:
          // Handle unauthorized - redirect to login
          window.location.href = '/login';
          throw new Error('Unauthorized');
        case 404:
          throw new Error(error.detail || 'Resource not found');
        case 502:
          throw new Error('Service temporarily unavailable');
        default:
          throw new Error(error.detail || `HTTP ${response.status} error`);
      }
    }
    
    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof TypeError) {
      // Network error
      throw new Error('Network error - please check your connection');
    }
    throw error;
  }
}
```

## WebSocket Integration Example

```javascript
function connectToConversationUpdates(conversationId) {
  const ws = new WebSocket(
    `ws://localhost:8000/api/v1/conversations/ws/${conversationId}`
  );
  
  ws.onopen = () => {
    console.log('Connected to conversation updates');
  };
  
  ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    console.log('Conversation update:', update);
    
    switch (update.event_type) {
      case 'status_update':
        if (update.status === 'ended') {
          // Handle conversation ended
          console.log('Conversation has ended');
        }
        break;
      case 'transcript_ready':
        // Handle transcript availability
        console.log('Transcript available:', update.transcript_url);
        break;
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('Disconnected from conversation updates');
  };
  
  return ws;
}
```