import os
import sys
import argparse

from . import repo
from .ollama import prepare_request, send_request, format_files_for_llm
import glob

files_to_exclude = ["package-lock.json", "license.md"]
exts_to_exclude = [".pyc", ".lock"]


def should_exclude_path(path: str):
    if os.path.isdir(path):
        return True
    elif os.path.splitext(path)[1].lower() in exts_to_exclude:
        return True
    elif os.path.basename(path).lower() in files_to_exclude:
        return True
    elif "/venv/" in path or "__pycache__" in path:
        return True
    elif "/node_modules/" in path:
        return True
    return False


def print_prompt(about: str):
    conditional_about = "" if about == "" else " about " + about
    sys.stdout.write(
        f"{os.linesep}Please ask a question{conditional_about}{os.linesep} > "
    )
    sys.stdout.flush()


def chat_about(
    content: str, about: str = "", single_query: str = "", count_only: bool = False
):
    context = []
    if single_query is not None and len(single_query) > 0:
        count, request_data = prepare_request(single_query, content, context)
        if count_only:
            print(f"{count} tokens")
        response_data = send_request(request_data)
        print(response_data["response"])
        return
    print_prompt(about)
    for query in sys.stdin:
        if query.startswith("?"):
            print(content)
        else:
            count, request_data = prepare_request(query, content, context)
            if count_only:
                print(f"{count} tokens")
            else:
                response_data = send_request(request_data)
                context = response_data["context"]
                del response_data["context"]
                print(response_data["response"])
        print_prompt(about)


def chat_about_file(file: str, single_query: str = "", count_only: bool = False):
    root_dir = os.path.dirname(file)
    content = format_files_for_llm([file], root_dir)
    about = os.path.basename(file)
    chat_about(content, about=about, single_query=single_query, count_only=count_only)


def chat_about_directory(path: str, about: str = "", single_query: str = "", count_only: bool = False):
    if about == "":
        about = path
    root_dir = path + os.path.sep
    itr = glob.iglob(os.path.join(path, "**"), recursive=True)
    files_in_dir = [f for f in itr if not should_exclude_path(f)]
    content = format_files_for_llm(files_in_dir, root_dir)
    chat_about(content, about=about, single_query=single_query, count_only=count_only)


def cli():
    parser = argparse.ArgumentParser(
        description="Chat about a file, directory, or git repo using ollama"
    )
    parser.add_argument(
        "about", type=str, help="the file, directory, or repo to chat about"
    )
    parser.add_argument(
        "--branch",
        "-b",
        type=str,
        help="the branch to clone from the repo",
        default="main",
    )
    parser.add_argument("--query", "-q", type=str, help="ask this question")
    parser.add_argument(
        "--count",
        "-c",
        help="Only count the tokens for the request",
        action='store_true'
    )
    args = parser.parse_args()
    repo_url = args.about
    branch = args.branch
    if os.path.isdir(repo_url):
        full_path = os.path.abspath(repo_url)
        kwargs = dict(single_query=args.query, count_only=args.count)
        chat_about_directory(full_path, **kwargs)
    elif os.path.isfile(repo_url):
        full_path = os.path.abspath(repo_url)
        kwargs = dict(single_query=args.query, count_only=args.count)
        chat_about_file(full_path, **kwargs)
    else:
        with repo.with_temp_repo_clone(repo_url, branch) as repo_path:
            kwargs = dict(about=repo_url, single_query=args.query)
            chat_about_directory(repo_path, **kwargs)
