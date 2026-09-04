# Agent Instructions

## Project

- This is a small, dependency-free Python workspace for inline scripts and exercises.
- The current implementation is in `atm.py`; keep changes focused there unless new files are required.
- There is no package manager, build system, or test suite currently configured.

## Development

- Run `python -m py_compile atm.py` after Python changes. The file must contain a valid function body before this check can pass.
- Run scripts directly with `python atm.py` only when a top-level entry point or `if __name__ == "__main__":` guard exists.
- Preserve the existing public function name `Atm_machine` unless a rename is explicitly requested; new functions should use descriptive PEP 8 snake_case names.
- Avoid adding dependencies for simple exercises; document any necessary dependency before introducing it.

## Scope

- Prefer small, direct changes suitable for an instructional script.
- Do not add framework, packaging, or test infrastructure without a concrete need.
