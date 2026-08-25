**Fictive Inc. Engineering & Code Style Guidelines**

**General Principles**

* **Readability Over Cleverness:** Code is read far more often than it is written. Prefer clear, explicit logic over compact, obscure tricks.
* **Consistency Rules:** Adhere to the existing conventions of the codebase. Homogeneous code reduces cognitive load across the team.
* **Fail Fast & Explicitly:** Validate inputs early, handle edge cases explicitly, and avoid swallowing errors silently.

---

**Style & Formatting Standards**

| Category | Standard | Example / Notes |
| --- | --- | --- |
| **Naming Conventions** | CamelCase for classes/types; camelCase for variables/functions; UPPER_CASE for global constants. | `class UserProfile`, `function calculateTotal()`, `MAX_RETRIES = 3` |
| **Formatting** | Automated formatting is mandatory via Prettier/Ruff. | Do not waste pull request reviews discussing tabs vs. spaces. |
| **Functions** | Keep functions short (target <30 lines) and single-purpose. | Maximum 3-4 arguments per function; use an options object for more. |
| **Comments** | Explain *why*, not *what*. Code should be self-documenting. | Avoid restating what the code physically does. |

---

**Core Best Practices**

* **Types & Schema Enforcement:** Always use strict typing (TypeScript, Python type hints, Go, etc.). Avoid using dynamic fallback types like `any` unless strictly necessary and documented.
* **Error Handling & Logging:** Log errors with sufficient context (event, parameters, timestamp). Never use empty `catch` blocks or print raw sensitive user data (PII) to logs.
* **Testing Standards:**
* Every pull request modifying business logic must include unit tests.
* Target a minimum of 80% line coverage for critical domain modules.
* Integration tests are required for API endpoints and database operations.


* **Version Control & Pull Requests (PRs):**
* Keep PRs small and focused (<400 lines changed). Small PRs get reviewed faster and catch more bugs.
* PR descriptions must include *Context*, *Changes Made*, and *How to Test*.
* Require at least one peer approval before merging to the main branch.



---

**Security & Performance Checklist**

* [ ] Sanitize and validate all external user inputs before processing.
* [ ] Never hardcode secrets, API keys, or database credentials (use environment variables).
* [ ] Avoid N+1 database queries; use batching or eager loading where applicable.
* [ ] Ensure proper resource cleanup (close database connections, file handles, and stream streams).
