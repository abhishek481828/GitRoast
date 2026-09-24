import sys
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from groq import Groq
from mcp_server.tools.github_scraper import GitHubScraper
from mcp_server.tools.code_analyzer import CodeAnalyzer
from mcp_server.tools.idea_debater import IdeaDebater
from mcp_server.tools.scaffolder import ProjectScaffolder
from mcp_server.tools.competitor_researcher import CompetitorResearcher
from mcp_server.tools.team_roaster import TeamRoaster
from mcp_server.personality.engine import PersonalityEngine
from mcp_server.orchestrator import GitRoastOrchestrator

from mcp_server.server import (
    handle_analyze_developer,
    handle_analyze_code_quality,
    handle_stress_test_idea,
    handle_scaffold_project,
    handle_research_competitors,
    handle_roast_team,
)

def print_help():
    print("""
🔥 GitRoast CLI Suite — Available Commands:
============================================

1. Profile Roast:
   python roast.py <username> [personality]
   Example: python roast.py abhishek481828 comedian

2. Code Quality Analysis (pylint + radon complexity + AST secrets):
   python roast.py code <username>
   Example: python roast.py code abhishek481828

3. Multi-Agent Idea Stress Tester (The Believer vs The Destroyer vs The Judge):
   python roast.py debate "<idea>"
   Example: python roast.py debate "An AI app that roasts developer GitHub profiles"

4. AI Project Scaffolder & 4-Week Roadmap:
   python roast.py scaffold "<idea>"
   Example: python roast.py scaffold "AI developer intelligence tool"

5. Competitor Researcher (GitHub Search API + Groq synthesis):
   python roast.py competitors "<topic>"
   Example: python roast.py competitors "developer intelligence"

6. Team Roast & Leaderboard (Compare 2-6 developers):
   python roast.py team <user1,user2,user3>
   Example: python roast.py team torvalds,octocat,abhishek481828
""")

async def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_help()
        return

    cmd = sys.argv[1].lower()
    
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    scraper = GitHubScraper()
    analyzer = CodeAnalyzer()
    engine = PersonalityEngine()
    orch = GitRoastOrchestrator(groq_client)
    debater = IdeaDebater(groq_client)
    scaffolder = ProjectScaffolder(groq_client, github_token=os.getenv("GITHUB_TOKEN"))
    researcher = CompetitorResearcher(groq_client, github_token=os.getenv("GITHUB_TOKEN", ""))
    team_roaster = TeamRoaster(groq_client)

    result = ""

    if cmd == "code" and len(sys.argv) > 2:
        target = sys.argv[2]
        print(f"🧪 Running static code analysis on '{target}''s repos (pylint, radon, AST secrets)...\n")
        result = await handle_analyze_code_quality({"username": target}, analyzer, orch, engine, groq_client)

    elif cmd == "debate" and len(sys.argv) > 2:
        idea = " ".join(sys.argv[2:])
        print(f"⚖️ Starting Multi-Agent Idea Debate for: '{idea}'...\n")
        result = await handle_stress_test_idea({"idea": idea}, debater, orch, engine, groq_client)

    elif cmd == "scaffold" and len(sys.argv) > 2:
        idea = " ".join(sys.argv[2:])
        print(f"🏗️ Scaffolding project and generating 4-week roadmap for: '{idea}'...\n")
        result = await handle_scaffold_project({"idea": idea}, scaffolder, orch, engine, groq_client)

    elif cmd == "competitors" and len(sys.argv) > 2:
        topic = " ".join(sys.argv[2:])
        print(f"🔍 Searching GitHub API for competitor intelligence on: '{topic}'...\n")
        result = await handle_research_competitors({"idea_or_topic": topic}, researcher, engine, groq_client)

    elif cmd == "team" and len(sys.argv) > 2:
        users = sys.argv[2]
        print(f"👥 Scraper analyzing team: {users}...\n")
        result = await handle_roast_team({"usernames": users}, team_roaster, scraper, orch, engine, groq_client)

    else:
        # Default fallback to profile roast
        username = sys.argv[1]
        personality = sys.argv[2] if len(sys.argv) > 2 else "comedian"
        print(f"🔥 Fetching GitHub profile for '{username}' ({personality} mode)...\n")
        result = await handle_analyze_developer({"username": username, "personality": personality}, scraper, orch, engine, groq_client)

    safe_output = result.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
    print(safe_output)

if __name__ == "__main__":
    asyncio.run(main())
