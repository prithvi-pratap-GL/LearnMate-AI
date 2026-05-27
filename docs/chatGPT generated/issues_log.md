# LearnMate AI - Issues Log

This document tracks the currently identified issues, risks, architectural concerns, and technical debt within the LearnMate AI system.

---

# Issue Classification

Issues are grouped into:

- Architecture Issues
- Security Issues
- Reliability Issues
- Product Limitations
- DevOps / Deployment Issues
- Code Quality Concerns

---

# Architecture Issues

---

## Issue 1: Multiple Backend Entrypoints

### Files

```text
start.py
run_server.py
minimal_server.py
```

### Problem

The project contains multiple backend startup files.

This creates:

- Confusing execution paths
- Deployment ambiguity
- Maintenance overhead
- Inconsistent startup behavior

Developers may not know which entrypoint is officially supported.

### Impact

Medium

### Recommendation

Standardize on a single backend entrypoint.

Recommended:

```text
start.py
```

Deprecate or remove unused alternatives.

---

## Issue 2: Port Configuration Inconsistency

### Observed

Different server files use different ports.

Examples:

```text
8000
5000
```

### Problem

Port inconsistency causes:

- Developer confusion
- Startup errors
- Deployment mismatch
- Documentation drift

### Impact

Low to Medium

### Recommendation

Use centralized configuration.

Example:

```env
PORT=8000
```

Load through settings configuration.

---

## Issue 3: Broken `minimal_server.py`

### Problem

Observed issues include:

- Missing imports
- Incorrect service references
- Undefined functions
- Runtime instability

Example:

- Missing explanation generation references
- Incorrect roadmap service usage

### Impact

Medium

### Recommendation

Either:

- Repair the file
- Or remove it completely

Avoid retaining dead or partially functional server code.

---

# Security Issues

---

## Issue 4: Wildcard CORS Configuration

### Location

Backend CORS middleware.

Observed:

```python
allow_origins=["*"]
```

### Problem

Wildcard CORS permits requests from all origins.

This is unsafe in production.

### Risks

Potential:

- Unauthorized frontend access
- Cross-origin abuse
- Expanded attack surface

### Impact

High

### Recommendation

Restrict allowed origins.

Example:

```python
allow_origins=[
    "http://localhost:5173",
    "https://yourdomain.com"
]
```

---

## Issue 5: Unsafe HTML Rendering

### Location

Frontend rendering logic.

Observed:

```jsx
dangerouslySetInnerHTML
```

### Problem

LLM-generated output is rendered without sanitization.

This introduces potential:

- XSS vulnerabilities
- Script injection
- Unsafe HTML rendering

### Impact

High

### Recommendation

Sanitize HTML before rendering.

Recommended:

- DOMPurify
- Markdown rendering with sanitization

---

# Reliability Issues

---

## Issue 6: Fragile LLM JSON Parsing

### Location

Question generation pipeline.

### Problem

Question extraction depends on:

- String parsing
- Manual JSON detection
- Assumed LLM formatting

LLM outputs are probabilistic.

Formatting changes may break parsing.

### Risks

Potential:

- Invalid JSON
- Empty responses
- Runtime failures
- Broken assessments

### Impact

High

### Recommendation

Use:

- Structured prompting
- JSON schema validation
- Retry and repair mechanisms

Prefer deterministic parsing.

---

## Issue 7: Evaluation Parsing Fragility

### Location

Evaluation logic.

Observed logic:

```python
rfind("{")
rfind("}")
```

### Problem

The system attempts to locate JSON through substring extraction.

This is brittle.

Minor LLM formatting deviations may break evaluation.

### Impact

High

### Recommendation

Replace with:

- JSON validation
- Pydantic parsing
- Schema enforcement

---

## Issue 8: Missing API Key Validation

### Expected

```env
HUGGING_FACE_API_KEY
```

### Problem

Startup behavior may fail if key is missing.

Observed handling is limited.

### Risks

- Runtime crashes
- API failures
- Poor developer experience

### Impact

Medium

### Recommendation

Add startup validation.

Example:

```python
if not api_key:
    raise RuntimeError(...)
```

Fail early.

---

# Product Limitations

---

## Issue 9: No Database Layer

### Problem

System currently lacks:

- Database
- Persistent storage
- User history
- Attempt tracking

All learning sessions are temporary.

### Impact

High

### Consequences

Cannot support:

- Progress history
- Analytics
- User accounts
- Long-term learning

### Recommendation

Introduce persistence.

Options:

- PostgreSQL
- MongoDB
- Supabase

---

## Issue 10: No Authentication System

### Problem

No:

- Login
- Sessions
- Authorization
- Identity management

### Impact

Medium to High

### Consequences

Cannot:

- Personalize users
- Save history
- Secure learning data

### Recommendation

Add:

- JWT authentication
- OAuth
- Session handling

---

## Issue 11: No Frontend Environment Configuration

### Problem

Frontend API URL appears hardcoded.

Observed:

```text
localhost:8000
```

### Risks

Hardcoded URLs create:

- Environment mismatch
- Deployment difficulty
- Manual code edits

### Impact

Medium

### Recommendation

Use:

```env
VITE_API_BASE_URL=
```

Example:

```js
import.meta.env.VITE_API_BASE_URL
```

---

# DevOps / Deployment Issues

---

## Issue 12: No Docker Support

### Problem

No:

- Dockerfile
- Docker Compose
- Containerization strategy

### Impact

Medium

### Consequences

Deployment becomes:

- Manual
- Inconsistent
- Environment-dependent

### Recommendation

Add:

```text
Dockerfile
docker-compose.yml
```

---

## Issue 13: No CI/CD Pipeline

### Problem

No automated:

- Build checks
- Tests
- Deployments
- Quality gates

### Impact

Medium

### Recommendation

Add CI/CD.

Possible:

- GitHub Actions
- GitLab CI
- Jenkins

Suggested pipeline:

```text
Lint
→ Test
→ Build
→ Deploy
```

---

## Issue 14: Limited Testing

### Problem

Test coverage appears minimal.

Heavy reliance on manual validation.

### Risks

Potential:

- Regression bugs
- Deployment instability
- Hidden failures

### Impact

Medium

### Recommendation

Add:

Backend:

- pytest

Frontend:

- Vitest
- React Testing Library

---

# Code Quality Concerns

---

## Issue 15: Documentation Drift

### Problem

Existing documentation does not fully match implementation.

Observed mismatch:

- Startup instructions
- Server paths
- Architecture details

### Impact

Low to Medium

### Recommendation

Treat documentation as versioned system knowledge.

Update alongside code changes.

---

## Issue 16: Heavy AI Dependency

### Problem

Core workflow depends entirely on external AI responses.

Failure scenarios:

- API outage
- Rate limits
- Model changes
- Latency spikes

### Impact

Medium

### Recommendation

Add:

- Retry handling
- Fallback responses
- Timeout handling
- Monitoring

---

# Technical Debt Summary

Current technical debt areas:

| Area | Severity |
|------|----------|
| CORS Security | High |
| HTML Sanitization | High |
| JSON Parsing | High |
| No Persistence | High |
| Multiple Entrypoints | Medium |
| No Auth | Medium |
| No CI/CD | Medium |
| No Docker | Medium |
| Limited Tests | Medium |

---

# Summary

LearnMate AI has a solid modular foundation but remains an early-stage system.

Primary improvement priorities:

1. Stabilize backend architecture
2. Harden AI parsing
3. Improve security
4. Introduce persistence
5. Add deployment and testing workflows

This document should be updated whenever issues are identified or resolved.