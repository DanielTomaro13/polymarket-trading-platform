# How to Run the Platform

This guide covers the two primary ways to run your Polymarket Trading Platform: using Docker (recommended) or running it locally for development. It also includes instructions on connecting the Claude Desktop App via MCP.

---

## 1. Running with Docker (Recommended)

Docker is the easiest way to run the platform because it automatically spins up the frontend, backend, and a TimescaleDB (PostgreSQL) instance without requiring manual configuration.

### Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop).

### Start the Platform
Run this command from the root directory (`/polymarket`):
```bash
docker-compose up --build
```

- The **Frontend Dashboard** will be available at: `http://localhost:3000`
- The **Backend API** will be available at: `http://localhost:8000`
- The **Database** will be automatically wired up — no setup required!

To stop the platform, press `Cmd + C` (or `Ctrl + C`) in the terminal, or run:
```bash
docker-compose down
```

---

## 2. Running Locally (For Development)

If you are writing code or making edits, you may want to run the servers natively instead of inside containers.

### Terminal 1: Backend
1. Open a terminal in the `backend` folder.
2. Create and activate a virtual environment (only needed the first time):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```
3. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Terminal 2: Frontend
1. Open a new terminal in the `frontend` folder.
2. Install dependencies (only needed the first time):
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

---

## 3. Connecting the Claude AI Agent (MCP)

We have built an MCP (Model Context Protocol) integration so that you can control the platform directly from the Claude Desktop app. Claude will be able to analyze markets, suggest trades, and execute orders through your running backend.

### Setup Instructions
1. Ensure you have the [Claude Desktop App](https://claude.ai/download) installed.
2. Open your Claude Desktop configuration file:
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
3. Add the following JSON configuration to the file. Make sure to replace the paths with the exact absolute paths on your machine if they differ.

```json
{
  "mcpServers": {
    "polymarket_agent": {
      "command": "/Users/danieltomaro/Documents/Projects/polymarket/backend/venv/bin/python",
      "args": [
        "/Users/danieltomaro/Documents/Projects/polymarket/backend/mcp_server_proxy.py"
      ]
    }
  }
}
```

### How to Use the Agent
- Ensure your backend server is running (either via Docker or Locally on port 8000).
- Open Claude Desktop. You should see a small `⚒️` (Hammer) icon indicating that tools are enabled.
- Simply ask Claude:
  > *"Research the Polymarket odds for the Chiefs to win the Super Bowl."*
  > *"Scan Kalshi and Polymarket for any current arbitrage gaps."*
  > *"What is your expected value sizing for buying 'YES' on the Celtics winning the NBA Championship?"*

Claude will securely proxy these requests through your local platform!
