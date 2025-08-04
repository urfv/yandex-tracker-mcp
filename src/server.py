import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from yandex_tracker_client import TrackerClient
from yandex_tracker_client.exceptions import NotFound
from typing import Optional, List, Dict, Any, Union, Literal
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
async def get_project(project_id: str) -> dict:
    """Get project details from Yandex Tracker.
    
    Args:
        project_id: Project ID to retrieve
    """
    try:
        project = client.projects.get(project_id)
        return {
            "id": project.id,
            "version": project.version,
            "key": project.key,
            "name": project.name,
            "description": getattr(project, 'description', None),
            "lead": convert_reference(project.lead),
            "status": getattr(project, 'status', None),
            "startDate": getattr(project, 'startDate', None),
            "endDate": getattr(project, 'endDate', None)
        }
    except NotFound:
        return {"error": f"Project {project_id} not found"}
    except Exception as e:
        return {"error": f"Failed to get project: {str(e)}"}

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
    """Count issues in Yandex Tracker matching the query.
    
    Args:
        query: Query string in Yandex Tracker query language
    """
    try:
        # Make a POST request to the count endpoint
        response = client._connection.post(
            path='/v3/issues/_count',
            data={'query': query}
        )
        return {"count": response}
    except Exception as e:
        return {"error": f"Failed to count issues: {str(e)}"}

@mcp.tool()
async def search_issues(
    query: str,
    per_page: Optional[int] = 50,
    page: Optional[int] = 1
) -> dict:
    """
    Search for issues using Yandex Tracker query language.

    Query language rules:
    - You can search by any field, e.g.:
        Project, Queue, Status, Assignee, Reporter, Priority, Type, Summary, Description, Created, Updated, Resolved, Component, Version, Sprint, Epic, Parent, Child, Key, Comment, Comment Author, Boards, Tags, Story Points, Time Spent, History, Modifier, Resolver, Component Owner, Queue Owner, Related, Related To Queue, Relates, Linked to, Is Subtask For, Is Parent Task For, Is Epic Of, Is Dependent By, Is Duplicated By, Clone, Clones Of Queue, Block Queue, Old Queue, Subtasks For Queue, In Epics Of Queue, Sprint In Progress By Board, Sprints By Board, Start Date, Last Comment, etc.
    - Use logical operators: AND, OR, NOT
    - Use comparison operators: =, !=, >, <, >=, <=, ~ (contains), !~ (does not contain), IN, NOT IN, IS EMPTY, IS NOT EMPTY
    - For text fields, use ~ for substring match, # for exact match, ! for negation
    - Date fields support comparison (>, <, >=, <=)
    - You can group conditions with parentheses

    Examples:
        Queue: TEST AND Status: Open
        Project: "Perpetuum mobile"
        Assignee: user123 OR Reporter: user456
        Priority: High AND Type: Bug
        Created: > 2024-01-01
        Summary: ~ "ошибка"
        Description: #"Избранное"
        Comment: "отличная работа"
        Key: "TASK-123", "TASK-321"
        (Queue: TEST OR Queue: PROD) AND Status: Open
        Comment Author: "Иван Иванов"
        Last Comment: < now()-1h
        Is Subtask For: "TASK-123"
        Linked to: "TASK-321"
        Boards: "My Board"
        Tags: "Поддержка", "wiki"
        Story Points: >=5
        Time Spent: >"5d 2h 30m"
        History: "проще простого"
        Modifier: user3370@
        Resolver: "Иван Иванов"
        Component Owner: user3370@
        Queue Owner: "Иван Иванов"
        Related: user3370@, "Иван Иванов"
        Related To Queue: Тестирование
        Relates: "TASK-123", "TASK-321"
        Is Parent Task For: "TASK-123"
        Is Epic Of: "TASK-123"
        Is Dependent By: "TASK-123"
        Is Duplicated By: "TASK-123"
        Clone: "TASK-123", "TASK-321"
        Clones Of Queue: TEST, DEVELOP
        Block Queue: TEST
        Old Queue: TEST
        Subtasks For Queue: TEST
        In Epics Of Queue: Тестирование
        Sprint In Progress By Board: 87
        Sprints By Board: 87
        Start Date: <2017-01-30

    See full documentation: https://yandex.ru/support/tracker/ru/user/query-filter#filter-parameters

    Args:
        query: Search query in Yandex Tracker query language
        per_page: Number of issues per page (default: 50)
        page: Page number (default: 1)
    Returns:
        Dictionary with 'issues' list and 'total' count
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

@mcp.tool()
async def get_boards() -> dict:
    """Get all boards from Yandex Tracker.
    
    Returns a list of all boards available in the organization.
    """
    try:
        # Make a GET request to get all boards
        response = client._connection.get(path='/v3/boards')
        return {
            "boards": response,
            "total": len(response) if response else 0
        }
    except Exception as e:
        return {"error": f"Failed to get boards: {str(e)}"}

@mcp.tool()
async def get_board(board_id: str) -> dict:
    """Get a specific board from Yandex Tracker.
    
    Args:
        board_id: Board ID to retrieve
    """
    try:
        # Make a GET request to get a specific board
        response = client._connection.get(path=f'/v3/boards/{board_id}')
        return response
    except Exception as e:
        return {"error": f"Failed to get board: {str(e)}"}

@mcp.tool()
async def get_issue_comments(issue_id: str) -> dict:
    """Get all comments for a given issue in Yandex Tracker.
    
    Args:
        issue_id: Issue key to retrieve comments for
    """
    try:
        # Make a GET request to the comments endpoint
        response = client._connection.get(
            path=f'/v2/issues/{issue_id}/comments',
            params={'expand': 'all'}
        )
        
        # Process the PaginatedList response
        comments_data = []
        if response:
            # Convert PaginatedList to list
            comments_list = list(response)
            
            for comment in comments_list:
                # Extract data more safely
                author_info = comment.get('createdBy', {}) if hasattr(comment, 'get') else getattr(comment, 'createdBy', {})
                author_display = author_info.get('display', 'Unknown') if isinstance(author_info, dict) else str(author_info)
                
                # Handle both dict-like and object-like access
                if hasattr(comment, 'get'):
                    comment_data = {
                        "id": comment.get('id'),
                        "text": comment.get('text', ''),
                        "author": author_display,
                        "created_at": comment.get('createdAt'),
                        "updated_at": comment.get('updatedAt'),
                        "version": comment.get('version')
                    }
                else:
                    comment_data = {
                        "id": getattr(comment, 'id', None),
                        "text": getattr(comment, 'text', ''),
                        "author": author_display,
                        "created_at": getattr(comment, 'createdAt', None),
                        "updated_at": getattr(comment, 'updatedAt', None),
                        "version": getattr(comment, 'version', None)
                    }
                
                comments_data.append(comment_data)
        
        return {
            "issue_id": issue_id,
            "comments": comments_data,
            "total": len(comments_data)
        }
    except NotFound:
        return {"error": f"Issue {issue_id} not found"}
    except Exception as e:
        return {"error": f"Failed to get comments: {str(e)}"}

if __name__ == "__main__":
    mcp.run() 