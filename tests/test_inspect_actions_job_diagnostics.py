"""Regression tests for read-only GitHub Actions job diagnostics."""
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "inspect_actions_job_diagnostics.py"
spec = importlib.util.spec_from_file_location("inspect_actions_job_diagnostics", MODULE)
diagnostics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostics)


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class DiagnosticsTests(unittest.TestCase):
    def test_missing_steps_reported_without_claiming_root_cause(self):
        requests = []

        def opener(request, timeout):
            requests.append((request, timeout))
            return Response(json.dumps({"name": "quality", "status": "completed",
                                        "conclusion": "failure", "steps": []}).encode())

        result = diagnostics.inspect_job("terraform", 123, "secret", opener)
        self.assertEqual(result["diagnostic"], "missing_job_steps")
        self.assertEqual(result["steps_reported"], 0)
        self.assertEqual(requests[0][1], 15)
        self.assertEqual(requests[0][0].get_header("Authorization"), "Bearer secret")
        self.assertNotIn("secret", json.dumps(result))

    def test_steps_are_preserved_for_triage(self):
        payload = {"status": "completed", "conclusion": "failure",
                   "steps": [{"name": "Checkout", "status": "completed",
                              "conclusion": "success"},
                             {"name": "Test", "status": "completed",
                              "conclusion": "failure"}]}
        result = diagnostics.inspect_job("testrepo", 17, opener=lambda *a, **k: Response(json.dumps(payload).encode()))
        self.assertEqual(result["steps_reported"], 2)
        self.assertEqual(result["steps"][1]["conclusion"], "failure")
        self.assertEqual(result["diagnostic"], "steps_available")

    def test_invalid_inputs_rejected_before_request(self):
        for repo, job_id in (("../private", 12), ("terraform", 0),
                             ("terraform", True), ("", 12)):
            with self.subTest(repo=repo, job_id=job_id):
                with self.assertRaises(ValueError):
                    diagnostics.inspect_job(repo, job_id, opener=lambda *a, **k: self.fail("unexpected network"))

    def test_oversized_and_nonobject_job_metadata_rejected(self):
        for payload in (b" " * 65537, b"[]", b"null"):
            with self.subTest(length=len(payload)):
                with self.assertRaisesRegex(ValueError, "job_metadata_limit_exceeded|invalid_job_metadata"):
                    diagnostics.inspect_job("terraform", 123, opener=lambda *a, **k: Response(payload))

    def test_api_failure_has_safe_structured_result(self):
        with patch.object(diagnostics, "inspect_job", side_effect=OSError("secret internal path")):
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                rc = diagnostics.main(["--repo", "terraform", "--job-id", "42"])
        self.assertEqual(rc, 2)
        data = json.loads(output.getvalue())
        self.assertEqual(data["jobs"][0]["error_type"], "OSError")
        self.assertNotIn("secret internal path", output.getvalue())


if __name__ == "__main__":
    unittest.main()
