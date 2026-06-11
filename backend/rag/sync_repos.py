from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from rag.config_loader import load_config


@dataclass
class RepoSyncResult:
    """Result of syncing the local repo with the remote."""

    repo_name: str
    success: bool
    changed_files: list[str] = field(
        default_factory=list
    )  # absolute paths of edited/added
    error: str | None = None  # only exists if success is false
    already_synced: bool = False  # no files were changed if true


def sync_single_repo(repo_url: str, dest_dir: Path) -> RepoSyncResult:
    """
    Clones/updates a repo into a specified directory.

    Args:
        repo_url (str): URL of the remote repository.
        dest_dir (Path): The directory to sync the the repo into.

    Returns:
        RepoSyncResult: The result of syncing
    """
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = dest_dir / repo_name

    try:
        if repo_path.exists():
            pull_result = subprocess.run(
                ["git", "pull"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            if "Already up to date." in pull_result.stdout:
                return RepoSyncResult(
                    repo_name=repo_name, success=True, already_synced=True
                )
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD@{1}", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            changed_files = [
                str(repo_path / f) for f in result.stdout.splitlines() if f.strip()
            ]
        else:
            subprocess.run(["git", "clone", repo_url], cwd=dest_dir, check=True)
            # Everything is new, so all files are "changed"
            changed_files = [str(p) for p in repo_path.rglob("*") if p.is_file()]

        return RepoSyncResult(
            repo_name=repo_name, success=True, changed_files=changed_files
        )

    except subprocess.CalledProcessError as e:
        return RepoSyncResult(repo_name=repo_name, success=False, error=str(e))


def sync_repos() -> list[RepoSyncResult]:
    """
    Finds the file with the repos to be used for the model and clones/updates the repos accordingly
    into the specified directory.

    Returns:
        list[RepoSyncResult]: results of syncing for each repo.
    """

    try:
        config = load_config()
        paths = config.Paths
    except (FileNotFoundError, ValueError):
        print("Config file not found. Exiting...")
        exit(1)

    paths.repo_dest_dir.mkdir(parents=True, exist_ok=True)
    repos = [
        line.strip()
        for line in paths.repo_list_path.read_text().splitlines()
        if line.strip()
    ]

    results: list[RepoSyncResult] = []
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(sync_single_repo, url, paths.repo_dest_dir): url
            for url in repos
        }
        for future in as_completed(futures):
            result = future.result()
            if result.already_synced:
                print(f"{result.repo_name} already caught up.")
            elif result.success:
                print(
                    f"Successfully synced {result.repo_name} ({len(result.changed_files)} changed files)"
                )
            else:
                print(f"Failed to sync {result.repo_name}: {result.error}")
            results.append(result)

    print("Sync complete.")
    return results


if __name__ == "__main__":
    sync_repos()
