# Configuration Enhancement Specification

## Objective
Move more thresholds and configurable parameters to environment variables and/or a centralized configuration file to improve flexibility and ease of deployment across different environments.

## Current State
- Some thresholds are already in `backend/config.py` (e.g., `CONFIDENCE_HIGH`, `CONFIDENCE_MEDIUM`, `AUTO_APPROVE_MAX_AMOUNT`).
- However, other thresholds and parameters are hardcoded in various modules (e.g., retry limits in workflow engine, noise levels in experiments, etc.).

## Proposed Changes
1. Centralize all configurable parameters in `backend/config.py` using Pydantic Settings.
2. Use environment variables to override defaults, with sensible defaults for local development and testing.
3. Examples of parameters to move:
   - Retry limits (currently in `settings.MAX_RETRIES` but used in `WorkflowEngine._execute_actions_with_retry` and elsewhere)
   - Noise levels for robustness testing (currently hardcoded in `experiments/test_robustness.py`)
   - Thresholds for the hybrid decision engine (already partially done, but ensure all are in config)
   - Any other hardcoded values that might need tuning (e.g., batch sizes, timeouts, feature flags).

## Implementation Plan
1. Review the codebase for hardcoded values that could be made configurable.
2. Add new fields to the `Settings` class in `backend/config.py`.
3. Update the code to use these new settings instead of hardcoded values.
4. Update `.env.example` to reflect new environment variables.
5. Ensure that the configuration is loaded and validated at startup.

## Files to Modify
- `backend/config.py`: Add new configuration fields.
- `.env.example`: Add new environment variable examples.
- Various files in `backend/` and `experiments/` where hardcoded values are replaced by config values.

## Validation
- After changes, run the existing test suite to ensure nothing breaks.
- Test that environment variables can override the defaults.
- Verify that the application starts correctly with the new configuration.

## References
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)