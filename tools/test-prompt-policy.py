import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name('prompt-policy.py')


class PromptPolicyTest(unittest.TestCase):
    def run_policy(self, text):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'prompt.md').write_text(text)
            return subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True)

    def test_accepts_gate_and_recourse(self):
        result = self.run_policy('The artifact must validate. [Gate: artifact validator; Recourse: rebuild artifact]\n')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_removed_gate(self):
        result = self.run_policy('The artifact must validate. [Recourse: rebuild artifact]\n')
        self.assertEqual(result.returncode, 1)
        self.assertIn('must line needs', result.stdout)

    def test_rejects_removed_recourse(self):
        result = self.run_policy('The artifact must validate. [Gate: artifact validator]\n')
        self.assertEqual(result.returncode, 1)
        self.assertIn('must line needs', result.stdout)


if __name__ == '__main__':
    unittest.main()
