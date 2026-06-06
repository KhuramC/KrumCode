import os
import subprocess

from core.config_loader import (
    load_config,
    get_dest_dir,
    get_repo_file,
    DEFAULT_DEST_DIR,
    DEFAULT_REPO_FILE,
)


# Reads in and syncs repositories listed in the specified file into the specified directory.
def sync_repos():

    # parse configuration from config, with fallback to defaults
    try:
        config = load_config()
        REPO_FILE = get_repo_file(config)
        DEST_DIR = get_dest_dir(config)
    except FileNotFoundError:
        print("Config file not found. Using default paths.")
        REPO_FILE = DEFAULT_REPO_FILE
        DEST_DIR = DEFAULT_DEST_DIR

    # Ensure the destination directory exists
    os.makedirs(DEST_DIR, exist_ok=True)

    with open(REPO_FILE, "r") as file:
        repos = [line.strip() for line in file if line.strip()]

    # TODO: Error handling for repo_url + git operations + parallelization?
    for repo_url in repos:
        # Extract the repo name from the URL
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = os.path.join(DEST_DIR, repo_name)

        if os.path.exists(repo_path):
            print(f"Updating existing repo: {repo_name}")
            # Run 'git pull' inside the existing directory
            subprocess.run(["git", "pull"], cwd=repo_path, check=True)
        else:
            print(f"Cloning new repo: {repo_name}")
            # Run 'git clone' in the destination directory
            subprocess.run(["git", "clone", repo_url], cwd=DEST_DIR, check=True)

    print("All repositories have been synced successfully!")


if __name__ == "__main__":
    sync_repos()
