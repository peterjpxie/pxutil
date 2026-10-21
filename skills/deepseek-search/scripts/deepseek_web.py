#!/usr/bin/env python3
"""Search and fetch web content through DeepSeek's Search & Fetch APIs."""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = "https://api.deepseek.com/v1/tools"
TIMEOUT = 60


def post(path, payload):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        sys.exit("DEEPSEEK_API_KEY is not set in the environment")

    request = urllib.request.Request(
        f"{BASE_URL}/{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        try:
            detail = json.loads(error.read().decode("utf-8"))
            message = detail.get("error", {}).get("message", error.reason)
        except (ValueError, UnicodeDecodeError):
            message = error.reason
        sys.exit(f"HTTP {error.code}: {message}")
    except urllib.error.URLError as error:
        sys.exit(f"request failed: {error.reason}")


def print_search(data):
    results = data.get("results", [])
    if not results:
        print("No results.")
        return
    for index, item in enumerate(results, 1):
        meta = []
        if item.get("site_name"):
            meta.append(item["site_name"])
        if item.get("date"):
            meta.append(item["date"])
        if item.get("rerank_score") is not None:
            meta.append(f"score {item['rerank_score']:.2f}")
        if item.get("authority") is not None:
            meta.append(f"authority {item['authority']}")

        print(f"## {index}. {item.get('title') or '(untitled)'}")
        print(f"URL: {item.get('url', '')}")
        if meta:
            print(" | ".join(meta))
        if item.get("summary"):
            print(f"\n**Summary:**\n{item['summary']}")
        elif item.get("snippet"):
            print(f"\n**Snippet:**\n{item['snippet']}")
        if item.get("content"):
            print(f"\n**Content:**\n{item['content']}")
        print()


def print_page(data):
    title = data.get("title")
    if title:
        print(f"# {title}\n")
    print(data.get("content", ""))


def main():
    parser = argparse.ArgumentParser(
        description="Search the web or fetch a page via DeepSeek APIs."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="search the live web")
    search.add_argument("query")
    search.add_argument(
        "-n",
        "--count",
        type=int,
        default=10,
        help="results to return (1-50), default=10",
    )
    search.add_argument(
        "--content",
        action="store_true",
        help="include full page content for each result",
    )
    search.add_argument("--ori-question", help="the user's original question")
    search.add_argument("--localization", help="IP address for localized results")
    search.add_argument("--json", action="store_true", help="output raw JSON")

    fetch = subparsers.add_parser("fetch", help="fetch a page as Markdown")
    fetch.add_argument("url")
    fetch.add_argument("--json", action="store_true", help="output raw JSON")

    args = parser.parse_args()

    if args.command == "search":
        if not 1 <= args.count <= 50:
            parser.error("--count must be between 1 and 50")
        payload = {
            "query": args.query,
            "count": args.count,
            "need_content": args.content,
        }
        if args.ori_question:
            payload["ori_question"] = args.ori_question[:128]
        if args.localization:
            payload["localization"] = args.localization
        data = post("search", payload)
        if args.json:
            json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
            print()
        else:
            print_search(data)
    else:
        data = post("fetch", {"url": args.url})
        if args.json:
            json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
            print()
        else:
            print_page(data)


if __name__ == "__main__":
    main()
