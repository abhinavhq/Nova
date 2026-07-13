"""
nova/coding_helper.py

Phase 6: Coding workflows.

Documentation lookup, GitHub issue triage, and Stack Overflow research
all reduce to the same underlying task Nova already does well: navigate
to a site, search/find the relevant content, and summarize it. This
module wraps NovaAgent with goal templates tuned for these specific
coding-research tasks, rather than building new browsing mechanics.
"""

from nova.agent import NovaAgent
from nova.browser import NovaBrowser


def lookup_documentation(browser: NovaBrowser, library_or_topic: str, question: str, base_url: str) -> str:
    """
    Navigate to a documentation site and find the answer to a specific
    question about a library/topic.

    base_url: the docs site's homepage/search entry point, e.g.
        "https://docs.python.org/3/" or "https://react.dev/reference/react"
    """
    browser.goto(base_url)
    goal = (
        f"You are on the official documentation site for {library_or_topic}. "
        f"Find information to answer this question: {question}. "
        f"Search or navigate as needed, then report back a concise, accurate answer "
        f"based on what the documentation actually says."
    )
    agent = NovaAgent(browser=browser, max_steps=10)
    return agent.run(goal)


def research_stackoverflow(browser: NovaBrowser, error_or_question: str) -> str:
    """
    Search Stack Overflow for a specific error message or question, and
    summarize the most relevant/top-voted answer pattern found.
    """
    browser.goto("https://stackoverflow.com")
    goal = (
        f"Search Stack Overflow for: {error_or_question}. "
        f"Find the most relevant question and its top answer, then summarize "
        f"the key fix/explanation in your own words - do not copy long passages verbatim."
    )
    agent = NovaAgent(browser=browser, max_steps=10)
    return agent.run(goal)


def triage_github_issues(browser: NovaBrowser, repo_url: str, focus: str = "") -> str:
    """
    Navigate to a GitHub repo's issues page and summarize open issues,
    optionally focused on a specific topic/keyword.
    """
    issues_url = repo_url.rstrip("/") + "/issues"
    browser.goto(issues_url)
    goal = (
        f"You are on a GitHub repository's issues page. "
        f"List and briefly summarize the open issues you can see"
        + (f", focusing on ones related to: {focus}" if focus else "")
        + ". Report back a short summary of what's currently open."
    )
    agent = NovaAgent(browser=browser, max_steps=10)
    return agent.run(goal)