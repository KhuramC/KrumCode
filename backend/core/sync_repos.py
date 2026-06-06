from pathlib import Path
import subprocess

from core.config_loader import load_config, get_paths


# Reads in and syncs repositories listed in the specified file into the specified directory.
def sync_repos() -> None:

    try:
        paths: dict[str, Path] = get_paths(load_config())
        repo_file_path: Path = paths["REPO_FILE"]
        destination_dir: Path = paths["DEST_DIR"]

    except FileNotFoundError or ValueError:
        print("Config file not found. Exiting...")
        exit(1)

    # Create directory and get individual repos
    destination_dir.mkdir(parents=True, exist_ok=True)
    repos: list[str] = [
        line.strip() for line in repo_file_path.read_text().splitlines() if line.strip()
    ]

    # TODO: Error handling for repo_url + git operations + parallelization?
    for repo_url in repos:
        # Extract the repo name from the URL
        repo_name: str = repo_url.split("/")[-1].replace(".git", "")

        repo_path: Path = destination_dir / repo_name

        if repo_path.exists():
            print(f"Updating existing repo: {repo_name}")
            # Run 'git pull' inside the existing directory
            subprocess.run(["git", "pull"], cwd=repo_path, check=True)
        else:
            print(f"Cloning new repo: {repo_name}")
            # Run 'git clone' in the destination directory
            subprocess.run(["git", "clone", repo_url], cwd=destination_dir, check=True)

    print("All repositories have been synced successfully!")


if __name__ == "__main__":
    sync_repos()
