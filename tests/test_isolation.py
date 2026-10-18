"""Maintainer probe checks; no target-project code or mutation backend runs."""

import errno
import os
import signal
import sys
import tempfile
import unittest

from qualification.macos_canaries import effect_status, observe


class IsolationProbeTests(unittest.TestCase):
    def test_launcher_permission_failure_is_not_an_effect_denial(self):
        result = {"status": "OBSERVED", "returncode": 71, "stdout": "",
                  "stderr": "sandbox-exec: sandbox_apply: Operation not permitted\n"}
        self.assertEqual(effect_status(result), "UNAVAILABLE")

    def test_only_started_successful_child_can_report_permission_denial(self):
        for code in (errno.EACCES, errno.EPERM):
            result = {"status": "OBSERVED", "returncode": 0,
                      "stdout": '{"started": true}\n'
                                '{"effect": "error", "errno": %d}\n' % code}
            self.assertEqual(effect_status(result), "DENIED")
            result["returncode"] = 1
            self.assertEqual(effect_status(result), "UNAVAILABLE")

    def test_timeout_and_transport_errors_are_inconclusive(self):
        self.assertEqual(effect_status({"status": "INCONCLUSIVE"}), "INCONCLUSIVE")
        for code in (errno.ETIMEDOUT, errno.ECONNREFUSED, errno.ENOENT):
            self.assertEqual(effect_status({
                "status": "OBSERVED", "returncode": 0,
                "stdout": '{"started": true}\n'
                          '{"effect": "error", "errno": %d}\n' % code,
            }), "INCONCLUSIVE")

    def test_missing_executable_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            result = observe([directory + "/missing"], directory, {})
        self.assertEqual(effect_status(result), "UNAVAILABLE")

    @unittest.skipUnless(os.name == "posix", "POSIX process-group observation only")
    def test_finite_timeout_reaps_the_synthetic_leader(self):
        with tempfile.TemporaryDirectory() as directory:
            result = observe([sys.executable, "-I", "-S", "-c",
                              "import time; time.sleep(10)"], directory, {}, timeout=0.1)
        self.assertEqual(effect_status(result), "INCONCLUSIVE")
        self.assertTrue(result["timed_out"])
        self.assertEqual(result["returncode"], -signal.SIGKILL)
        self.assertLess(result["elapsed_seconds"], 3)


if __name__ == "__main__":
    unittest.main()
