{
  "case_id": "c04",
  "detection": {
    "detected": true,
    "kind": "supported_contradiction",
    "reason": "Both reported defects match the target and are supported by the supplied contract, production path and missing assertions. The report correctly distinguishes clone-policy loss from the independent sleep guard omission. This is source-based detection, not reproduction.",
    "target_claim_ids": ["F1-C1", "F2-C1"],
    "evidence": [
      "project/src/urllib3/util/retry.py:32-43 documents reusable Retry configuration; lines 140-154 define the header policy and include 429 and 503.",
      "project/src/urllib3/util/retry.py:174,194,199-215 shows that new() omits the configured flag and restores the True default; increment() returns that copy at lines 425-439.",
      "project/src/urllib3/connectionpool.py:804-835 checks eligibility, increments, sleeps with the response and recursively passes the copied policy.",
      "project/src/urllib3/util/retry.py:274-302 honors a positive Retry-After in sleep(response) without checking the flag.",
      "project/test/test_retry.py:103-189 contains counter, backoff, sleep and eligibility tests without either reported opt-out assertion."
    ]
  },
  "findings": [
    {
      "id": "F1",
      "summary": "Retry copies reset the caller's disabled header policy, enabling an unintended subsequent header-triggered retry.",
      "classification": "accepted_gap",
      "unsupported": false,
      "evidence": [
        "The documented policy is stored by the constructor but omitted from new().",
        "The pool passes the incremented policy into subsequent requests."
      ],
      "claims": [
        {
          "id": "F1-C1",
          "claim": "new()/increment() resets respect_retry_after_header=False to True. For the proposed GET sequence 500 → 429 with Retry-After: 60 → 200 and status_forcelist=[500], this enables the otherwise excluded 429 retry. Preserving the policy should instead return 429 after two requests without sleeping, with the response policy still False.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/src/urllib3/util/retry.py:174,194,199-215 establishes the default reset; lines 425-439 connects it to increment().",
            "project/src/urllib3/util/retry.py:150-154,325-343 permits GET and explicitly forced 500 retries, while header-based 429 eligibility depends on the flag.",
            "project/src/urllib3/connectionpool.py:805-835 propagates the copied policy. Source tracing predicts three requests and a 60-second sleep call for the supplied implementation, assuming ordinary successful response handling.",
            "project/src/urllib3/connectionpool.py:673-678 and project/src/urllib3/response.py:179-181 establish that the response receives the request's Retry policy.",
            "project/src/urllib3/util/retry.py:114-125,282-302 supports the proposed no-sleep expectation with default zero backoff and the policy preserved."
          ]
        },
        {
          "id": "F1-C2",
          "claim": "The cited counter and status-selection tests do not assert preservation of respect_retry_after_header=False after an increment.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/test/test_retry.py:103-112 checks exhaustion and its error message using the default policy.",
            "project/test/test_retry.py:166-189 checks eligibility on freshly constructed policies.",
            "The complete supplied project/test/test_retry.py contains no configuration or assertion involving respect_retry_after_header."
          ]
        }
      ]
    },
    {
      "id": "F2",
      "summary": "sleep(response) independently ignores the disabled header policy, and the supplied timing tests do not protect that interaction.",
      "classification": "accepted_gap",
      "unsupported": false,
      "evidence": [
        "A directly constructed False policy reaches the positive-header sleep without cloning.",
        "The pool's response-status retry path calls this method after incrementing."
      ],
      "claims": [
        {
          "id": "F2-C1",
          "claim": "sleep(response) honors a positive Retry-After despite respect_retry_after_header=False. A directly constructed policy and a 503 response isolate this defect; even with clone preservation repaired, an explicitly forced 503 retry would still select the header delay. The proposed False/True recorder test correctly expects no sleep versus one 60-second sleep call with zero backoff.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/src/urllib3/util/retry.py:140-154 places 503 within the documented opt-out contract.",
            "project/src/urllib3/util/retry.py:248-277 parses the numeric header and calls time.sleep with its positive value.",
            "project/src/urllib3/util/retry.py:288-302 checks only response truthiness before using sleep_for_retry; it never consults the flag.",
            "project/src/urllib3/util/retry.py:335-343 permits explicit status_forcelist retries independently of the header policy.",
            "project/src/urllib3/connectionpool.py:808-820 increments before sleeping. The report acknowledges clone loss separately and uses direct construction to establish independence."
          ]
        },
        {
          "id": "F2-C2",
          "claim": "test_sleep supplies no response and makes no explicit timing assertion; neighboring backoff tests check computed durations rather than header-versus-backoff selection.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/test/test_retry.py:159-164 calls retry.sleep() without a response, recorder or assertion.",
            "project/test/test_retry.py:114-157 asserts get_backoff_time() results and related state.",
            "The complete supplied retry test file contains no positive Retry-After response passed to sleep and no False/True header-policy timing comparison."
          ]
        }
      ]
    }
  ],
  "counts": {
    "findings": 2,
    "claims": 4,
    "unsupported_claims": 0,
    "false_positive_claims": 0
  },
  "control_alarm": false,
  "limitations": [
    "Only the permitted files were inspected. Staging links were mapped to project-relative paths.",
    "No target code, tests or proposed regressions were executed. Behavioral conclusions are source-only model judgments; the report's 'suspected' and 'not reproduced' qualifications remain applicable.",
    "The frozen oracle overstates existing coverage when it says the supplied retry tests exercise header retry eligibility: test/test_retry.py checks explicit status eligibility but contains no header-policy configuration or header-presence eligibility assertion. This does not undermine either detected defect.",
    "Coverage conclusions apply to the supplied files. Oracle statements about upstream history and later regression assertions were not independently verified."
  ]
}
