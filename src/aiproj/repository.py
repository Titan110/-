from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


TEXT_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".rb", ".php",
    ".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".ini", ".cfg", ".sh",
    ".sql", ".graphql", ".gql", ".html", ".css", ".scss", ".vue", ".svelte",
}

IGNORED_DIRS = {
    ".git", ".ai", ".venv", "venv", "node_modules", "dist", "build", "target",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".next", "coverage",
}


@dataclass(frozen=True)
class GitInfo:
    branch: str
    commit: str
    status: str


def _run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def find_repo_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("aiproj must be run inside a Git repository")
    return Path(result.stdout.strip()).resolve()


def git_info(root: Path) -> GitInfo:
    return GitInfo(
        branch=_run_git(root, "branch", "--show-current") or "detached",
        commit=_run_git(root, "rev-parse", "HEAD") or "unborn",
        status=_run_git(root, "status", "--short") or "clean",
    )


def iter_project_files(root: Path, max_bytes: int = 256_000):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "Dockerfile", "Makefile", "Procfile", "Gemfile", "Rakefile"
        }:
            continue
        try:
            if path.stat().st_size > max_bytes:
                continue
        except OSError:
            continue
        yield path


def read_text(path: Path, limit: int = 12_000) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return data[:limit]


def project_inventory(root: Path) -> dict[str, list[str]]:
    top_level = sorted(p.name for p in root.iterdir() if p.name not in IGNORED_DIRS)
    manifests = [
        name for name in (
            "pyproject.toml", "requirements.txt", "package.json", "pnpm-lock.yaml",
            "yarn.lock", "go.mod", "Cargo.toml", "pom.xml", "build.gradle",
            "Dockerfile", "docker-compose.yml", "Makefile",
        ) if (root / name).exists()
    ]
    likely_dirs = [
        name for name in (
            "src", "app", "apps", "packages", "lib", "server", "client", "api",
            "tests", "test", "docs", "migrations", "scripts", "infra",
        ) if (root / name).exists()
    ]
    return {"top_level": top_level, "manifests": manifests, "likely_dirs": likely_dirs}
