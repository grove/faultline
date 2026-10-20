{
  "case_id": "c04",
  "detection": {
    "detected": true,
    "kind": "supported_contradiction",
    "reason": "Both reported mechanisms match the target: cloning loses the explicit False policy, and sleep(response) independently ignores that policy. The report supplies documented inputs, reachable pool paths, incorrect behavior and specific missing assertions. This establishes a source-supported contradiction, not runtime reproduction.",
    "evidence": [
      "project/src/urllib3/util/retry.py:32-43 documents retry-state cloning and public configuration; lines 140-154 define the opt-out for statuses including 429 and 503.",
      "project/src/urllib3/util/retry.py:174-215 defaults the flag to True but omits it from new(); increment() returns that clone at lines 425-439.",
      "project/src/urllib3/connectionpool.py:804-835 checks eligibility, increments, sleeps with the response and recursively requests using the updated policy.",
      "project/src/urllib3/util/retry.py:264-302 reads a positive Retry-After and calls time.sleep without checking the opt-out.",
      "project/test/test_retry.py contains neither False-policy preservation assertions nor response-driven sleep assertions."
    ],
    "target_claim_ids": [
      "F1C1",
      "F1C2",
      "F2C1",
      "F2C2"
    ]
  },
  "findings": [
    {
      "id": "F1",
      "summary": "Retry-state cloning re-enables automatic Retry-After retries despite an explicit opt-out.",
      "classification": "accepted_gap",
      "unsupported": false,
      "evidence": [
        "The report's 500-then-429 sequence uses documented configuration and a default-allowed GET.",
        "The first forced retry produces a clone with the flag reset to True, enabling the subsequent header-based 429 retry."
      ],
      "claims": [
        {
          "id": "F1C1",
          "claim": "With total=2, status_forcelist=[500] and respect_retry_after_header=False, a GET receiving 500 followed by 429 with Retry-After: 10 should return the 429. Instead, new()/increment() resets the flag to True, allowing a ten-second sleep request and an unwanted third request.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/src/urllib3/util/retry.py:140-154 documents the policy and includes 429 among its statuses; lines 174-215 show the default and missing clone parameter.",
            "project/src/urllib3/util/retry.py:325-343 forces the initial 500 retry independently of the flag; after cloning, total=1 and the positive header make 429 eligible.",
            "project/src/urllib3/util/retry.py:377-439 decrements total and returns the new state; the second increment reaches zero without exhaustion.",
            "project/src/urllib3/connectionpool.py:804-835 sleeps and recurses. With the flag preserved, 429 is neither forced nor automatically eligible and is returned at line 837."
          ]
        },
        {
          "id": "F1C2",
          "claim": "test_history uses the default flag and test_status_forcelist checks fresh policies, so neither protects nondefault flag preservation. The proposed real-pool regression should assert two requests, returned status 429, no sleep and a False flag on response.retries.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/test/test_retry.py:166-178 checks fresh status_forcelist policies; lines 234-257 increment default-policy instances and assert history only.",
            "No supplied test configures respect_retry_after_header=False.",
            "project/src/urllib3/connectionpool.py:673-678 passes the active Retry object into the response; project/src/urllib3/response.py:179-181 and 222 document and store that state.",
            "The proposed assertions distinguish the documented two-response outcome from the reachable extra retry without replacing retry helpers."
          ]
        }
      ]
    },
    {
      "id": "F2",
      "summary": "Response-driven sleep ignores the Retry-After opt-out independently of cloning.",
      "classification": "accepted_gap",
      "unsupported": false,
      "evidence": [
        "503 belongs to the documented Retry-After policy domain and remains retryable through an explicit status_forcelist.",
        "A directly configured False instance reaches header-driven sleep without any cloning, establishing a separate implementation defect."
      ],
      "claims": [
        {
          "id": "F2C1",
          "claim": "An explicitly forced 503 retry remains eligible with respect_retry_after_header=False, but its timing should use backoff. sleep(response) instead requests ten seconds for Retry-After: 10 even on a directly configured False instance with zero initial backoff; preserving the flag in new() alone would therefore leave this defect.",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/src/urllib3/util/retry.py:107-125 documents forced retries and backoff; lines 140-154 explicitly permit ignoring Retry-After for 503.",
            "project/src/urllib3/util/retry.py:335-343 checks status_forcelist before the automatic header policy, supporting continued forced eligibility.",
            "project/src/urllib3/util/retry.py:248-277 parses '10' and passes 10 to time.sleep; lines 288-302 contain no flag guard.",
            "The generic sleep docstring describes header precedence, but the class parameter explicitly provides an opt-out for 503.",
            "project/src/urllib3/connectionpool.py:808-820 clones before sleeping. The report's direct sleep example correctly isolates the missing guard from that additional state-loss mechanism."
          ]
        },
        {
          "id": "F2C2",
          "claim": "test_sleep supplies no response and asserts no timing, while test_backoff checks calculated values without response-driven pool sleep. A direct False-policy sleep test should record no calls; a False-policy GET sequence 503, 503, 200 with Retry-After: 10, status_forcelist=[503] and backoff_factor=0.2 should make three requests and record only [0.4].",
          "classification": "accepted_gap",
          "unsupported": false,
          "evidence": [
            "project/test/test_retry.py:159-164 calls sleep() without a response or timing assertion; lines 114-138 assert get_backoff_time() values.",
            "project/src/urllib3/util/retry.py:231-246 yields zero after one consecutive failure and 0.4 after two with factor 0.2; lines 282-286 skip zero backoff.",
            "project/src/urllib3/connectionpool.py:804-837 retries the two forced 503 responses and returns the unforced 200.",
            "Under the current implementation, positive headers instead select time.sleep(10) on each retry. The proposed [0.4] assertion protects both policy preservation and timing composition."
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
    "All judgments are based on supplied source. No imports, tests or scenarios were executed; predicted sleep calls are not measured elapsed times. The report explicitly labels its findings high-confidence suspicions and states that tests were not run.",
    "Coverage conclusions are bounded to the supplied files, not an unavailable complete test suite or dependency environment.",
    "The frozen oracle overstates existing coverage when it says test/test_retry.py exercises header retry eligibility: the supplied tests contain no Retry-After, has_retry_after or respect_retry_after_header cases. Its central defect traces and missing-policy-assertion conclusion are supported.",
    "Report citations were mapped by project-relative path into the supplied project/ directory; staging paths and historical provenance were not inspected."
  ]
}
