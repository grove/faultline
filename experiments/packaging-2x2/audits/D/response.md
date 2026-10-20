Found two actionable test weaknesses.

1. **Installed-prerelease tests omit exact pins and exclusions**

   **What could go wrong:** [Installed handling](src/packaging/specifiers.py:934) replaces a prerelease with its base version before comparison. Source tracing indicates that `SpecifierSet("!=1.0a1", prereleases=True).contains("1.0a1", installed=True)` returns `True`, retaining an explicitly excluded version. Conversely, an exact `==1.0a1` pin rejects it.

   **Why these tests may miss it:** [The installed tests](tests/test_specifiers.py:694) exercise only `~=1.0`, where removing the developmental suffix produces their expected result.

   **Smallest useful test:** Parameterize `==1.0a1` and `!=1.0a1`, enable prereleases, and check `"1.0a1"` with `installed=True`. Expect `True` and `False`, respectively.

   **Confidence and uncertainty:** High-confidence **suspected implementation bug**, based on source inspection. The `installed` parameter lacks documentation, but [documented exclusion semantics](docs/pep-0440.rst:962) require inversion of equality.

2. **Filter tests never disable prereleases on the `Specifier` object**

   **What could go wrong:** `Specifier(">=1.0", prereleases=False).filter(["2.0a1"])` appears to yield `"2.0a1"`. [Filtering](src/packaging/specifiers.py:598) initially forces inclusion during comparison, then releases buffered prereleases when no final matches—even when the object explicitly disables them.

   **Why these tests may miss it:** [The filter test](tests/test_specifiers.py:556) always constructs a default-policy object. Its `False` case supplies a per-call override, which follows a different path.

   **Smallest useful test:** Construct `Specifier(">=1.0", prereleases=False)`, filter `["2.0a1"]` without an override, and assert an empty result.

   **Confidence and uncertainty:** High-confidence **suspected implementation bug**. The [property contract](src/packaging/specifiers.py:69) says `False` explicitly disables prereleases; automatic fallback remains appropriate for default policy.

Reviewed prerelease detection, membership and filtering, `SpecifierSet`, marker callers, requirement/metadata construction, relevant tests, and docs within the frozen snapshot. Findings are based solely on file inspection; runtime behavior remains unverified. **Tests were not run.**
