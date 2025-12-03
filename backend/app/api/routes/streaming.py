import asyncio
import json
from typing import AsyncGenerator

async def stream_workflow_progress(workflow_type: str, topic: str, workflow_func, cache_service, **kwargs) -> AsyncGenerator[str, None]:
    """
    Stream workflow execution progress as SSE events with cache awareness.
    
    Yields JSON events: {"type": "status", "data": {...}}
    """
    try:
        # Start event
        yield "data: " + json.dumps({
            "type": "start",
            "workflow_type": workflow_type,
            "topic": topic
        }) + "\n\n"
        
        await asyncio.sleep(0.1)  # Ensure client receives start
        
        # Check cache first
        cached_result = cache_service.get_cached_result(topic, workflow_type.replace("-", "_"))
        if cached_result:
            # Cache hit - send full result immediately
            yield "data: " + json.dumps({
                "type": "cache_hit",
                "data": cached_result
            }) + "\n\n"
            
            yield "data: " + json.dumps({"type": "complete"}) + "\n\n"
            return
        
        # Cache miss - stream workflow execution
        result_data = {}
        
        if workflow_type == "simple_reflection":
            async for event in stream_reflection_workflow(workflow_func, topic, **kwargs):
                yield event
                # Capture step data for caching
                try:
                    event_str = event.strip()
                    if event_str.startswith("data: "):
                        event_str = event_str[6:]  # Remove "data: " prefix
                    event_data = json.loads(event_str)
                    if event_data.get("type") == "step_complete":
                        result_data[event_data["step"]] = event_data["data"]
                except (json.JSONDecodeError, KeyError):
                    pass  # Skip malformed events
        elif workflow_type == "tool_research":
            async for event in stream_tool_research_workflow(workflow_func, topic, **kwargs):
                yield event
                try:
                    event_str = event.strip()
                    if event_str.startswith("data: "):
                        event_str = event_str[6:]
                    event_data = json.loads(event_str)
                    if event_data.get("type") == "step_complete":
                        result_data = event_data["data"]
                except (json.JSONDecodeError, KeyError):
                    pass
        elif workflow_type == "multi_agent":
            async for event in stream_multi_agent_workflow(workflow_func, topic, **kwargs):
                yield event
                try:
                    event_str = event.strip()
                    if event_str.startswith("data: "):
                        event_str = event_str[6:]
                    event_data = json.loads(event_str)
                    if event_data.get("type") == "step_complete":
                        step = event_data["step"]
                        if step == "plan":
                            result_data["plan"] = event_data["data"]
                        elif step == "final":
                            result_data = event_data["data"]
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Store in cache after streaming completes
        if result_data:
            cache_service.store_result(topic, workflow_type.replace("-", "_"), result_data)
        
        # Completion event
        yield "data: " + json.dumps({"type": "complete"}) + "\n\n"
        
    except Exception as e:
        yield "data: " + json.dumps({
            "type": "error",
            "message": str(e)
        }) + "\n\n"


async def stream_reflection_workflow(workflow, topic: str, **kwargs) -> AsyncGenerator[str, None]:
    """Stream reflection workflow: draft → reflection → revised"""
    
    # Draft step
    yield "data: " + json.dumps({
        "type": "progress",
        "step": "draft",
        "message": "Generating initial draft..."
    }) + "\n\n"
    
    draft = await workflow.draft_agent.execute(topic)
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "draft",
        "data": draft
    }) + "\n\n"
    
    # Reflection step
    yield "data: " + json.dumps({
        "type": "progress",
        "step": "reflection",
        "message": "Analyzing draft and generating critique..."
    }) + "\n\n"
    
    reflection = await workflow.reflection_agent.execute(draft)
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "reflection",
        "data": reflection
    }) + "\n\n"
    
    # Revision step
    yield "data: " + json.dumps({
        "type": "progress",
        "step": "revision",
        "message": "Revising based on feedback..."
    }) + "\n\n"
    
    revised = await workflow.revision_agent.execute(draft, reflection)
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "revised",
        "data": revised
    }) + "\n\n"


