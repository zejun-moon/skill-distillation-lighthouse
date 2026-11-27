# skill-distillation-lighthouse

🗼 **A lighthouse for turning real experience into AI-loadable skills** — distil a real
operations/dev session into a skill repository that an AI can load on its own and follow
without getting things wrong, backed by a **machine-enforced redaction standard**.

```
run → desensitized report → pitfall table → executable checks → SKILL.md flow → versioned release
         ↑                                                                  ↑
   machine scan gate                                               redaction self-check + CI
```

## Two questions this repo answers

### ① How do you distil experience into a skill?

Not "write a document" — a flow with explicit gates and pass conditions:

| Step | What | Pass condition |
|---|---|---|
| 1 | Draw the boundary | "what / explicitly not what / can it be public" |
| 2 | Collect evidence | every item can answer "how do I know this is true?" |
| 3 | Write a desensitized report | `field-reports/` with complete frontmatter |
| 4 | **Four-way triage** | recurs → pitfall table; detectable → script; one-off → report only |
| 5 | Write the main flow | SKILL.md < 500 lines, description with bilingual triggers |
| 6 | Machine gate | scanner reports 0 **and** the positive control still bites |
| 7 | Publish | version consistent in four places + **read-back verification** |

Full guide: [`SKILL.md`](skills/skill-distillation-lighthouse/SKILL.md)

### ② What is the redaction standard?

Not "I'll remember to remove it" — a **threat model + replacement table + hard rules +
machine gate**:

- **Threat model**: credentials / internal addresses / private registries / account identity /
  internal uids / org structure / business data / screenshots
- **Replacement table**: real IP → `10.0.0.x`, internal domain → `example.com`,
  prefixed namespace → drop the prefix, uid → parameterize
- **Seven hard rules**: redact by default, err on the side of more, placeholders must look
  like placeholders, …
- **Semantic leaks**: the third class a scanner cannot catch (scale numbers, internal
  weaknesses, org/process details) and how to abstract them
- **After a leak**: changing code is not enough (rotate credentials first)

Full spec: [`references/desensitization.md`](skills/skill-distillation-lighthouse/references/desensitization.md)

## Three tools you can take and use immediately

```bash
# ① general-purpose redaction scanner (copy into any repo)
python3 skills/skill-distillation-lighthouse/scripts/scan-sensitive.py --root /path/to/repo
python3 skills/skill-distillation-lighthouse/scripts/scan-sensitive.py --rules my-rules.json --json out.json

# ② skill-repo structure verifier
python3 skills/skill-distillation-lighthouse/scripts/verify-structure.py --root /path/to/repo

# ③ scaffold a compliant skill repo in one command
bash skills/skill-distillation-lighthouse/scripts/new-skill-scaffold.sh \
     --target ./my-skill-repo --name my-skill \
     --description "Turn X into Y; use this skill whenever the user mentions Z"
```

## Why a skill repo instead of a knowledge base

| | Knowledge base / notes | Skill repo |
|---|---|---|
| Form | long prose | runnable scripts + decision tables |
| How an AI uses it | greps keywords, misses context | follows steps, each with a **pass condition** |
| Verifiability | unclear which sentence is reliable | every claim tagged **measured / inferred / untested** |
| Failure samples | usually omitted | **deliberately recorded** (how the wrong call was made) |
| Updates | relies on someone remembering | `CHANGELOG` + CI + semantic versioning |
| Confidentiality | easy to leak real details | machine scan gate + CI secret scanning |

## Layout

```text
skills/skill-distillation-lighthouse/
  SKILL.md                              # main flow (7 steps + triage + boundaries)
  references/
    desensitization.md                  # the redaction standard (core)
    skill-authoring.md                  # frontmatter / splitting / labelling / boundaries
    repo-layout.md                      # layout + versioning + release + CI
    pitfalls.md                         # 9 pitfalls of building skill repos
    review-checklist.md                 # pre-commit / pre-merge / pre-release checklists
  scripts/
    scan-sensitive.py                   # general-purpose redaction scanner
    verify-structure.py                 # structure verifier
    new-skill-scaffold.sh               # scaffold generator
field-reports/                          # desensitized field reports
tools/check_repo.py                     # this repo's self-check (orchestrates the two tools)
tests/                                  # scanner positive/negative fixtures
```

## Verification status

| Item | Result |
|---|---|
| Self-check (structure + redaction) | **0 problems** |
| Unit tests | **all green** (positive + negative fixtures) |
| Positive control | unsanitized real material → scanner **does hit** (proves it is not a placebo) |
| Script syntax | all pass |
| Scaffold smoke test | generates a compliant skeleton that passes the self-check |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Core rule: **write the desensitized field report
first, then promote the conclusion into `references/pitfalls.md`**, and
`python3 tools/check_repo.py` must exit 0 before you push.

## License

[MIT](LICENSE)
