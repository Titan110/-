from pathlib import Path

from aiproj.init_layer import initialize


def test_initialize_creates_cognitive_layer(tmp_path: Path, monkeypatch):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)

    created = initialize(tmp_path)

    assert (tmp_path / ".ai" / "project.md") in created
    assert (tmp_path / ".ai" / "architecture.md").exists()
    assert (tmp_path / ".ai" / "constraints.md").exists()
    assert (tmp_path / ".ai" / "state.md").exists()
    assert (tmp_path / ".ai" / "knowledge" / "README.md").exists()


def test_initialize_does_not_overwrite_without_force(tmp_path: Path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    ai = tmp_path / ".ai"
    ai.mkdir()
    project = ai / "project.md"
    project.write_text("custom\n", encoding="utf-8")

    initialize(tmp_path)

    assert project.read_text(encoding="utf-8") == "custom\n"
