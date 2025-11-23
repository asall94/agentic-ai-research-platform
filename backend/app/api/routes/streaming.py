import asyncio
import json
from typing import AsyncGenerator

async def stream_workflow_progress(workflow_type: str, topic: str, workflow_func, **kwargs) -> AsyncGenerator[str, None]:
    """
    Stream workflow execution progress as SSE events.
    
    Yields JSON events: {"type": "status", "data": {...}}
    """
    try:
        # Start event
        yield json.dumps({
            "type": "start",
            "workflow_type": workflow_type,
            "topic": topic
        }) + "\n\n"
        
        await asyncio.sleep(0.1)  # Ensure client receives start
        
        # Execute workflow with progress callbacks
        if workflow_type == "simple_reflection":
            async for event in stream_reflection_workflow(workflow_func, topic, **kwargs):
                yield event
        elif workflow_type == "tool_research":
            async for event in stream_tool_research_workflow(workflow_func, topic, **kwargs):
                yield event
        elif workflow_type == "multi_agent":
            async for event in stream_multi_agent_workflow(workflow_func, topic, **kwargs):
                yield event
        
        # Completion event
        yield json.dumps({"type": "complete"}) + "\n\n"
        
    except Exception as e:
        yield json.dumps({
            "type": "error",
            "message": str(e)
        }) + "\n\n"


async def stream_reflection_workflow(workflow, topic: str, **kwargs) -> AsyncGenerator[str, None]:
    """Stream reflection workflow: draft → reflection → revised"""
    
    # Draft step
    yield json.dumps({
        "type": "progress",
        "step": "draft",
        "message": "Generating initial draft..."
    }) + "\n\n"
    
    draft = await workflow.draft_agent.execute(topic)
    yield json.dumps({
        "type": "step_complete",
        "step": "draft",
        "data": draft
    }) + "\n\n"
    
    # Reflection step
    yield json.dumps({
        "type": "progress",
        "step": "reflection",
        "message": "Analyzing draft and generating critique..."
    }) + "\n\n"
    
    reflection = await workflow.reflection_agent.execute(draft)
    yield json.dumps({
        "type": "step_complete",
        "step": "reflection",
        "data": reflection
    }) + "\n\n"
    
    # Revision step
    yield json.dumps({
        "type": "progress",
        "step": "revision",
        "message": "Revising based on feedback..."
    }) + "\n\n"
    
    revised = await workflow.revision_agent.execute(draft, reflection)
    yield json.dumps({
        "type": "step_complete",
        "step": "revised",
        "data": revised
    }) + "\n\n"


async def stream_tool_research_workflow(workflow, topic: str, **kwargs) -> AsyncGenerator[str, None]:
    """Stream tool research workflow"""
    
    tools = kwargs.get("tools", ["arxiv", "wikipedia", "tavily"])
    
    yield json.dumps({
        "type": "progress",
        "step": "research",
        "message": f"Searching {', '.join(tools)}..."
    }) + "\n\n"
    
    result = await workflow.execute(topic, tools=tools)
    
    yield json.dumps({
        "type": "step_complete",
        "step": "research",
        "data": result
    }) + "\n\n"


async def stream_multi_agent_workflow(workflow, topic: str, **kwargs) -> AsyncGenerator[str, None]:
    """Stream multi-agent workflow with step-by-step execution"""
    
    max_steps = kwargs.get("max_steps", 4)
    
    # Planning step
    yield json.dumps({
        "type": "progress",
        "step": "planning",
        "message": "Generating execution plan..."
    }) + "\n\n"
    
    from app.agents import PlannerAgent
    planner = PlannerAgent()
    plan_steps = await planner.execute(topic)
    
    if workflow.limit_steps:
        plan_steps = plan_steps[:min(len(plan_steps), max_steps)]
    
    yield json.dumps({
        "type": "step_complete",
        "step": "plan",
        "data": plan_steps
    }) + "\n\n"
    
    # Execute each step
    history = []
    for i, step in enumerate(plan_steps, 1):
        yield json.dumps({
            "type": "progress",
            "step": f"step_{i}",
            "message": f"Step {i}/{len(plan_steps)}: {step[:60]}..."
        }) + "\n\n"
        
        decision = await workflow._decide_agent(step)
        agent_name = decision.get("agent")
        task = decision.get("task")
        
        context = workflow._build_context(history)
        enriched_task = f"You are {agent_name}.\n\nContext:\n{context}\n\nTask:\n{task}"
        
        agent = workflow.agents.get(agent_name)
        if agent:
            output = await agent.execute(enriched_task)
        else:
            output = f"⚠️ Unknown agent: {agent_name}"
        
        history.append({"step": step, "agent": agent_name, "output": output})
        
        yield json.dumps({
            "type": "step_complete",
            "step": f"step_{i}",
            "data": {"step": step, "agent": agent_name, "output": output}
        }) + "\n\n"
    
    # Final output
    final_output = history[-1]["output"] if history else "No output generated"
    yield json.dumps({
        "type": "step_complete",
        "step": "final",
        "data": {"plan": plan_steps, "history": history, "final_report": final_output}
    }) + "\n\n"
