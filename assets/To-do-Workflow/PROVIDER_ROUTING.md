# Multi-Provider Routing

To ensure high availability and intelligent load distribution, OrkestrAI utilizes a sophisticated multi-provider routing system.

## Provider Abstraction

The `BaseProvider` interface standardizes interactions across completely different AI provider paradigms (OpenAI SDK vs. Direct HTTP APIs). Currently implemented providers:
- `GeminiProvider`
- `GroqProvider`
- `OpenAIProvider`
- `OpenRouterProvider` (Anthropic Claude, etc.)

## Dynamic Routing & Fallback

The `ProviderRouter` handles execution securely:
1. **Prioritization**: Requests attempt the primary fast providers first (Gemini/Groq).
2. **Waterfall Fallback**: If a provider fails (e.g., rate limit, server error), the router catches the exception, logs a `provider_fallback` event, and automatically attempts the next provider in the chain (OpenAI -> OpenRouter).
3. **Event Streaming**: The router broadcasts `provider_selected` directly to the frontend WebSocket, updating the "Active LLM" UI badge in real time without polling.
