{
  "case_id": "c01",
  "detection": {
    "detected": false,
    "kind": "protected",
    "reason": "The declared Retry-After policy interaction is protected by implementation guards and meaningful assertions. Neither reported finding alleges that historical defect persists. Both identify supported alternative gaps.",
    "evidence": [
      "project/src/urllib3/util/retry.py:199-216 preserves respect_retry_after_header in new(); increment() uses new() at 426-433.",
      "project/src/urllib3/util/retry.py:298-303 checks respect_retry_after_header before honoring the response header.",
      "project/test/test_retry.py:293-298 asserts propagation for both policy values; 300-343 asserts sleep versus no sleep for positive numeric and absolute-date headers.",
      "The manager-default policy loss and absolute-date timezone error are distinct from the protected interaction."
    ],
    "target_claim_ids": []
  },
  "findings": [
    {
      "id": "F1",
      "summary": "Manager-level status retry policy is lost when following a redirect without a per-request Retry override.",
      "classification": "accepted_gap",
      "unsupported": false,
      "evidence": [
        "The documented manager-level policy reaches the initial pool, but PoolManager reconstructs redirect retries from request kwargs without supplying that default.",
        "This concerns status retry selection after a redirect, within the declared policy-preservation scope; it is distinct from redirect sleep_for_retry behavior."
      ],
      "claims": [
        {
          "id": "F1C1",
          "claim": "With manager-only Retry(total=2, status_forcelist=[503]), an eligible GET receiving a relative-location 302 followed by a 503 without Retry-After is predicted to return 503 instead of retrying to the available 200, contrary to the documented pool-level policy.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/docs/user-guide.rst:392-400 promises a manager-level retry policy for all requests, with explicit request overrides.",
            "project/src/urllib3/poolmanager.py:159-161,177-202 passes manager configuration into pool construction; project/src/urllib3/connectionpool.py:184-188,597-598 retains and selects that default initially.",
            "project/src/urllib3/poolmanager.py:321-345 disables pool redirect handling, follows the relative location, and calls Retry.from_int(None) when request retries are absent.",
            "project/src/urllib3/util/retry.py:218-225,449-450 selects Retry.DEFAULT; its status_forcelist is empty by 169,188. PoolManager passes the resulting clone explicitly at 359-369.",
            "project/src/urllib3/util/retry.py:333-344 rejects the subsequent 503 without a force-list match or Retry-After; project/src/urllib3/connectionpool.py:804-837 consequently returns it. This is a source-derived prediction, not reproduction."
          ]
        },
        {
          "id": "F1C2",
          "claim": "The supplied status-selection and clone-propagation assertions do not exercise manager-default preservation across redirects; a real manager/pool sequence asserting final 200 after three transport attempts would address this gap.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/test/test_retry.py:171-194 tests is_retry() directly; 293-298 tests new() directly.",
            "The supplied test/test_retry.py contains no manager or pool request integration test. Its redirect test at 152-162 exercises Retry.increment() and backoff directly.",
            "Keeping manager and pool urlopen() real would traverse the policy replacement at project/src/urllib3/poolmanager.py:343-369. The proposed test has not been executed."
          ]
        },
        {
          "id": "F1C3",
          "claim": "An explicit per-request Retry bypasses this particular policy-loss path.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/src/urllib3/poolmanager.py:343-345 skips conversion for a Retry instance.",
            "project/src/urllib3/util/retry.py:199-216 preserves status_forcelist during cloning, and increment() delegates to new() at 426-433.",
            "project/src/urllib3/poolmanager.py:359-369 forwards that updated policy to the redirected request."
          ]
        }
      ]
    },
    {
      "id": "F2",
      "summary": "Absolute Retry-After dates use local-time conversion, while the existing frozen clock masks the timezone error.",
      "classification": "accepted_gap",
      "unsupported": false,
      "evidence": [
        "The implementation promises to sleep for the server-requested duration but converts the absolute date with time.mktime().",
        "The frozen oracle expressly leaves timezone correctness open; its protected policy assertions do not refute this separate defect."
      ],
      "claims": [
        {
          "id": "F2C1",
          "claim": "At 11:00 GMT on a host whose local offset is UTC+02:00, a 12:00 GMT Retry-After date is predicted to become a past deadline, allowing an eligible 503 status retry to proceed immediately instead of waiting 3,600 seconds.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/src/urllib3/util/retry.py:140-142,289-295 defines respecting Retry-After and sleeping for the requested duration.",
            "project/src/urllib3/util/retry.py:249-263 parses the date with email.utils.parsedate(), converts its clock fields with local-time time.mktime(), subtracts time.time(), and clamps negative durations to zero.",
            "Under the stated offset, local noon corresponds to 10:00 GMT, producing a negative difference from 11:00 GMT instead of the correct positive hour.",
            "With an eligible method, retries remaining and respect_retry_after_header=True, the header-bearing 503 reaches project/src/urllib3/connectionpool.py:804-835. Retry.sleep_for_retry() skips zero at retry.py:275-281, and the default backoff is zero.",
            "This supports the report's high-confidence suspected bug under its stated conditions; no runtime result was obtained."
          ]
        },
        {
          "id": "F2C2",
          "claim": "The absolute-date sleep assertions can conceal the shared timezone error because their frozen current time also uses mktime(); numeric-header assertions do not cover date conversion. An independent UTC clock with a controlled non-UTC timezone would expose the gap.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/test/test_retry.py:305-312 expects a one-hour difference between absolute UTC dates.",
            "project/test/test_retry.py:322-330 constructs the mocked current epoch through time.mktime() on the same date, allowing the shared local offset to cancel.",
            "project/test/test_retry.py:286-291 and 303-304 exercises numeric values, which take the separate integer branch at project/src/urllib3/util/retry.py:251-252.",
            "The assertions at project/test/test_retry.py:338-343 meaningfully protect the policy flag, but do not independently establish UTC correctness.",
            "The proposed real-pool 503-to-200 regression with mocked sleep and an independently calculated UTC epoch is grounded; its expected single 3,600-second sleep remains unexecuted."
          ]
        }
      ]
    }
  ],
  "counts": {
    "findings": 2,
    "claims": 5,
    "unsupported_claims": 0,
    "false_positive_claims": 0
  },
  "control_alarm": false,
  "limitations": [
    "Assessment used only the permitted report, rubric, oracle and supplied project files. Staging citations were mapped to project-relative paths.",
    "No target imports, tests or other target execution occurred. Source-only judgment is not reproduction; both proposed regressions remain unverified by execution.",
    "Coverage conclusions apply only to the supplied files, not the complete upstream test suite.",
    "The frozen oracle's protected classification is supported for its exact target and does not establish correctness of either alternative interaction."
  ]
}
