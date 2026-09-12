# Security Enhancement Specification

## Objective
Implement authentication, authorization, and input validation to secure the API and protect against common vulnerabilities.

## Current State
- The API is currently open (no authentication) and uses CORS with `allow_origins=["*"]`.
- Input validation is done via Pydantic models in some places, but not consistently.
- There is no protection against common web vulnerabilities (e.g., SQL injection, XSS, CSRF) beyond what FastAPI and SQLAlchemy provide by default.

## Proposed Changes
1. **Authentication**:
   - Implement API key or JWT-based authentication for accessing the API endpoints.
   - Consider different levels of access (e.g., read-only for metrics, submit for jobs, approve for human tasks).

2. **Authorization**:
   - Implement role-based access control (RBAC) or attribute-based access control (ABAC) to restrict what users can do.
   - For example, only allow users with the "approver" role to access the human approval queue endpoints.

3. **Input Validation**:
   - Ensure all input is validated using Pydantic models (already in use for some endpoints, but extend to all).
   - Use FastAPI's built-in validation and add custom validators where necessary.

4. **Protection Against Common Vulnerabilities**:
   - **SQL Injection**: Already mitigated by using SQLAlchemy ORM (if used correctly) or parameterized queries.
   - **XSS**: The frontend is served as static files and the API returns JSON, so the risk is low. However, ensure that any user-generated content displayed in the frontend is properly escaped.
   - **CSRF**: If we implement session-based authentication, we need CSRF protection. For token-based authentication (e.g., JWT in headers), CSRF is not a concern.
   - **Rate Limiting**: Implement rate limiting to prevent abuse of the API.

5. **Secure Configuration**:
   - Ensure that sensitive information (like database passwords, secret keys) is not hardcoded and is managed via environment variables or a secrets manager.
   - Use HTTPS in production (already handled by Netlify for the frontend, but the backend should also use HTTPS if exposed).

## Implementation Plan
1. **Authentication**:
   - Choose an authentication method (e.g., API keys for simplicity, or JWT for more flexibility).
   - Create an authentication module (`backend/auth.py`) that handles token creation and verification.
   - Add a dependency in FastAPI (`Depends`) to protect endpoints.

2. **Authorization**:
   - Define roles and permissions.
   - Create a function to check the user's role and permissions for each endpoint.

3. **Input Validation**:
   - Review all API endpoints and ensure they have Pydantic models for input validation.
   - Add validation for any missing endpoints (e.g., the job submission endpoint).

4. **Rate Limiting**:
   - Use a package like `slowapi` or `fastapi-limiter` to add rate limiting to the API.

5. **Security Headers**:
   - Add middleware to set security headers (e.g., Content Security Policy, X-Frame-Options, etc.).

6. **Secrets Management**:
   - Update `.env.example` to include new environment variables for secrets (e.g., `SECRET_KEY`, `API_KEYS`, `DATABASE_URL` with password).
   - Ensure that the application reads these from the environment and does not commit them to version control.

## Files to Modify
- `backend/auth.py`: New file for authentication logic.
- `backend/main.py`: Add authentication middleware and dependencies to routes.
- `backend/config.py`: Add new configuration fields for security (e.g., secret key, algorithm, rate limit settings).
- `requirements.txt`: Add new dependencies (e.g., `python-jose` for JWT, `passlib` for hashing, `slowapi` for rate limiting).
- `.env.example`: Add new environment variables for secrets and security settings.
- `backend/database.py`: If we add tables for users, API keys, etc.
- `backend/models/db_models.py`: Add new database models for authentication and authorization.
- `frontend/index.html` and `frontend/app.js`: Update to send authentication tokens with requests (if we implement auth for the frontend).

## Validation
- Write unit tests for the authentication and authorization logic.
- Test that protected endpoints are inaccessible without valid credentials.
- Test that rate limiting works as expected.
- Perform a security review (or use a tool like Bandit) to check for common vulnerabilities.
- Test the frontend to ensure it works with the new authentication mechanism.

## References
- [FastAPI Security Guide](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [SlowAPI for Rate Limiting](https://slowapi.readthedocs.io/)