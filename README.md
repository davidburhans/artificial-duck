# Artificial Duck

Artificial Duck allows you to ask questions about source code using natural language for free.

## Requirements

You must have [Ollama](https://ollama.ai/) installed and running on your system. If it is not running on the default
location of `http://127.0.0.1:11434`, specify the correct url using the `OLLAMA_URL` env variable.

## Installation

`python3 -m pip install git+https://github.com/davidburhans/artificial_duck.git#egg=artificial_duck`

## Usage

`artificial-duck [-h] [--branch BRANCH] [--query QUERY] [--count] about`

Chat about a file, directory, or git repo using ollama

positional arguments:
  about                 the file, directory, or repo to chat about

options:
  -h, --help            show this help message and exit
  --branch BRANCH, -b BRANCH
                        the branch to clone from the repo
  --query QUERY, -q QUERY
                        ask this question
  --count, -c           Only count the tokens for the request
