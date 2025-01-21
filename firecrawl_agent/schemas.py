from pydantic import BaseModel
from typing import Dict, Optional, Union

class InputSchema(BaseModel):
    tool_name: str
    tool_input_data: str
    query: Optional[str] = None

class SystemPromptSchema(BaseModel):
    """Schema for system prompts."""
    role: str = "You are a web scraping assistant that helps users extract information from websites."
    persona: Optional[Union[Dict, BaseModel]] = None