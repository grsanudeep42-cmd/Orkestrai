# Gemini CLI Instructions - Orkestrai

This file provides foundational mandates for the Gemini CLI agent to ensure efficient context management and high-quality engineering.

## Context Management & Token Efficiency

### 1. File Access & Ignoring
- **NEVER** read files within `node_modules`, `__pycache__`, `.venv`, `.git`, `build`, `dist`, `.next`, `out`, or `bob_sessions` directories.
- **Ignore Large Assets:** Avoid reading markdown files in `assets/To-do-Workflow/` or `assets/UI-Designs/` unless specifically requested by the user or strictly necessary for implementing a feature. These files are large and can quickly consume context.
- **Respect .gitignore:** Always adhere to patterns defined in `.gitignore`.

### 2. Surgical Reading Patterns
- **Search First:** Use `grep_search` or `glob` to identify specific lines or files of interest before reading.
- **Avoid Full File Reads:** For files exceeding 100 lines, **ALWAYS** use `start_line` and `end_line` parameters in `read_file` to retrieve only the necessary sections.
- **Batch Reads:** When multiple sections of a file are needed, request them in parallel in a single turn.

### 3. Documentation Handling
- **Reference MDs Sparingly:** Do not read `README.md` or other documentation files in their entirety unless the task is specifically about documentation or requires a global understanding of the module.
- **Use Grep for Docs:** If looking for specific information in documentation, use `grep_search` to find the relevant section first.

## Engineering Standards

- **Backend (FastAPI):** Follow existing patterns in `backend/app/`. Use SQLAlchemy for DB operations and Pydantic for schemas.
- **Frontend (Next.js):** Follow existing patterns in `frontend/app/`. Use Tailwind CSS and TypeScript.
- **Validation:** Always verify changes with existing tests or by creating new reproduction scripts. Use `pytest` for backend and appropriate tools for frontend.
- **No Hacks:** Never suppress linter warnings or bypass the type system. Use idiomatic language features.
