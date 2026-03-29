import asyncio
import json
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

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
        
        if workflow_type == "tool_research":
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
        
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as e:
        logger.error(f"Streaming error [{workflow_type}]: {type(e).__name__}: {e}", exc_info=True)
        yield "data: " + json.dumps({
            "type": "error",
            "message": str(e)
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
    logger.info(f"[W2] Starting research agent for: {topic[:50]}")
    research_report = await research_agent.execute(topic, tools=tools, tool_func_mapping=tool_func_mapping)
    logger.info(f"[W2] Research agent completed, len={len(research_report or '')}")
    
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
    logger.info("[W2] Starting reflection agent")
    reflection = await reflection_agent.execute(research_report)
    logger.info("[W2] Reflection agent completed")
    
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "reflection",
        "data": reflection
    }) + "\n\n"
    
    # Step 3: Revision
    yield "data: " + json.dumps({
        "type": "progress",
        "step": "revised",
        "message": "Revising based on analysis..."
    }) + "\n\n"
    
    revision_agent = RevisionAgent(model=workflow.model)
    logger.info("[W2] Starting revision agent")
    revised_report = await revision_agent.execute(research_report, reflection)
    logger.info("[W2] Revision agent completed")
    
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "revised",
        "data": revised_report
    }) + "\n\n"
    
    # Step 4: HTML conversion
    yield "data: " + json.dumps({
        "type": "progress",
        "step": "formatting",
        "message": "Formatting output..."
    }) + "\n\n"
    
    html_output = await workflow._convert_to_html(revised_report)
    
    # Final result - collect sources from tool call results, filter to relevant ones
    from app.utils import filter_relevant_sources, strip_inline_links
    raw_sources = list(research_agent.collected_sources)
    sources = filter_relevant_sources(raw_sources, revised_report or research_report)
    final_result = {
        "research_report": strip_inline_links(research_report),
        "reflection": reflection,
        "revised_report": strip_inline_links(revised_report),
        "html_output": html_output,
        "sources": sources[:10]
    }
    
    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "formatting",
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
        if agent_name == "research_agent" and agent:
            from app.tools.arxiv_tool import arxiv_tool_def, arxiv_search_tool
            from app.tools.tavily_tool import tavily_tool_def, tavily_search_tool
            from app.tools.wikipedia_tool import wikipedia_tool_def, wikipedia_search_tool
            output = await agent.execute(
                enriched_task,
                tools=[arxiv_tool_def, tavily_tool_def, wikipedia_tool_def],
                tool_func_mapping={
                    "arxiv_search_tool": arxiv_search_tool,
                    "tavily_search_tool": tavily_search_tool,
                    "wikipedia_search_tool": wikipedia_search_tool,
                }
            )
        elif agent:
            output = await agent.execute(enriched_task)
        else:
            output = f"Unknown agent: {agent_name}"
        
        history.append({"step": step, "agent": agent_name, "output": output})
        
        yield "data: " + json.dumps({
            "type": "step_complete",
            "step": f"step_{i}",
            "data": {"step": step, "agent": agent_name, "output": output}
        }) + "\n\n"
    
    # Final synthesis - WriterAgent produces polished report (mirrors MultiAgentWorkflow.execute)
    yield "data: " + json.dumps({
        "type": "progress",
        "step": f"step_{len(plan_steps) + 1}",
        "message": "Synthesizing final report..."
    }) + "\n\n"

    synthesis_task = f"""You are the WriterAgent responsible for producing the final polished report.

Based on all the work done by the team below, produce a comprehensive, well-structured final report on the topic: "{topic}"

Team work history:
{workflow._build_context(history)}

**Your task:**
- Synthesize all research findings into a coherent narrative
- Incorporate editorial feedback and improvements suggested by the editor
- Structure the content with clear sections and flow
- Include all relevant citations and sources
- Produce publication-ready content in the SAME LANGUAGE as the original topic

**IMPORTANT:** Return ONLY the final polished report text, NOT meta-commentary or explanations about what you did."""

    final_report = await workflow.agents["writer_agent"].execute(synthesis_task)

    # Collect and filter sources (extract from raw report before stripping)
    import re as _re
    from app.utils import filter_relevant_sources, strip_inline_links
    sources = list(workflow.agents["research_agent"].collected_sources)
    seen_urls = {s["url"] for s in sources}
    for title, url in _re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', final_report):
        if url.startswith('http') and url not in seen_urls:
            sources.append({"title": title, "url": url})
            seen_urls.add(url)
    sources = filter_relevant_sources(sources, final_report)
    final_report = strip_inline_links(final_report)

    yield "data: " + json.dumps({
        "type": "step_complete",
        "step": "final",
        "data": {"plan": plan_steps, "history": history, "final_report": final_report, "sources": sources[:10]}
    }) + "\n\n"
