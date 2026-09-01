from __future__ import annotations

import unittest

import run_conformance as h


REQUIRED = {
    "one-page-one-worker",
    "two-pages-two-workers",
    "two-pages-same-shared-worker",
    "iframe-to-worker",
    "direct-worker-fallback",
    "misleading-opener-id",
    "worker-url-gstyphoon",
    "worker-url-hashed",
    "worker-url-blob",
    "worker-url-data",
    "worker-url-no-extension",
    "remote-host",
    "cross-port-websocket",
    "loopback-alias",
    "reload-recreated-worker",
    "stale-target-session",
    "exact-supported-identity",
    "wrong-identity",
    "one-room-failure-isolation",
    "advisory-vs-authoritative-role",
}


class HarnessContractTests(unittest.TestCase):
    def test_required_scenarios_are_explicit(self):
        observed = {scenario_id for scenario_id, _zh, _policy in h.SCENARIOS}
        self.assertEqual(REQUIRED, observed)

    def test_every_scenario_has_every_component(self):
        for scenario_id, _zh, policy in h.SCENARIOS:
            with self.subTest(scenario=scenario_id):
                self.assertEqual(set(h.COMPONENTS), set(policy))
                for expected, probes in policy.values():
                    self.assertIn(expected, {h.PASS, h.EXPECTED_ROLE_DIFFERENCE if hasattr(h, "EXPECTED_ROLE_DIFFERENCE") else h.ROLE})
                    self.assertTrue(probes)
                    self.assertTrue(all(probe in h.PROBES for probe in probes))

    def test_role_differences_are_not_hidden_as_pass(self):
        policies = {scenario_id: policy for scenario_id, _zh, policy in h.SCENARIOS}
        self.assertEqual(h.ROLE, policies["exact-supported-identity"]["BROWSER_FLEET"][0])
        self.assertEqual(h.ROLE, policies["wrong-identity"]["BROWSER_FLEET"][0])
        self.assertEqual(h.ROLE, policies["two-pages-same-shared-worker"]["BROWSER_FLEET"][0])
        self.assertEqual(h.ROLE, policies["two-pages-two-workers"]["PYLAUNCH"][0])

    def test_safety_probes_cover_all_components(self):
        self.assertEqual(set(h.COMPONENTS), set(h.SAFETY_PROBES))
        for probes in h.SAFETY_PROBES.values():
            self.assertTrue(probes)
            self.assertTrue(all(probe in h.PROBES for probe in probes))

    def test_mutation_scan_does_not_forbid_observing_blob_or_data_urls(self):
        sample = "url='blob:https://x/id'; other='data:text/javascript,x'"
        self.assertFalse(any(pattern.search(sample) for pattern in h.FORBIDDEN_MUTATION_PATTERNS.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
