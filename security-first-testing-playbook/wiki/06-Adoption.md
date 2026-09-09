# 06 · Adoption

None of this arrives at once. The sequence matters more than the ambition: teams
installing every gate in a single quarter produce a pipeline nobody trusts and
everybody bypasses.

## Nine anti-patterns

Each is common, defensible in the moment, and corrosive over a year.

1. **The coverage mandate** — an organisation-wide percentage target. Produces
   assertion-free tests within one quarter.
2. **Retry until green** — automatic reruns instead of quarantine. Hides genuine
   race conditions and destroys the meaning of red.
3. **The separate QA gate** — a team that tests after development. Feedback
   arrives too late to be cheap and too late to be heeded.
4. **Security as a pre-release scan** — findings arrive after the architecture is
   frozen, so they are deferred rather than fixed.
5. **Mock everything** — a green suite proving only that your beliefs about
   collaborators are internally consistent.
6. **The forty-five minute pipeline** — trains the team to batch changes and skip
   local runs, which raises change failure rate.
7. **Buying a fourth scanner** — adding tools in a category you already have
   instead of writing the authorisation tests no tool can write.
8. **Untested backups and runbooks** — recovery procedures never executed are
   hypotheses held with unearned confidence.
9. **Evidence assembled at audit time** — if the pack cannot be produced from the
   pipeline, the controls it describes are not operating.

A useful diagnostic: ask three developers, separately, what happens when the
pipeline goes red. If the answers differ, the process is folklore rather than
policy.

## The operating checklist

### Every pull request
- [ ] Unit, contract and integration suites green
- [ ] Diff coverage ≥ 80% on changed lines
- [ ] SAST, SCA, IaC and secret scans clean of new high findings
- [ ] Authorisation matrix updated for any new endpoint or role
- [ ] Under six minutes end to end

### Every release
- [ ] SBOM generated at build time and stored with the artefact
- [ ] Provenance attestation signed and verified at deploy
- [ ] DAST and performance profile compared against the previous release
- [ ] Accessibility scan clean; keyboard pass on critical journeys
- [ ] Exit criteria met, or exception recorded with an owner and expiry

### Every quarter
- [ ] Threat model refreshed for changed trust boundaries
- [ ] Risk banding and test strategy reviewed and re-dated
- [ ] Mutation score and flakiness rate reviewed per module
- [ ] Recovery drill executed and timed; backup restored
- [ ] Evidence pack produced for one release, at random

## Staged roadmap

### First 90 days — make the pipeline trustworthy
Write the test strategy and risk banding. Get the pull-request pipeline under six
minutes. Introduce quarantine and drive flakiness below 1%. Turn on secret
scanning, SCA and diff coverage as warnings, then as blocks. Write the
authorisation matrix test for the two highest-risk services.

### Months 4–6 — deepen verification, prove the supply chain
Contract tests on the two noisiest boundaries. Real-engine integration tests for
every data-access layer. Nightly mutation testing with a published per-module
score. SBOM on every build; SLSA Build L1 provenance, then signature verification
enforced at deploy.

### Months 7–12 — close the loop on threats and evidence
Threat modelling as a standing design activity, each mitigation landing as a
test. DAST and fuzzing in the nightly stage. Performance thresholds as release
gates. First recovery drill and first chaos experiment. Publish a disclosure
policy and a `security.txt`.

### Beyond 12 months — operate it as a programme
Independent penetration testing with retest. Progressive delivery with automated
rollback. An ASVS L2 coverage claim with a maintained trace table. Quarterly
evidence drills. A bug bounty **only once triage capacity demonstrably exists**.

The most common sequencing error is starting at months 7–12: buying a DAST tool
and a penetration test before the pipeline is fast enough that anyone acts on the
results.

## Seven things worth remembering

1. **Testing is where security knowledge is stored.** A vulnerability class that
   can recur without a test failing is a lesson your team never learned.
2. **Coverage is a floor; mutation score is the signal.** Executing a line is not
   verifying a behaviour, and in the AI era that gap is widening fast.
3. **Nothing automated finds broken access control.** It stays at number one
   because it is application-specific. Write the matrix by hand.
4. **Prove what you shipped and how it was built.** SBOM, provenance, signature,
   VEX. Supply chain entered the OWASP Top 10 at number three for a reason.
5. **A gate must be fast, written down, and machine-checkable.** Anything else is
   renegotiated under deadline pressure, every time.
6. **Shift right as deliberately as you shift left.** Some properties only exist
   under real traffic.
7. **Evidence should fall out of the pipeline.** If the audit pack takes a
   project to assemble, the controls it describes are not really operating.
