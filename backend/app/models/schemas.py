from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class WorkflowRequest(BaseModel):
    """Base request for workflow execution"""
    topic: str = Field(..., min_length=1, max_length=500, description="Research topic or prompt")
    model: Optional[str] = Field(None, description="Override default model")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature for generation")
    
    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Strip whitespace and validate topic is not empty"""
        v = v.strip()
        if not v:
            raise ValueError("Topic cannot be empty or only whitespace")
        return v


class ReflectionWorkflowRequest(WorkflowRequest):
    """Request for simple reflection workflow (Q2)"""
    draft_model: Optional[str] = Field(None, description="Model for drafting")
    reflection_model: Optional[str] = Field(None, description="Model for reflection")
    revision_model: Optional[str] = Field(None, description="Model for revision")


class ToolResearchWorkflowRequest(WorkflowRequest):
    """Request for tool-enhanced research workflow (Q3)"""
    tools: Optional[List[Literal["arxiv", "tavily", "wikipedia"]]] = Field(
        default=["arxiv", "tavily", "wikipedia"],
        description="Tools to enable"
    )
    max_results: Optional[int] = Field(5, ge=1, le=10, description="Max results per tool")
    export_format: Optional[Literal["html", "markdown", "json"]] = Field("html", description="Export format")


class MultiAgentWorkflowRequest(WorkflowRequest):
    """Request for multi-agent workflow (Q5)"""
    max_steps: Optional[int] = Field(4, ge=1, le=10, description="Maximum workflow steps")
    limit_steps: Optional[bool] = Field(True, description="Limit to max_steps")
    enable_planning: Optional[bool] = Field(True, description="Enable planning agent")


class WorkflowResponse(BaseModel):
    """Base response from workflow execution"""
    workflow_id: str = Field(..., description="Unique workflow execution ID")
    workflow_type: str = Field(..., description="Type of workflow executed")
    topic: str = Field(..., description="Original research topic")
    status: Literal["completed", "failed", "partial"] = Field(..., description="Execution status")
    created_at: datetime = Field(default_factory=datetime.now)
    execution_time: float = Field(..., description="Execution time in seconds")
    result: Dict[str, Any] = Field(..., description="Workflow results")
    error: Optional[str] = Field(None, description="Error message if failed")


class ReflectionWorkflowResponse(WorkflowResponse):
    """Response from reflection workflow"""
    draft: str
    reflection: str
    revised: str


class ToolResearchWorkflowResponse(WorkflowResponse):
    """Response from tool-enhanced research workflow"""
    research_report: str
    reflection: Optional[str] = None
    revised_report: Optional[str] = None
    html_output: Optional[str] = None
    sources: List[Dict[str, str]] = Field(default_factory=list)


class MultiAgentWorkflowResponse(WorkflowResponse):
    """Response from multi-agent workflow"""
    plan: List[str]
    execution_history: List[Dict[str, Any]]
    final_report: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tools_available: Dict[str, bool]
    models_configured: Dict[str, str]
