from app.agents import PlannerAgent, ResearchAgent, WriterAgent, EditorAgent
from app.core.config import settings
from openai import OpenAI
import json
import re
import logging

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """Multi-agent orchestration workflow (Q5): Plan → Research → Write → Edit"""
    
    def __init__(
        self,
        model: str = None,
        max_steps: int = 4,
        limit_steps: bool = True
    ):
        self.model = model or settings.DEFAULT_RESEARCH_MODEL
        self.max_steps = max_steps
        self.limit_steps = limit_steps
        self.client = OpenAI()
        
        # Agent registry
        self.agents = {
            "research_agent": ResearchAgent(model=self.model),
            "writer_agent": WriterAgent(model=self.model),
            "editor_agent": EditorAgent(model=self.model)
        }
    
    async def execute(self, topic: str) -> dict:
        """Execute the multi-agent workflow"""
        
        logger.info(f"Starting multi-agent workflow for: {topic}")
        
        # Step 1: Planning
        planner = PlannerAgent()
        logger.info("Step 1: Creating plan...")
        plan_steps = await planner.execute(topic)
        
        # Limit steps if configured
        if self.limit_steps:
            plan_steps = plan_steps[:min(len(plan_steps), self.max_steps)]
        
        logger.info(f"Plan created with {len(plan_steps)} steps")
        
        # Step 2: Execute plan
        history = []
        
        for i, step in enumerate(plan_steps):
            logger.info(f"Executing step {i+1}/{len(plan_steps)}: {step}")
            
            # Decide which agent to use
            agent_decision = await self._decide_agent(step)
            agent_name = agent_decision["agent"]
            task = agent_decision["task"]
            
            # Build context from previous steps
            context = self._build_context(history)
            enriched_task = f"""You are {agent_name}.

Here is the context of what has been done so far:
{context}

Your next task is:
{task}
"""
            
            # Execute with selected agent
            if agent_name in self.agents:
                output = await self.agents[agent_name].execute(enriched_task)
            else:
                output = f"⚠️ Unknown agent: {agent_name}"
            
            history.append({
                "step": step,
                "agent": agent_name,
                "output": output
            })
        
        # Step 3: Final synthesis - Let WriterAgent produce polished final version
        logger.info("Final step: Synthesizing final report from all agent outputs...")
        
        synthesis_task = f"""You are the WriterAgent responsible for producing the final polished report.

Based on all the work done by the team below, produce a comprehensive, well-structured final report on the topic: "{topic}"

Team work history:
{self._build_context(history)}

**Your task:**
- Synthesize all research findings into a coherent narrative
- Incorporate editorial feedback and improvements suggested by the editor
- Structure the content with clear sections and flow
- Include all relevant citations and sources
- Produce publication-ready content in the SAME LANGUAGE as the original topic

**IMPORTANT:** Return ONLY the final polished report text, NOT meta-commentary or explanations about what you did."""

        final_report = await self.agents["writer_agent"].execute(synthesis_task)
        
        # Add synthesis step to history
        history.append({
            "step": "Final synthesis and polishing",
            "agent": "writer_agent",
            "output": final_report
        })
        
        # Extract sources ONLY from final output (retained info only)
        import re
        sources = []
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', final_report)
        for title, url in links:
            if url.startswith('http'):
                sources.append({"title": title, "url": url})
        
        logger.info("Multi-agent workflow completed")
        
        return {
            "plan": plan_steps,
            "history": history,
            "final_report": final_report,
            "sources": sources[:10]  # Limit to 10 sources cited in final output
        }
    
    async def _decide_agent(self, step: str) -> dict:
        """Decide which agent should handle a step"""
        
        agent_decision_prompt = f"""
You are an execution manager for a multi-agent research team.

Given the following instruction, identify which agent should perform it and extract the clean task.

Return only a valid JSON object with two keys:
- "agent": one of ["research_agent", "editor_agent", "writer_agent"]
- "task": a string with the instruction that the agent should follow

Only respond with a valid JSON object. Do not include explanations or markdown formatting.

Instruction: "{step}"
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": agent_decision_prompt}],
                temperature=0,
            )
            
            raw_content = response.choices[0].message.content
            cleaned_json = self._clean_json_block(raw_content)
            agent_info = json.loads(cleaned_json)
            
            return agent_info
            
        except Exception as e:
            logger.error(f"Agent decision error: {e}")
            return {"agent": "writer_agent", "task": step}
    
    def _build_context(self, history: list) -> str:
        """Build context from execution history"""
        
        if not history:
            return "No previous steps."
        
        context_parts = []
        for i, item in enumerate(history):
            context_parts.append(
                f"Step {i+1} executed by {item['agent']}:\n{item['output'][:300]}..."
            )
        
        return "\n\n".join(context_parts)
    
    def _clean_json_block(self, raw: str) -> str:
        """Clean JSON blocks that may be wrapped in markdown"""
        
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
        return raw.strip()
