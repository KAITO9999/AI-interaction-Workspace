import ast
import importlib.util
import sys
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "agentkit_lint.py"
SPEC = importlib.util.spec_from_file_location("agentkit_lint", MODULE)
agentkit_lint = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = agentkit_lint
SPEC.loader.exec_module(agentkit_lint)


class NativeStaticAnalysisTests(unittest.TestCase):
    def test_python_syntax_error_has_location(self):
        findings = agentkit_lint.lint_python_source("def broken(:\n", "broken.py")
        self.assertEqual(findings[0]["rule"], "PY-SYNTAX")
        self.assertEqual(findings[0]["line"], 1)

    def test_python_unused_import_is_detected_but_used_alias_is_not(self):
        findings = agentkit_lint.lint_python_source(
            "import os\nimport json as jsonlib\nprint(jsonlib.dumps({}))\n", "sample.py")
        self.assertEqual([(item["rule"], item["message"]) for item in findings],
                         [("F401", "unused import 'os'")])

    def test_python_bare_except_and_mutable_default_are_detected(self):
        findings = agentkit_lint.lint_python_source(
            "def f(value=[]):\n    try:\n        return value\n    except:\n        return []\n", "sample.py")
        self.assertEqual({item["rule"] for item in findings}, {"E722", "PY-MUTABLE-DEFAULT"})

    def test_python_init_imports_are_not_assumed_unused(self):
        findings = agentkit_lint.lint_python_source("from .api import public_name\n", "pkg/__init__.py")
        self.assertEqual(findings, [])

    def test_shell_unquoted_expansion_is_detected(self):
        findings = agentkit_lint.lint_shell_source('echo $HOME\nprintf "%s" "$USER"\n')
        self.assertEqual([(item["rule"], item["line"]) for item in findings], [("SC2086", 1)])

    def test_shell_quoted_expansion_and_comments_do_not_trigger(self):
        findings = agentkit_lint.lint_shell_source('echo "$HOME" # echo $BAD\n# echo $ALSO_BAD\nname=$HOME\n')
        self.assertEqual(findings, [])

    def test_shell_command_substitution_and_export_status_pitfall_are_detected(self):
        findings = agentkit_lint.lint_shell_source('echo $(find . -name "*.py")\nexport RESULT=$(tool)\n')
        rules = [item["rule"] for item in findings]
        self.assertIn("SC2046", rules)
        self.assertIn("SC2155", rules)

    def test_shell_legacy_backticks_and_exit_status_pattern_are_reported(self):
        findings = agentkit_lint.lint_shell_source('result=`date`\nif [ $? -eq 0 ]; then :; fi\n')
        self.assertIn("SC2006", [item["rule"] for item in findings])
        self.assertIn("SC2181", [item["rule"] for item in findings])

    def test_shell_unknown_dialect_is_rejected(self):
        with self.assertRaises(ValueError):
            agentkit_lint.lint_shell_source("echo ok", "fish")


if __name__ == "__main__":
    unittest.main(verbosity=2)
