#!/usr/bin/env python
import asyncio
import logging
from dotenv import load_dotenv
from typing import Dict
from naptha_sdk.schemas import AgentDeployment, AgentRunInput, ToolRunInput
from naptha_sdk.modules.tool import Tool
from naptha_sdk.user import sign_consumer_id

from firecrawl_agent.schemas import InputSchema, SystemPromptSchema

load_dotenv()
logger = logging.getLogger(__name__)

class FirecrawlAgent:
    def __init__(self, deployment: AgentDeployment):
        self.deployment = deployment
        self.tool = Tool(tool_deployment=self.deployment.tool_deployments[0])
        self.system_prompt = SystemPromptSchema(role=self.deployment.config.system_prompt["role"])

    async def call_tool(self, module_run: AgentRunInput):
        tool_run_input = ToolRunInput(
            consumer_id=module_run.consumer_id,
            inputs=module_run.inputs,
            deployment=self.deployment.tool_deployments[0],
            signature=sign_consumer_id(module_run.consumer_id, os.getenv("PRIVATE_KEY"))
        )
        tool_response = await self.tool.call_tool_func(tool_run_input)
        return tool_response

async def run(module_run: Dict, *args, **kwargs):
    module_run = AgentRunInput(**module_run)
    module_run.inputs = InputSchema(**module_run.inputs)
    firecrawl_agent = FirecrawlAgent(module_run.deployment)
    tool_response = await firecrawl_agent.call_tool(module_run)
    return tool_response

if __name__ == "__main__":
    import os
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import setup_module_deployment

    naptha = Naptha()

    # Configs
    deployment = asyncio.run(setup_module_deployment(
        "agent", 
        "firecrawl_agent/configs/deployment.json", 
        node_url=os.getenv("NODE_URL"), 
        user_id=naptha.user.id
    ))

    # Example: Scraping a website
    input_params = {
        "tool_name": "scrape_website",
        "tool_input_data": "https://docs.firecrawl.dev"
    }

    # Example: Extracting specific data
    # input_params = {
    #     "tool_name": "extract_data",
    #     "tool_input_data": "https://docs.firecrawl.dev",
    #     "query": "Extract the API rate limits"
    # }

    module_run = {
        "inputs": input_params,
        "deployment": deployment,
        "consumer_id": naptha.user.id,
        "signature": sign_consumer_id(naptha.user.id, os.getenv("PRIVATE_KEY"))
    }

    response = asyncio.run(run(module_run))
    print("Response: ", response)