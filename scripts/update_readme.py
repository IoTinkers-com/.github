#!/usr/bin/env python3
"""
Auto-generates the projects list in the organization profile README
by fetching repositories from the GitHub API.

Replaces content between PROJECTS_LIST_EN_START/END and PROJECTS_LIST_ES_START/END markers.
"""

import os
import re
import sys
import urllib.request
import json
from datetime import datetime


ORG = "IoTinkers-com"
README_PATH = os.path.join(os.path.dirname(__file__), "..", "profile", "README.md")
API_URL = f"https://api.github.com/orgs/{ORG}/repos?per_page=100&type=all"


def fetch_repos():
    """Fetch all public repos from the organization via GitHub API."""
    token = os.environ.get("GITHUB_TOKEN", "")
    req = urllib.request.Request(API_URL)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req) as resp:
        repos = json.loads(resp.read().decode("utf-8"))

    # Filter out the .github profile repo itself, sort by updated_at desc
    repos = [r for r in repos if r["name"] != ".github"]
    repos.sort(key=lambda r: r.get("updated_at", ""), reverse=True)
    return repos


def generate_table(repos, lang="en"):
    """Generate a markdown table of repositories."""
    if lang == "es":
        header = "| Proyecto | Descripción | Lenguaje |\n|---|---|---|"
        updated_label = "Última actualización"
    else:
        header = "| Project | Description | Language |\n|---|---|---|"
        updated_label = "Last updated"

    # Use a list format instead of table for better readability on GitHub
    lines = []
    for repo in repos:
        name = repo["name"]
        desc = repo.get("description") or ""
        lang_name = repo.get("language") or "—"
        url = repo["html_url"]
        is_private = repo.get("private", False)
        visibility = "🔒 " if is_private else "🌐 "
        lines.append(f"- {visibility}[**{name}**]({url}) — {desc} (`{lang_name}`)")

    return "\n".join(lines)


def update_section(content, marker_start, marker_end, new_content):
    """Replace content between markers."""
    pattern = rf"({re.escape(marker_start)})(.*?)({re.escape(marker_end)})"
    replacement = rf"\1\n{new_content}\n\3"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def main():
    print(f"Fetching repos for {ORG}...")
    repos = fetch_repos()
    print(f"Found {len(repos)} repositories")

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    en_table = generate_table(repos, lang="en")
    es_table = generate_table(repos, lang="es")

    content = update_section(
        content, "<!-- PROJECTS_LIST_EN_START -->", "<!-- PROJECTS_LIST_EN_END -->", en_table
    )
    content = update_section(
        content, "<!-- PROJECTS_LIST_ES_START -->", "<!-- PROJECTS_LIST_ES_END -->", es_table
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("README updated successfully")


if __name__ == "__main__":
    main()
