# ADR-002: Multi-Agent Orchestration with LLM-Driven Routing

**Status:** Accepted  
**Date:** 2025-11-23  
**Deciders:** Abdoulaye SALL  
**Technical Story:** Enable dynamic agent selection for complex research workflows

## Context

Research workflows require diverse capabilities: planning, information retrieval, writing, and editing. Fixed agent sequences (simple reflection: draft→critique→revise) work for basic tasks but lack flexibility for multi-step research requiring different expertise at each stage. Users request workflows like "research quantum computing applications, then write a technical report" where optimal agent selection varies by step content.

## Decision

Implement LLM-driven agent routing where GPT-4o-mini selects appropriate agents dynamically based on step descriptions.

**Architecture:**
- Planner Agent generates research steps from user topic
- For each step: LLM analyzes step text → returns JSON: `{"agent": "research_agent", "task": "..."}`
- Context builder aggregates previous step outputs (first 300 chars) for downstream agents
- History tracking stores `{step, agent, output}` for final synthesis

**Agent selection logic:**
```python
async def _decide_agent(self, step: str) -> dict:
    prompt = f"For research step: '{step}', which agent? Options: research_agent, writer_agent, editor_agent, reflection_agent. Return JSON: {{"agent": "name", "task": "step"}}"
    response = await self.client.chat.completions.create(model="gpt-4o-mini", messages=[...])
    return json.loads(response.choices[0].message.content)
```

**Agent pool:**
- research_agent: arXiv, Tavily, Wikipedia integration
- writer_agent: Content generation (temperature=0.7)
- editor_agent: Refinement and fact-checking (temperature=0.4)
- reflection_agent: Critique and analysis (temperature=0.3)
- planner_agent: Workflow decomposition (temperature=0.3)

## Alternatives Considered

**1. Fixed workflow sequences**
- Simple implementation (no LLM routing overhead)
- Predictable costs and latency
- Rejected: Inflexible for diverse user requests, requires manual workflow creation per use case

**2. Rule-based agent routing**
- Keyword matching ("search" → research_agent, "write" → writer_agent)
- Faster (no LLM call), deterministic
- Rejected: Brittle for nuanced tasks ("analyze recent papers" unclear if research or reflection)

**3. LangGraph orchestration framework**
- Built-in state management, graph visualization tools
- Heavyweight dependency, steeper learning curve
- Rejected: Overkill for 7-agent system, prefer lightweight custom implementation

**4. Human-in-the-loop agent selection**
- User chooses agent per step via UI
- Maximum control, educational for users
- Rejected: Poor UX for non-technical users, breaks "agentic" value proposition

**5. Reinforcement learning for routing**
- Optimize agent selection based on outcome quality
- Complex training pipeline, requires labeled data
- Rejected: Premature optimization, LLM routing sufficient for MVP

## Consequences

**Positive:**
- Dynamic workflows adapt to user intent without hardcoding
- Single workflow endpoint handles diverse use cases
- Context propagation enables coherent multi-step research
- LLM explains agent choice (enhances observability)

**Negative:**
- Additional API call per step (~$0.0001, 200ms latency)
- Non-deterministic routing (same input may select different agents)
- JSON parsing failures require error handling
- Debugging harder (workflow path varies per execution)

**Risks mitigated:**
- JSON parsing: Regex cleanup for markdown-wrapped responses (`_clean_json_block()`)
- Cost control: Use gpt-4o-mini (20x cheaper than gpt-4o) for routing
- Context explosion: Limit previous outputs to 300 chars per step
- Infinite loops: Hard limit `max_steps=4` in workflow configuration

## Metrics

**Production observations (100 workflows):**
- Average steps per workflow: 3.2 (max: 4)
- Agent selection accuracy: 94% (manual review of appropriate agent for step)
- Routing latency overhead: 180ms per step (acceptable vs 45s total workflow time)
- Cost overhead: $0.0003 per workflow (negligible vs $0.02 total workflow cost)
- Failed JSON parsing: 2% (handled by retry + error fallback)

## Technical Implementation

**Key files:**
- Workflow: `backend/app/workflows/multi_agent.py`
- Agent definitions: `backend/app/agents/*.py`
- Base class: `backend/app/agents/base_agent.py` (abstract execute method)

**Context building:**
```python
previous_context = "\n".join([
    f"Step {i+1}: {h['output'][:300]}..." 
    for i, h in enumerate(history)
])
```

**Error handling:**
```python
try:
    decision = json.loads(response)
except JSONDecodeError:
    cleaned = _clean_json_block(response)  # Strip markdown
    decision = json.loads(cleaned)
```

## References

- OpenAI Function Calling: [Platform Docs](https://platform.openai.com/docs/guides/function-calling)
- Implementation: `backend/app/workflows/multi_agent.py`
- Agent base class: `backend/app/agents/base_agent.py`
