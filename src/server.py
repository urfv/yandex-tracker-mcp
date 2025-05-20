import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from yandex_tracker_client import TrackerClient
from yandex_tracker_client.exceptions import NotFound
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Yandex Tracker client
client = TrackerClient(
    token=os.getenv("YANDEX_TRACKER_TOKEN"),
    org_id=os.getenv("YANDEX_TRACKER_ORG_ID")
)

# Initialize FastMCP server
mcp = FastMCP("yandex-tracker")

def convert_reference(ref: Any) -> Union[str, Dict[str, Any], None]:
    """Convert Yandex Tracker reference objects to readable format.
    
    Args:
        ref: Reference object from Yandex Tracker
        
    Returns:
        Converted reference in readable format
    """
    if ref is None:
        return None
    
    # Handle string and basic types
    if isinstance(ref, (str, int, float, bool)):
        return ref
    
    # Handle datetime
    if isinstance(ref, datetime):
        return ref.isoformat()
    
    # Handle reference objects
    try:
        if hasattr(ref, 'display'):
            return {
                'id': getattr(ref, 'id', None),
                'key': getattr(ref, 'key', None),
                'display': ref.display
            }
        return str(ref)
    except:
        return str(ref)

def format_issue(issue: Any) -> Dict[str, Any]:
    """Format issue object to readable dictionary.
    
    Args:
        issue: Issue object from Yandex Tracker
        
    Returns:
        Formatted issue dictionary
    """
    return {
        "key": issue.key,
        "summary": issue.summary,
        "description": issue.description,
        "status": convert_reference(issue.status),
        "assignee": convert_reference(issue.assignee),
        "created_at": convert_reference(issue.createdAt),
        "updated_at": convert_reference(issue.updatedAt),
        "priority": convert_reference(issue.priority),
        "type": convert_reference(issue.type),
        "queue": convert_reference(issue.queue)
    }

@mcp.tool()
async def get_issue(issue_id: str) -> dict:
    """Get issue details from Yandex Tracker by issue key.
    
    Args:
        issue_id: Issue key to retrieve details for
    """
    try:
        issue = client.issues[issue_id]
        return format_issue(issue)
    except NotFound:
        return {"error": f"Issue {issue_id} not found"}
    except Exception as e:
        return {"error": f"Failed to get issue: {str(e)}"}

@mcp.tool()
async def create_issue(
    queue: str,
    summary: str,
    description: Optional[str] = None,
    type: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None
) -> dict:
    """Create a new issue in Yandex Tracker.
    
    Args:
        queue: Queue key where the issue will be created
        summary: Issue summary/title
        description: Optional issue description
        type: Optional issue type (e.g., 'task', 'bug')
        priority: Optional priority (e.g., 'normal', 'high')
        assignee: Optional assignee ID
    """
    try:
        issue = client.issues.create(
            queue=queue,
            summary=summary,
            description=description,
            type=type,
            priority=priority,
            assignee=assignee
        )
        return format_issue(issue)
    except Exception as e:
        return {"error": f"Failed to create issue: {str(e)}"}

@mcp.tool()
async def edit_issue(
    issue_id: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    type: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None
) -> dict:
    """Edit an existing issue in Yandex Tracker.
    
    Args:
        issue_id: Issue key to edit
        summary: Optional new summary
        description: Optional new description
        type: Optional new type
        priority: Optional new priority
        assignee: Optional new assignee
    """
    try:
        issue = client.issues[issue_id]
        if summary:
            issue.summary = summary
        if description:
            issue.description = description
        if type:
            issue.type = type
        if priority:
            issue.priority = priority
        if assignee:
            issue.assignee = assignee
        issue.save()
        return format_issue(issue)
    except NotFound:
        return {"error": f"Issue {issue_id} not found"}
    except Exception as e:
        return {"error": f"Failed to edit issue: {str(e)}"}

@mcp.tool()
async def move_issue(issue_id: str, queue: str) -> dict:
    """Move an issue to a different queue.
    
    Args:
        issue_id: Issue key to move
        queue: Target queue key
    """
    try:
        issue = client.issues[issue_id]
        issue.move(queue)
        return format_issue(issue)
    except NotFound:
        return {"error": f"Issue {issue_id} not found"}
    except Exception as e:
        return {"error": f"Failed to move issue: {str(e)}"}

@mcp.tool()
async def count_issues(query: str) -> dict:
    """Count issues matching the specified query.
    
    Args:
        query: Search query in Yandex Tracker query language
    """
    try:
        count = client.issues.count(query)
        return {"count": count}
    except Exception as e:
        return {"error": f"Failed to count issues: {str(e)}"}

@mcp.tool()
async def search_issues(
    query: str,
    per_page: Optional[int] = 50,
    page: Optional[int] = 1
) -> dict:
    """Search for issues using Yandex Tracker query language.
    
    Args:
        query: Search query in Yandex Tracker query language
        per_page: Number of issues per page (default: 50)
        page: Page number (default: 1)
    """
    try:
        issues = client.issues.find(query, per_page=per_page, page=page)
        return {
            "issues": [format_issue(issue) for issue in issues],
            "total": len(issues)
        }
    except Exception as e:
        return {"error": f"Failed to search issues: {str(e)}"}

@mcp.tool()
async def link_issues(source_issue: str, target_issue: str, link_type: str) -> dict:
    """Link two issues together.
    
    Args:
        source_issue: Source issue key
        target_issue: Target issue key
        link_type: Type of link (e.g., 'relates', 'blocks', 'depends')
    """
    try:
        source = client.issues[source_issue]
        target = client.issues[target_issue]
        source.link(target, link_type)
        return {
            "source": format_issue(source),
            "target": format_issue(target),
            "link_type": link_type
        }
    except NotFound as e:
        return {"error": f"Issue not found: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to link issues: {str(e)}"}

if __name__ == "__main__":
    mcp.run() 