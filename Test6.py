"""
Automated end-to-end test for Test #6 (APM demo status tracking) using Bedrock.

Ensure you have browser-use installed with `examples` extra, i.e. `uv install 'browser-use[examples]'`

@dev Ensure AWS environment variables are set correctly for Bedrock access.
"""

from browser_use.controller.service import Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use import ActionResult, Agent
from pydantic import BaseModel
import argparse
import asyncio
import os
import sys

import boto3
from botocore.config import Config
from langchain_aws import ChatBedrockConverse
from typing import Optional
from browser_use.browser.context import BrowserContext

# disable browser-use's built-in LLM API-key check
os.environ["SKIP_LLM_API_KEY_VERIFICATION"] = "True"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

controller = Controller()

@controller.action(
    'Access the graph and open the popup'
)
async def bounding_box(browser: BrowserContext):
    page = await browser.get_current_page()

    js_file_path = os.path.join(os.path.dirname(
        __file__), "JSInjections", "clickMaxGraphPoint.js")
    with open(js_file_path, 'r') as file:
        js_code = file.read()

    logs = await page.evaluate(js_code)
    return ActionResult(extracted_content=logs, include_in_memory=False)

def get_llm():
    config = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})
    bedrock_client = boto3.client(
        'bedrock-runtime', region_name='us-east-1', config=config)

    return ChatBedrockConverse(
        model_id='anthropic.claude-3-5-sonnet-20240620-v1:0',
        temperature=0.0,
        max_tokens=None,
        client=bedrock_client,
    )

task = """
        1. Navigate to https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#application-signals:services/Environment%3Deks%3Ademo%2Fdefault%26Name%3Dvisits-service-java%26Type%3DService/operations?selectedOperation=POST+%2Fowners%2F%7BownerId%7D%2Fpets%2F%7BpetId%7D%2Fvisits
        2. Access the graph and open the popup
        3. In the right panel, click the first link under "Trace ID".
        4. Wait a few seconds for the page to render. Under "visits-service-java AWS::EKS::Container", click on the row with "visits-service-java" and wait a few seconds
        5. In the right panel, click the "Exceptions" button next to the "Metadata" button.
        6. Look for the messge "The level of configured provisioned throughput for the table was exceeded.". If this is there, notify me with a checkmark and if not, notify me with an X.
        """

parser = argparse.ArgumentParser()
parser.add_argument('--query', type=str,
                    help='The query for the agent to execute', default=task)
args = parser.parse_args()

llm = get_llm()

browser = Browser(
    config=BrowserConfig(
        browser_binary_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        # headless=True,
    )
)

agent = Agent(
    task=args.query,
    llm=llm,
    controller=controller,
    browser=browser,
    validate_output=True,
)


async def main():
    history = await agent.run(max_steps=100)
    print(history.action_results())
    await browser.close()

asyncio.run(main())
