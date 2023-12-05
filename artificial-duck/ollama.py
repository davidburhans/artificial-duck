import tiktoken
import requests
import json
import os


encoding = tiktoken.get_encoding(os.environ.get("TOKEN_ENCODING", "r50k_base"))
system_prompt = os.environ.get(
    "SYSTEM_PROMPT",
    """You are an expert software engineer being asked to answer a question
about the following code. Take your time and pay close attention to detail.
Apply examples directly to the provided code when possible. Any code written
should be simple and easy to understand.""",
)
service_url = os.environ.get("OLLAMA_URL") or "http://127.0.0.1:11434"


def read_file(filepath: str, root_dir: str):
    with open(filepath) as file:
        return f"""Code for {filepath.replace(root_dir, "")}:
{file.read()}
"""


def format_files_for_llm(files: list[str], root_dir: str = ""):
    content = ""
    for file_name in files:
        content = f"""{content}
{read_file(file_name, root_dir)}"""
    return content


def prepare_request(question: str, content: str, context: list[int]):
    request_data = dict(
        context=context,
        model="codellama",
        prompt=question,
        stream=False,
        system=f"""{system_prompt}
        {content}""",
    )
    token_count = len(encoding.encode(request_data["prompt"])) + len(
        encoding.encode(request_data["system"])
    )
    return (
        token_count,
        request_data,
    )


def send_request(request_data: dict):
    url = f"{service_url}/api/generate"
    json_data = json.dumps(request_data)
    headers = {"Content-Type": "application/json"}
    r = requests.post(
        url, data=json_data, headers=headers
    )
    if r.ok:
        response_data = r.json()
        return response_data
    else:
        r.raise_for_status()
