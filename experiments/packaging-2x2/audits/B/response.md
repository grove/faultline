Found two suspected bugs and one missing regression test.

1. **Object-level `prereleases=False` can be ignored by `Specifier.filter`.**

   **What could go wrong:** Filtering `["2.0a1"]` with `Specifier(">=1.0", prereleases=False)` appears to return the prerelease. The [filter implementation](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/src/packaging/specifiers.py:598) checks candidates with prereleases enabled, buffers the match, then yields it when no final version matches. This conflicts with the documented [explicit-disable setting](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/src/packaging/specifiers.py:69).

   **Why these tests may miss it:** The [direct filter tests](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/tests/test_specifiers.py:556) always construct the object with its default setting. Their `False` case supplies a method argument, which takes a different path. `SpecifierSet` tests do exercise constructor-level `False`, but the set passes an explicit boolean to each underlying filter.

   **Smallest useful test:** Construct `Specifier(">=1.0", prereleases=False)`, filter `["2.0a1"]`, and assert the result is `[]`.

   **Confidence and uncertainty:** High-confidence **suspected implementation bug**, based on the explicit-disable contract and source trace; not reproduced.

2. **Installed prerelease normalization can defeat exact pins and exclusions.**

   **What could go wrong:** With `installed=True`, [contains replaces the candidate with its base version](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/src/packaging/specifiers.py:934). Thus `1.0rc1` becomes `1.0` before matching. Source inspection indicates that an exact `==1.0rc1` pin would reject it, while `!=1.0rc1` with prereleases enabled would accept it. This can misclassify whether an installed candidate satisfies a dependency.

   **Why these tests may miss it:** The [installed-prerelease test](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/tests/test_specifiers.py:694) only uses `~=1.0`. Its assertions reward base-version conversion without checking clauses whose meaning depends on the prerelease suffix.

   **Smallest useful test:** Extend that test with candidate `1.0rc1`, `prereleases=True`, and `installed=True`: expect `True` for `==1.0rc1` and `False` for `!=1.0rc1`.

   **Confidence and uncertainty:** **Suspected implementation bug**. The source outcome is clear, and [version-exclusion semantics](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/docs/pep-0440.rst:962) support the expectation. Confidence in the intended installed behavior is lower because that parameter is undocumented here and the existing test deliberately permits base-version conversion for compatible bounds.

3. **Compound requirements lack protection for inferred prerelease inclusion.**

   **What could go wrong:** A requirement such as `demo>=1.0a1,<2` should admit `1.5a1`. Its inferred policy must propagate to the `<2` clause. Requiring every clause to independently opt in, or losing that propagated setting, would reject a valid candidate.

   **Why these tests may miss it:** The [set filter cases](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/tests/test_specifiers.py:703) contain zero or one clause. The [requirement parsing assertions](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/tests/test_requirements.py:137) check parsed equality rather than inclusion behavior.

   **Smallest useful test:** Parse `Requirement("demo>=1.0a1,<2")`; assert its specifier has `prereleases is True`, contains `1.5a1`, and filters `["1.5a1", "2.1"]` to `["1.5a1"]`.

   **Confidence and uncertainty:** High-confidence **missing test protection**. The current [policy inference](/private/tmp/faultline-2x2-20261020.vfmoEH/stage/project/src/packaging/specifiers.py:736) and propagation appear correct.

Reviewed the requested implementation, relevant comparison/version helpers, marker/requirement/metadata callers, associated assertions, and prerelease documentation within the frozen snapshot. Nonempty-set fallback has conflicting prose and doctest expectations, so I did not classify that behavior as a confirmed bug. Findings are from static inspection only.

**Tests were not run.**
