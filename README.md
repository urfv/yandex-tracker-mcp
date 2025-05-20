# Yandex Tracker MCP Server

A simple MCP server for interacting with Yandex Tracker API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Yandex Tracker credentials:
```bash
cp .env.example .env
```
Then edit `.env` and add your:
- YANDEX_TRACKER_TOKEN: Your OAuth token
- YANDEX_TRACKER_ORG_ID: Your organization ID

## Running the Server

```bash
python -m src.server
```

## Available Tools

### Get Issue
Retrieves issue details from Yandex Tracker.

Input:
```json
{
    "issue_id": "ISSUE-123"
}
```

## Testing

Use MCP Inspector to test the server functionality. 