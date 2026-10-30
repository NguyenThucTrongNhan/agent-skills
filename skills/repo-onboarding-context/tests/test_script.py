import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "scripts"
    / "generate_context_tree.py"
)


def run_tree(
    project_root: Path,
    *args: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.is_file(), f"Script not found: {SCRIPT_PATH}"

    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(project_root), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def test_maps_valid_files_and_ignores_directories(tmp_path: Path) -> None:
    project = tmp_path / "mock_project"
    project.mkdir()

    for name, marker in [
        (".git", "GIT_MARKER.txt"),
        ("node_modules", "NODE_MARKER.txt"),
        (".venv", "VENV_MARKER.txt"),
    ]:
        directory = project / name
        directory.mkdir()
        (directory / marker).write_text("mock", encoding="utf-8")

    api = project / "src" / "Core.API"
    api.mkdir(parents=True)
    (api / "Program.cs").write_text(
        'Console.WriteLine("Hello");',
        encoding="utf-8",
    )

    result = run_tree(project, "--depth", "3")

    assert result.returncode == 0, result.stderr
    assert "src/" in result.stdout
    assert "Core.API/" in result.stdout
    assert "Program.cs" in result.stdout

    for ignored in [
        ".git/",
        "node_modules/",
        ".venv/",
        "GIT_MARKER.txt",
        "NODE_MARKER.txt",
        "VENV_MARKER.txt",
    ]:
        assert ignored not in result.stdout


def test_depth_limits_traversal_and_output(tmp_path: Path) -> None:
    project = tmp_path / "project.with.dots"
    shallow = project / "one"
    deep = shallow / "two"

    deep.mkdir(parents=True)
    (shallow / "visible.txt").write_text("visible", encoding="utf-8")
    (deep / "hidden.txt").write_text("hidden", encoding="utf-8")

    result = run_tree(project, "--depth", "1")

    assert result.returncode == 0, result.stderr
    assert "one/" in result.stdout
    assert "visible.txt" in result.stdout
    assert "two/" not in result.stdout
    assert "hidden.txt" not in result.stdout


def test_sensitive_file_names_can_be_shown_but_contents_are_not(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    secret_marker = "UNIQUE_SECRET_CONTENT_DO_NOT_PRINT"
    (project / ".env").write_text(secret_marker, encoding="utf-8")
    (project / "secrets.json").write_text(secret_marker, encoding="utf-8")
    (project / "appsettings.json").write_text(
        secret_marker, encoding="utf-8"
    )
    (project / "private.pem").write_text(secret_marker, encoding="utf-8")

    result = run_tree(project)

    assert result.returncode == 0, result.stderr
    assert ".env" in result.stdout
    assert "secrets.json" in result.stdout
    assert "appsettings.json" in result.stdout
    assert "private.pem" in result.stdout
    assert secret_marker not in result.stdout
    assert secret_marker not in result.stderr


def test_ignored_extensions_are_case_insensitive(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    (project / "image.PNG").write_bytes(b"not a real image")
    (project / "readme.md").write_text("hello", encoding="utf-8")

    result = run_tree(project)

    assert result.returncode == 0, result.stderr
    assert "image.PNG" not in result.stdout
    assert "readme.md" in result.stdout


def test_output_is_sorted(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    (project / "z.txt").write_text("z", encoding="utf-8")
    (project / "a.txt").write_text("a", encoding="utf-8")

    result = run_tree(project)

    assert result.returncode == 0, result.stderr
    assert result.stdout.index("a.txt") < result.stdout.index("z.txt")


def test_missing_path_returns_error(tmp_path: Path) -> None:
    result = run_tree(tmp_path / "missing")

    assert result.returncode == 2
    assert "does not exist" in result.stderr


def test_negative_depth_returns_error(tmp_path: Path) -> None:
    result = run_tree(tmp_path, "--depth", "-1")

    assert result.returncode != 0
    assert "non-negative" in result.stderr


def test_output_limit_reports_truncation(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    for index in range(5):
        (project / f"file-{index}.txt").write_text(
            "data", encoding="utf-8"
        )

    result = run_tree(project, "--max-lines", "2")

    assert result.returncode == 3
    assert "[Truncated]" in result.stderr


def test_directory_symlink_is_not_followed(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "OUTSIDE_MARKER.txt").write_text(
        "outside", encoding="utf-8"
    )

    try:
        (project / "external-link").symlink_to(
            outside,
            target_is_directory=True,
        )
    except (OSError, NotImplementedError):
        pytest.skip("Directory symlinks are unavailable in this environment")

    result = run_tree(project)

    assert result.returncode == 0, result.stderr
    assert "OUTSIDE_MARKER.txt" not in result.stdout

@pytest.fixture
def tree_module():
    spec = importlib.util.spec_from_file_location("tree_under_test", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_path_uses_current_working_directory(tmp_path: Path) -> None:
    project = tmp_path / "cwd-project"
    project.mkdir()
    (project / "CWD_MARKER.txt").touch()
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--depth", "3"],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "cwd-project/" in result.stdout
    assert "CWD_MARKER.txt" in result.stdout


def test_file_path_returns_error(tmp_path: Path) -> None:
    target = tmp_path / "not-a-directory.txt"
    target.touch()
    result = run_tree(target)
    assert result.returncode == 2
    assert "not a directory" in result.stderr


@pytest.mark.parametrize("value", ["0", "-1", "invalid", "1.5"])
def test_invalid_max_lines_returns_argument_error(tmp_path: Path, value: str) -> None:
    result = run_tree(tmp_path, "--max-lines", value)
    assert result.returncode == 2
    assert "positive integer" in result.stderr


@pytest.mark.parametrize(
    "file_count,limit,expected_code",
    [
        (0, 1, 0),  # Root alone exactly fits.
        (1, 2, 0),  # Root and one file exactly fit.
        (2, 2, 3),  # One more entry than the limit.
        (1, 3, 0),  # Output below the limit.
    ],
)
def test_output_limit_boundary(
    tmp_path: Path, file_count: int, limit: int, expected_code: int
) -> None:
    project = tmp_path / "boundary-project"
    project.mkdir()
    for index in range(file_count):
        (project / f"file-{index}.txt").touch()
    result = run_tree(project, "--max-lines", str(limit))
    assert result.returncode == expected_code, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0].startswith("--- Project Tree")
    assert len(lines[1:]) == min(1 + file_count, limit)
    assert ("[Truncated]" in result.stderr) == (expected_code == 3)


def test_permission_callback_returns_scan_error(
    tmp_path: Path, monkeypatch, capsys, tree_module
) -> None:
    # Inject a portable error: chmod-based tests can pass unexpectedly as root
    # and behave differently on Windows.
    blocked = tmp_path / "denied"

    def walk_with_permission_error(path, **kwargs):
        assert kwargs["topdown"] is True
        assert kwargs["followlinks"] is False
        kwargs["onerror"](PermissionError(13, "Permission denied", str(blocked)))
        return iter(())

    monkeypatch.setattr(tree_module.os, "walk", walk_with_permission_error)
    result = tree_module.generate_tree(tmp_path, max_depth=3, max_lines=1000)
    output = capsys.readouterr()
    assert result == 1
    assert "PermissionError" in output.err
    assert str(blocked) in output.err


def test_raised_os_error_returns_scan_error(
    tmp_path: Path, monkeypatch, capsys, tree_module
) -> None:
    def walk_raising_error(path, **kwargs):
        raise OSError(5, "Injected scan failure", str(tmp_path))

    monkeypatch.setattr(tree_module.os, "walk", walk_raising_error)
    result = tree_module.generate_tree(tmp_path, max_depth=3, max_lines=1000)
    output = capsys.readouterr()
    assert result == 1
    assert "Scan failed" in output.err
