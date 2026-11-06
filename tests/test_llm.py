from pathlib import Path
from unittest.mock import patch
from src.cli import main as cli_main
from src.llm import is_demo_mode, synthesize_contracts
from src.scanner import scan_repository


def test_is_demo_mode(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    assert not is_demo_mode()
    monkeypatch.setenv("DEMO_MODE", "true")
    assert is_demo_mode()


def test_synthesize_contracts_precalculated_fallback(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'pkg'")

    report = scan_repository(tmp_path)
    yaml_txt, md_txt, engine = synthesize_contracts(report)
    assert engine == "precalculated_deterministic"
    assert "version: '1.0'" in yaml_txt
    assert "Agent Operating Guidelines" in md_txt


def test_synthesize_contracts_mocked_llm(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'pkg'")
    report = scan_repository(tmp_path)

    mock_llm_out = "version: '2.0-custom'\n===SPLIT===\n# Custom AGENTS.md from LLM"
    with patch("src.llm.call_llm", return_value=mock_llm_out):
        yaml_txt, md_txt, engine = synthesize_contracts(report, force_llm=True)
        assert engine == "llm_synthesized"
        assert "version: '2.0-custom'" in yaml_txt
        assert "# Custom AGENTS.md from LLM" in md_txt


def test_cli_fix_with_llm_flag(tmp_path: Path, capsys):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'pkg'")
    assert cli_main(["fix", str(tmp_path), "--llm"]) == 0
    out = capsys.readouterr().out
    assert "Auto-Onboarded" in out