async def stream_tool_research_workflow(workflow, topic: str, **kwargs) -> AsyncGenerator[str, None]:
    """Stream tool research workflow with detailed progress including tool execution"""
    
    from app.agents import ResearchAgent, ReflectionAgent, RevisionAgent
    from app.tools.arxiv_tool import arxiv_tool_def, arxiv_search_tool
    from app.tools.tavily_tool import tavily_tool_def, tavily_search_tool
    from app.tools.wikipedia_tool import wikipedia_tool_def, wikipedia_search_tool
    
    # Setup tools
    tools = [arxiv_tool_def, tavily_tool_def, wikipedia_tool_def]
    tool_func_mapping = {
        "arxiv_search_tool": arxiv_search_tool,
        "tavily_search_tool": tavily_search_tool,
        "wikipedia_search_tool": wikipedia_search_tool
    }
    
    # Step 1: Research with real tools
    yield "data: " + json.dumps({
        "type": "progress",
        "step": "research",
        "message": "Conducting research with arXiv, Tavily, and Wikipedia..."
    }) + "\n\n"
    
    research_agent = ResearchAgent(model=workflow.model)
    # Pass tools and function mapping for full research capability
    research_report = await research_agent.execute(topic, tools=tools, tool_func_mapping=tool_func_mapping)
    
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "research",
        "data": research_report
    }) + "\n\n"
    
    # Step 2: Reflection
    yield "data: " + json.dumps({
        "type": "progress",
        "step": "reflection",
        "message": "Analyzing research quality..."
    }) + "\n\n"
    
    reflection_agent = ReflectionAgent(model=workflow.model)
    reflection = await reflection_agent.execute(research_report)
    
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "reflection",
        "data": reflection
    }) + "\n\n"
    
    # Step 3: Revision
    yield "data: " + json.dumps({
        "type": "progress",
        "step": "revision",
        "message": "Revising based on analysis..."
    }) + "\n\n"
    
    revision_agent = RevisionAgent(model=workflow.model)
    revised_report = await revision_agent.execute(research_report, reflection)
    
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "revision",
        "data": revised_report
    }) + "\n\n"
    
    # Step 4: HTML conversion
    yield "data: " + json.dumps({
        "type": "progress",
        "step": "formatting",
        "message": "Formatting output..."
    }) + "\n\n"
    
    html_output = await workflow._convert_to_html(revised_report)
    
    # Final result
    final_result = {
        "research_report": research_report,
        "reflection": reflection,
        "revised_report": revised_report,
        "html_output": html_output,
        "sources": []
    }
    
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "final",
        "data": final_result
    }) + "\n\n"


async def stream_multi_agent_workflow(workflow, topic: str, **kwargs) -> AsyncGenerator[str, None]:
    """Stream multi-agent workflow with step-by-step execution"""
    
    max_steps = kwargs.get("max_steps", 4)
    
    # Planning step - silently execute (plan already shown in frontend)
    from app.agents import PlannerAgent
    planner = PlannerAgent()
    plan_steps = await planner.execute(topic)
    
    if workflow.limit_steps:
        plan_steps = plan_steps[:min(len(plan_steps), max_steps)]
    
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "plan",
        "data": plan_steps
    }) + "\n\n"
    
    # Execute each step
    history = []
    for i, step in enumerate(plan_steps, 1):
        yield "data: " + json.dumps({
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
        
        yield "data: " + json.dumps({
            "type": "step_complete",
            "step": f"step_{i}",
            "data": {"step": step, "agent": agent_name, "output": output}
        }) + "\n\n"
    
    # Final output
    final_output = history[-1]["output"] if history else "No output generated"
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "final",
        "data": {"plan": plan_steps, "history": history, "final_report": final_output}
    }) + "\n\n"
