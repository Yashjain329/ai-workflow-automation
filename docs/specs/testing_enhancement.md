# Testing Enhancement Specification

## Objective
Improve the test suite by adding more integration and end-to-end tests, as well as performance benchmarks, to ensure the system works correctly as a whole and meets performance requirements.

## Current State
- The project has 18 unit tests covering:
  - API endpoints
  - Failure scenarios
  - ML classifier
  - Reliability and robustness (idempotency, retries, failure handling)
  - State machine
  - Policy unit tests
- There are no explicit integration or end-to-end tests that test the full workflow from job submission to completion.
- Performance benchmarks exist in the `experiments/` directory (e.g., `run_benchmark.py`, `compare_baselines.py`, `test_robustness.py`), but they are not integrated into the test suite and are more for research evaluation.

## Proposed Changes
1. **Integration Tests**:
   - Add tests that test the interaction between multiple components (e.g., API -> workflow engine -> database -> connectors).
   - Example: Submit a job via the API and verify that it goes through all states and ends up in the correct final state.

2. **End-to-End (E2E) Tests**:
   - Use a tool like `pytest` with `requests` to test the full HTTP API, or use a browser automation tool (e.g., Playwright, Selenium) to test the frontend interacting with the backend.
   - Since the frontend is simple, we can start with API-based E2E tests.

3. **Performance Benchmarks as Tests**:
   - Integrate the existing benchmark scripts into the test suite as performance tests that can be run separately (e.g., with `pytest` and a custom marker).
   - Set baseline performance metrics and fail tests if performance degrades beyond a threshold.

4. **Test Coverage**:
   - Aim to increase test coverage, especially for the workflow engine and connectors.
   - Use coverage tools (e.g., `pytest-cov`) to identify untested code.

5. **Test Data Management**:
   - Use fixtures to set up consistent test data (e.g., temporary databases, mock external services).
   - Consider using factories or model-bakery for creating test objects.

## Implementation Plan
1. **Set Up Testing Infrastructure**:
   - Add `pytest-cov` to `requirements.txt` for coverage reporting.
   - Consider adding `responses` or `requests-mock` for mocking external HTTP calls in tests.
   - For E2E testing of the frontend, consider adding `playwright` or `selenium` (but note that this may require additional setup).

2. **Create Integration Tests**:
   - Create a new test module, e.g., `tests/test_integration.py`.
   - Write tests that:
     - Start with a clean database (use fixtures to drop and create tables).
     - Submit a job via the API endpoint.
     - Poll for the job status or use a callback to verify the job progression.
     - Verify the final state, database records, and any side effects (e.g., notifications sent).

3. **Create End-to-End Tests**:
   - Create a new test module, e.g., `tests/test_e2e.py`.
   - Write tests that simulate a user submitting a job via the frontend (by sending HTTP requests to the backend as the frontend would) and verifying the outcome in the UI (by checking the dashboard API or directly the database).

4. **Integrate Performance Benchmarks**:
   - Modify the existing benchmark scripts to be callable as functions that return metrics.
   - Create a new test module, e.g., `tests/test_performance.py`, that runs these benchmarks and asserts that metrics are within acceptable bounds.
   - Use `pytest` markers to allow running performance tests separately (e.g., `pytest -m performance`).

5. **Improve Test Coverage**:
   - Run `pytest --cov=backend` to see current coverage.
   - Identify missing tests and add them, focusing on complex logic in the workflow engine, policy rules, and connectors.

6. **Continuous Integration**:
   - If using CI (e.g., GitHub Actions), ensure that the test suite runs on every push and that performance tests are run on a schedule or for release branches.

## Files to Modify
- `requirements.txt`: Add `pytest-cov`, `responses` (or similar), and any E2E testing tools.
- `tests/test_integration.py`: New file for integration tests.
- `tests/test_e2e.py`: New file for end-to-end tests.
- `tests/test_performance.py`: New file for performance tests.
- Update existing benchmark scripts in `experiments/` to be importable and to return metrics (if not already).
- Optionally, update `conftest.py` to share fixtures (e.g., for a temporary database).

## Validation
- Run the new tests to ensure they pass.
- Verify that the test suite still passes with the new additions.
- Check coverage reports to see improvement.
- Ensure that performance tests are not flaky and that they provide useful feedback.

## References
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Responses: A utility for mocking out the `requests` Python library](https://pypi.org/project/responses/)
- [Playwright for Python](https://playwright.dev/python/)