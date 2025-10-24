# FastAPI Development Standards

## Mandatory Patterns

### 1. Security (Non-Negotiable)

**ALL endpoints MUST:**
- Use `@require_session` decorator from `libs/auth/decorators.py`
- Never parse raw headers (`Authorization`, `Cookie`, etc.) in handlers
- Never log request bodies, auth tokens, or PII (name, email, phone, address)

```python
from libs.auth.decorators import require_session, SessionContext

@router.post("/tasks")
@require_session  # REQUIRED - validates session, rate limits, audit logs
async def create_task(session: SessionContext):
    # session.user_id, session.roles available here
    pass
```

**External calls MUST:**
- Use `httpx.AsyncClient` with timeout (default: 10s, max: 30s)
- Never construct URLs from unvalidated user input
- Validate TLS certificates (no `verify=False`)

### 2. Typed I/O Only

**ALL handlers MUST:**
- Accept Pydantic `BaseModel` for request bodies
- Declare `response_model=` with a Pydantic model
- Use `Field(...)` constraints (`min_length`, `max_length`, `ge`, `le`)
- No `dict[str, Any]`, `**kwargs`, or untyped returns

```python
class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: str = Field(max_length=2000)

@router.post("/tasks", response_model=CreateTaskResponse)
@require_session
async def create_task(request: CreateTaskRequest, session: SessionContext):
    pass
```

### 3. Observability (Structured Logging)

**USE:** `libs/observability/logger.py` (never `print`, `logging`, or `structlog` directly)

```python
from libs.observability.logger import get_logger

logger = get_logger(__name__)

# REQUIRED fields in every endpoint log:
logger.info(
    "endpoint_executed",
    route="/tasks",           # endpoint path
    method="POST",            # HTTP method
    status=201,               # HTTP status
    latency_ms=45.3,          # request latency
    user_id=session.user_id,  # from session (null for public endpoints)
)
```

**ERROR logging MUST include:**
- `error_type` (exception class name)
- `route`, `method`, `status`
- `user_id` (if available)
- Never log stack traces of business exceptions (only infra errors)

### 4. Dependency Injection Pattern

**Repository/Service injection:**
```python
from libs.domain.ports.task_repository import TaskRepository

def get_task_repository() -> TaskRepository:
    return PostgresTaskRepository(pool=get_db_pool())

@router.post("/tasks")
@require_session
async def create_task(
    request: CreateTaskRequest,
    session: SessionContext,
    task_repo: TaskRepository = Depends(get_task_repository),
):
    pass
```

### 5. Error Handling Contract

**Never expose internal errors to clients:**
```python
try:
    result = await task_repo.create_task(...)
except TaskRepository.RecordNotFound:
    raise HTTPException(status_code=404, detail="Task not found")
except Exception as exc:
    logger.error(
        "task_creation_failed",
        route="/tasks",
        method="POST",
        status=500,
        user_id=session.user_id,
        error_type=type(exc).__name__,
    )
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 6. Testing Requirements

**Every endpoint MUST have:**
1. **Contract test**: validates request/response schema against OpenAPI spec
2. **Auth test**: confirms `@require_session` blocks unauthenticated requests
3. **Happy path test**: valid input → expected output
4. **Validation test**: invalid input → 422 with field errors
5. **Error case test**: repository failure → 500 without leaking details

Example:
```python
async def test_create_task_requires_auth(client: TestClient):
    """MUST fail without valid session."""
    response = await client.post("/tasks", json={"title": "Test"})
    assert response.status_code == 401

async def test_create_task_validates_input(client: TestClient, mock_session):
    """MUST reject invalid field lengths."""
    response = await client.post(
        "/tasks",
        json={"title": "", "description": "x" * 3000},
        headers=mock_session.headers,
    )
    assert response.status_code == 422
    assert "title" in response.json()["detail"][0]["loc"]
```

## Security Baseline Checklist

Before submitting code, verify:
- Uses `@require_session` decorator (no raw auth headers)
- No secrets/tokens/PII in logs
- External HTTP calls have timeouts (<= 30s)
- All inputs validated via Pydantic with Field constraints
- Errors return generic messages (never internal exception text)
- Uses `libs/observability/logger.get_logger()` (not print/logging)

## Diff Discipline

When proposing code changes:
1. **Minimal diff**: only change what's needed to fix the issue
2. **Rationale**: explain *why* in PR description
3. **Failing test**: include test that fails before your change, passes after
4. **Rule reference**: cite which rule(s) your change enforces

## Examples of What NOT to Do

❌ Parsing auth headers manually:
```python
token = request.headers.get("Authorization")  # NEVER DO THIS
```

❌ Unvalidated input:
```python
def create_task(data: dict):  # Missing Pydantic validation
```

❌ Logging PII:
```python
logger.info("Creating task", user_email=user.email)  # PII leak
```

❌ No timeout on external calls:
```python
await httpx.get(url)  # Missing timeout - can hang forever
```

❌ Generic exception handling exposing internals:
```python
except Exception as e:
    return {"error": str(e)}  # Leaks implementation details
```

## When in Doubt

If a pattern/API is not in the codebase or these rules:
1. Mark with `# TODO: verify pattern for {X}` 
2. Ask in PR review
3. Never guess or use deprecated patterns

