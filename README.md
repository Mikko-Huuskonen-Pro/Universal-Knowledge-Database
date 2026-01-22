# Universal Knowledge Database (UKDB)

UKDB is an open, AI-agnostic **pack format and toolchain** for shipping structured knowledge and
engine-ready parameters with explicit provenance and integrity hashing.

This repository intentionally targets **deterministic consumption by computation engines**
(e.g. payroll and accounting engines). Therefore UKDB packs are **integer-only** for all numeric fields.

UKDB packs are not authored by humans.
They are produced by compilers, importers, or AI systems and are intended for direct engine consumption.
---

## Core Philosophy

**UKDB is deterministic, integer-first data.**

- No floats (`float`, `double`, `f32`, `f64`) in any canonical numeric fields
- No ambiguous units
- All numeric values are represented as integers with explicit unit conventions
- Packs are validated with JSON Schema and protected with SHA-256 integrity hashes

UKDB is designed to be:
- portable across tools and AI systems
- human-reviewable and machine-validated
- deterministic and versionable
- easy to diff in Git

---

## Numeric Conventions (Hard Rules)

UKDB packs used for computation MUST encode numeric values using these conventions:

### Money
All money is stored as **integer cents**:

- `*_cents: i64`  
  Example: `12.34 EUR` → `1234`

```yaml
daily_allowance_cents: 2320
gross_salary_cents: 350000

Rates (Percentages)
All rates are stored as basis points (1 bp = 0.01%):
*_bp: i64
Example: 25.50% → 2550

income_tax_rate_bp: 2550
pension_employee_rate_bp: 715

Other numeric units
Use explicit suffixes for integers:
_days, _hours, _minutes
_count
_year, _month (when representing calendar parts)

Other numeric units
Use explicit suffixes for integers:
_days, _hours, _minutes
_count
_year, _month (when representing calendar parts)

pay_period_days: 14
dependents_count: 2

Disallowed
UKDB packs MUST NOT contain:
floats (including "23.20" as a number)
implicit units
mixed representations for the same concept

daily_allowance: 23.20   # ❌ disallowed (float + implicit currency)
tax_rate_percent: 25.5   # ❌ disallowed (float)

Pack Purpose: Direct Engine Consumption
This UKDB variant is intended to feed deterministic engines directly:

UKDB Pack (integer-only) → Engine → Output + Trace + Hash



Because all values are already in canonical integer form, engines can:
compute without normalization ambiguity
guarantee cross-machine determinism
produce stable simulation hashes

UKDB Pack (v0.1)
A pack is a folder (or zip) containing:
ukdb.yaml (manifest)
entities.ndjson
sources.ndjson
claims.ndjson
notes.ndjson
links.ndjson
optional blobs/ for attachments referenced by SHA256
See: docs/SPEC_UKDB_0_1.md and docs/PACK_FORMAT.md.
CLI
ukdb init <path> – create an empty pack skeleton at <path>.ukdb/
ukdb build <input_dir> <out_pack> – build a pack from a directory of files into <out_pack>.ukdb/
ukdb validate <pack> – validate pack against JSON Schemas
ukdb hash <pack> – compute and write manifest integrity hashes into ukdb.yaml
Docs: docs/CLI.md
Development

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ukdb --help

On Windows:

.\ukdb.cmd --help

Non-goals
No prompt instructions inside UKDB core files
No model-specific bindings
No floats in canonical numeric fields
No runtime computation inside UKDB tooling
License
MIT (see LICENSE)

---

# ✅ UPDATED ROADMAP.md (ONLY v0.2, integerization + hardening)

```md
# Roadmap

## v0.2 — Integer-Only Packs for Deterministic Engines

Goal: make UKDB packs safe to consume **directly** by deterministic computation engines
by enforcing integer-only numeric representations and explicit unit suffix conventions.

### Numeric hardening (breaking-in-spirit, but implement as non-breaking if possible)
- [ ] Define and document canonical numeric conventions:
  - Money: `_cents` (i64)
  - Rates: `_bp` basis points (i64)
  - Counts/durations: `_count`, `_days`, `_hours`, etc. (i64)
- [ ] Update JSON Schemas (or add schema profiles) to validate:
  - no floats in canonical numeric fields
  - required suffix conventions for money/rates
- [ ] Add `ukdb validate` rules/warnings:
  - reject floats where integers are expected
  - detect ambiguous fields (e.g. `salary: 3500` without `_cents`)

### Tooling & integrity
- [ ] Ensure deterministic output ordering for all ndjson files
- [ ] Strengthen `ukdb hash` integrity section (stable hashing rules documented)

### Extraction improvements
- [ ] Rule-based extraction from Markdown headings & frontmatter
- [ ] Preserve numeric literals from sources, but map to canonical integer fields when rules are known

### Interoperability
- [ ] `ukdb merge A B -> C` (deterministic merge, dedupe by IDs and hashes)
- [ ] Optional adapter: export conversation/history into a pack (still AI-agnostic)

### Explicit non-goals for v0.2
- ❌ No numeric computation or rounding inside UKDB tooling
- ❌ No engine-specific business logic execution

