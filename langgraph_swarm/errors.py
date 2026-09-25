"""Custom exceptions for LangGraph Swarm."""


class SwarmValidationError(Exception):
    """Raised when human feedback validation fails in HITL gates.

    This exception is used to signal validation failures when processing
    handoff payloads in human-in-the-loop workflows. It helps distinguish
    schema/validation errors from other runtime exceptions.

    Example:
        >>> if "path_validations" not in feedback:
        ...     raise SwarmValidationError("Missing path_validations key")
    """

    pass


class TaskExecutionError(Exception):
    """Raised when a worker task execution fails.

    This exception wraps worker-level failures to provide cleaner
    error handling and recovery in swarm orchestration.

    Example:
        >>> try:
        ...     result = worker.execute(task)
        ... except Exception as e:
        ...     raise TaskExecutionError(f"Worker failed: {e}") from e
    """

    pass
