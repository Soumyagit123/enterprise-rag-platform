# Implementation Workflow

This is the standard operating procedure for AntiGravity agents when tackling a Phase.

1. **Plan & Architect**: The Architect Agent reviews the Phase requirements and breaks it down into component-level files.
2. **Decompose & Assign**: Tasks are split (e.g., Backend Agent builds API, Infra Agent writes Dockerfile).
3. **Execute Parallelly**: Agents write their respective code.
4. **Integration**: Code is stitched together, ensuring dependencies (like environment variables and ports) match.
5. **Validate**: Run syntax checks, type checks (mypy), and basic tests (pytest).
6. **Refactor**: Clean up messy code, enforce error handling and logging.
7. **Document**: Update MEMORY/implementation-history.md with what was completed and any deviations from the original plan.
