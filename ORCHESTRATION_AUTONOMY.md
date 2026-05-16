# Orchestration Autonomy

OrkestrAI has evolved from a linear task-runner into a dynamic, stateful autonomous operating system.

## The Shared Memory Context

Agents no longer operate in a vacuum. A persistent, in-memory `SharedContext` tracks the ecosystem's state across the entire orchestration lifecycle:

1. **Cumulative Learning**: Each agent's output is injected into the global context (`memory['shared_context']`).
2. **Context Passing**: Every subsequent agent receives the complete context, ensuring the Builder Agent writes code specifically tailored to the Architecture Agent's decisions.
3. **Real-time Event Emission**: When memory is updated, a `memory_updated` websocket event is fired, allowing the frontend to trace the expanding knowledge graph.

## Autonomous Correction Loop

The `AuditAgent` serves as the system's immune system, detecting hallucinations, architectural flaws, and scope creep.

1. **Critique Generation**: If an agent produces sub-standard work, the AuditAgent generates a rigorous critique and sets `needs_retry: true`.
2. **Feedback Injection**: The critique is injected directly into the active agent's `memory["audit_feedback"]`.
3. **Execution Retry**: The Orchestration Engine detects the failure state and reruns the agent, passing the critique.
4. **Retry Thresholds**: Retries are globally clamped to prevent infinite loops (default max: 2).
