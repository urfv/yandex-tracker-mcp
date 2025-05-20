import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from yandex_tracker_client import TrackerClient
from yandex_tracker_client.exceptions import NotFound

# Load environment variables
load_dotenv()

# Initialize Yandex Tracker client
client = TrackerClient(
    token=os.getenv("YANDEX_TRACKER_TOKEN"),
    org_id=os.getenv("YANDEX_TRACKER_ORG_ID")
)

# Initialize FastMCP server
mcp = FastMCP("yandex-tracker")

@mcp.tool()
async def get_issue(issue_id: str) -> dict:
    """Get issue details from Yandex Tracker by issue key.
    
    Args:
        issue_id: Issue key to retrieve details for
    """
    try:
        issue = client.issues[issue_id]
        return {
            "key": issue.key,
            "summary": issue.summary,
            "description": issue.description,
            "status": issue.status,
            "assignee": issue.assignee,
            "created_at": issue.createdAt,
            "updated_at": issue.updatedAt,
            "priority": issue.priority,
            "type": issue.type,
            "queue": issue.queue.key
        }
    except NotFound:
        return {"error": f"Issue {issue_id} not found"}
    except Exception as e:
        return {"error": f"Failed to get issue: {str(e)}"}

if __name__ == "__main__":
    mcp.run() 