from app.agents import ResearchAgent, EditorAgent
from app.tools import arxiv_search_tool, tavily_search_tool, wikipedia_search_tool
from app.core.config import settings
from openai import OpenAI
import json
import logging

logger = logging.getLogger(__name__)


class ToolResearchWorkflow:
    """Tool-enhanced research workflow (Q3): Search → Reflect → Export"""
    
    def __init__(
        self,
        model: str = None,
        tools: list = None,
        max_results: int = 5
    ):
        self.model = model or settings.DEFAULT_RESEARCH_MODEL
        self.max_results = max_results
        self.client = OpenAI()
        
        # Map tool names to functions
        self.tool_mapping = {
            "arxiv": arxiv_search_tool,
            "tavily": tavily_search_tool,
            "wikipedia": wikipedia_search_tool
        }
        
        # Select tools
        if tools:
            self.tools = [self.tool_mapping[t] for t in tools if t in self.tool_mapping]
        else:
            self.tools = list(self.tool_mapping.values())
    
    async def execute(self, topic: str, export_format: str = "html") -> dict:
        """Execute the tool research workflow"""
        
        logger.info(f"Starting tool research workflow for: {topic}")
        
        # Step 1: Research with tools
        research_agent = ResearchAgent(model=self.model)
        logger.info("Step 1: Conducting research with tools...")
        research_report = await research_agent.execute(topic, tools=self.tools)
        
        # Step 2: Reflection and rewrite
        logger.info("Step 2: Reflecting on research...")
        reflection_result = await self._reflect_and_rewrite(research_report)
        
        # Step 3: Convert to desired format
        logger.info(f"Step 3: Converting to {export_format}...")
        if export_format == "html":
            html_output = await self._convert_to_html(
                reflection_result.get("revised_report", research_report)
            )
        else:
            html_output = None
        
        logger.info("Tool research workflow completed")
        
        return {
            "research_report": research_report,
            "reflection": reflection_result.get("reflection"),
            "revised_report": reflection_result.get("revised_report"),
            "html_output": html_output,
            "sources": []  # TODO: Extract from research
        }
    
    async def _reflect_and_rewrite(self, report: str) -> dict:
        """Reflect on and rewrite the report"""
        
        user_prompt = f"""Analyze and improve the following research report.

Report:
{report}

Provide your response as valid JSON with exactly two keys:
1. "reflection": A structured analysis covering strengths, limitations, suggestions, and opportunities for improvement
2. "revised_report": An improved version incorporating the reflection feedback, with enhanced clarity and academic tone

Output ONLY valid JSON in this exact format with no additional text:
{{"reflection": "your reflection here", "revised_report": "your revised report here"}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an academic reviewer and editor."},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            llm_output = response.choices[0].message.content.strip()
            data = json.loads(llm_output)
            
            return {
                "reflection": str(data.get("reflection", "")).strip(),
                "revised_report": str(data.get("revised_report", "")).strip()
            }
        except Exception as e:
            logger.error(f"Reflection error: {e}")
            return {"reflection": None, "revised_report": report}
    
    async def _convert_to_html(self, report: str) -> str:
        """Convert report to HTML"""
        
        user_prompt = f"""Convert the following research report into a well-structured HTML document.

Report:
{report}

Requirements:
- Return ONLY valid, clean HTML (no markdown, no code blocks, no additional commentary)
- Use semantic HTML5 tags (<header>, <main>, <section>, <article>, etc.)
- Include appropriate section headers (<h1>, <h2>, <h3>)
- Format paragraphs with <p> tags
- Make all URLs clickable with <a href="..."> tags
- Preserve all citations in their original format
- Add minimal inline CSS for readability (font-family, line-height, margins)
- Use a professional academic style

Output the complete HTML document starting with <!DOCTYPE html>."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You convert plaintext reports into full clean HTML documents."},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"HTML conversion error: {e}")
            return f"<html><body><pre>{report}</pre></body></html>"
