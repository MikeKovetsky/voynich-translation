from asyncio import subprocess


def git_commit_and_push(message):
    subprocess.run(["git", "commit", "-m", message])
    subprocess.run(["git", "push"])