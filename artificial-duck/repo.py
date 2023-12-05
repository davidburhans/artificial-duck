from contextlib import contextmanager
from git import Repo
from tempfile import TemporaryDirectory


@contextmanager
def with_temp_repo_clone(repo_url, branch="main"):
    with TemporaryDirectory() as tmp_dir:
        Repo.clone_from(repo_url, tmp_dir, branch=branch)
        yield tmp_dir
