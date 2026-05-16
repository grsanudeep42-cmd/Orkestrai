# Cinematic UI Evolution

The frontend has been entirely rewritten to visualize the autonomous AI ecosystem, making the orchestration feel alive.

## Core Features

### Metrics Dashboard
- **Active LLM Badge**: Streams the current AI provider handling the generation block in real-time.
- **Autonomous Retries**: Tracks the number of times the system has caught and corrected its own mistakes. Pulsing animations trigger on increment.
- **Execution Time**: Real-time summation of LLM latency per generation step.

### Live Agent Thinking Feed
The event log has been transformed from a basic list into a cinematic stream:
- Colors dictate state (`bg-tertiary` for complete, `bg-warning` for critiques, `bg-error` for retries).
- The `agent_thinking` events gently pulse.
- When the `AuditAgent` triggers a retry, the active log entry receives a glowing red border (`glow-error`) and prominently displays the failure reason and critique.

### Dynamic Node Statuses
The agent swarm dashboard dynamically tracks the pipeline state. When a correction loop triggers, a "SELF-CORRECTION" visual cue pulses directly beneath the active agent, representing the invisible background work to the end user.
