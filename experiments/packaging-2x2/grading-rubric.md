# Frozen grading rubric

Frozen before all four audits. Review the emitted report against its supplied
source/test/document packet only. Do not assume the coordinator's historical
expectation is correct. No external retrieval, Git history, project execution,
or other reports. The assigned instruction version and treatment label are hidden.

The primary historical question is default membership below an explicit
prerelease exclusive bound, for example `3.0.0a7` in `<3.0.0a8`. Trace
`Specifier.prereleases`, `contains`, the comparator, and shared assertions that
force `prereleases=True`, separately from default-path assertions. Existing tests
expect False for exclusive dev bounds. They are counterevidence to reconcile,
not automatic proof of the intended policy. The supplied historical PEP, if
present, is evidence to interpret together with its general prerelease rules;
do not transfer a comparison rule to autodetection without explaining why.

Primary detection is true only if the report explicitly surfaces this exclusive
prerelease-bound/default-policy interaction as a suspected bug or a contract
conflict/question. An explicit conflict counts with the original packet; absence
of normative text must not force an unsupported positive assertion. Record
`bug_claim`, `contract_conflict`, or `miss` separately. Generic prerelease advice,
other valid findings, and forced-prereleases-only comparisons do not count.
Grade quality against information actually supplied, not a stronger report.

Split every substantive finding into materially distinct API/lifecycle claims.
For each claim use exactly one classification:

- accepted_gap: supported unprotected behavior or an actionable, appropriately
  conditional contract question; correct current code can lack protection.
- false_positive: material claim contradicted by supplied evidence, including
  a claimed absence already protected by relevant assertions/fixtures.
- unresolved: material requirement or mechanism cannot be established; flag
  unsupported unconditional assertions explicitly. Uncertainty alone is not false.
- duplicate: adds no distinct claim to an earlier finding.
- out_of_scope: outside the declared packaging prerelease behavior.

Keep all findings. Aggregate a finding conservatively: any material false_positive
claim makes it false_positive; otherwise any unresolved claim makes it unresolved;
otherwise any accepted_gap makes it accepted_gap; otherwise all-duplicate is
duplicate and all-out_of_scope is out_of_scope. Explain mixed cases explicitly.
Count unsupported claims separately from identified false positives. Record
ambiguity handling as appropriate, inappropriate, no_ambiguity, or mixed, with
evidence; distinguish conditional assertions from merely hedged prose. A supported
mechanism does not establish a policy, and one API's policy does not define another.

Return JSON only, using this structure:
{"detection":{"detected":true,"kind":"bug_claim|contract_conflict|miss","finding_ids":[],"reason":"...","appropriate_to_supplied_information":true},"findings":[{"id":"F1","title":"...","classification":"accepted_gap|false_positive|unresolved|duplicate|out_of_scope","claims":[{"id":"F1a","claim":"...","classification":"...","unsupported":false,"reason":"...","evidence":["path:line and explanation"],"counterevidence":"..."}],"ambiguity_handling":"appropriate|inappropriate|no_ambiguity|mixed","ambiguity_reason":"..."}],"counts":{"findings":0,"claims":0,"unsupported_claims":0,"false_positive_claims":0},"limitations":["..."]}

This is independent LLM source judgment, not human adjudication or reproduction.
One run per cell supports no reliability rate or causal attribution. No additional
audits, selective retries, or skill changes follow an ambiguous grade.
