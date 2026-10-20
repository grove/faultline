1. **`filter()` can ignore an explicit instance-level opt-out.**

   **What could go wrong:** For `Specifier(">=1.0", prereleases=False)`, filtering `["2.0a1"]` appears to return the prerelease. The [implementation](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/src/packaging/specifiers.py:598) forces prerelease membership checks, buffers the candidate, then emits it as fallback despite the explicit opt-out.

   **Why these tests may miss it:** The [direct filter tests](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/tests/test_specifiers.py:556) always construct `Specifier` without an instance-level setting. Their `False` case supplies a method argument instead. `SpecifierSet` resolves and forwards its policy, masking this direct-API gap.

   **Smallest useful test:** Construct that specifier, assert `contains("2.0a1")` is false, and assert filtering the singleton returns `[]`.

   **Confidence and uncertainty:** **Suspected implementation bug; high confidence.** The [property contract](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/src/packaging/specifiers.py:69) says `False` explicitly disables prereleases.

2. **Prerelease autodetection can crash on an accepted arbitrary equality literal.**

   **What could go wrong:** `Specifier("===arbitrarystring").contains("1.0")` reaches [autodetection](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/src/packaging/specifiers.py:259), which calls `Version("arbitrarystring")` and raises `InvalidVersion`. Supplying `prereleases=True` bypasses that parsing and reaches a false equality result. The accepted requirement `name===arbitrarystring` exposes the same default-policy problem through its `SpecifierSet`.

   **Why these tests may miss it:** The [identity membership tests](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/tests/test_specifiers.py:493) use valid PEP 440 literals. The [requirement tests accepting arbitrary strings](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/tests/test_requirements.py:86) check parsing and equality without evaluating candidates.

   **Smallest useful test:** Assert that `Specifier("===arbitrarystring").contains("1.0")` returns false.

   **Confidence and uncertainty:** **Suspected implementation bug; medium confidence.** The [parser’s escape-hatch contract](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/src/packaging/specifiers.py:115) supports this expectation. An intentional restriction limiting such literals to parsing and inspection would change the assessment, but none was located.

3. **Automatic fallback lacks protection when a prerelease arrives first.**

   **What could go wrong:** A regression in buffering could return `"2.0a1"` from candidates `["2.0a1", "1.0"]`, despite a matching final release appearing later.

   **Why these tests may miss it:** The automatic [unit case](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/tests/test_specifiers.py:559) contains only a prerelease. The mixed automatic [doctest](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/src/packaging/specifiers.py:583) puts the matching final first.

   **Smallest useful test:** Filter a one-shot iterator containing `["2.0a1", "1.0"]` with `Specifier(">=1.0")`; expect exactly `["1.0"]`.

   **Confidence and uncertainty:** **Missing test protection; high confidence.** Current buffering appears correct, and the documented fallback rule establishes the expectation.

Reviewed the named methods, `SpecifierSet`, marker/requirement/metadata callers, relevant tests, and local docs. Static inspection only. The nonempty `SpecifierSet` fallback prose conflicts with its doctest, so that ambiguity was not treated as a finding. **Tests were not run.**
