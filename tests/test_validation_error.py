"""Tests for SwarmValidationError and TaskExecutionError exceptions."""

import pytest

from langgraph_swarm.errors import SwarmValidationError, TaskExecutionError


class TestSwarmValidationError:
    """Tests for SwarmValidationError exception."""

    def test_swarm_validation_error_raises(self):
        """Test that SwarmValidationError can be raised and caught."""
        with pytest.raises(SwarmValidationError):
            raise SwarmValidationError("Invalid feedback structure")

    def test_swarm_validation_error_message(self):
        """Test that error message is preserved."""
        error = SwarmValidationError("Missing path_validations key")
        assert "path_validations" in str(error)

    def test_swarm_validation_error_inheritance(self):
        """Test that SwarmValidationError inherits from Exception."""
        error = SwarmValidationError("test")
        assert isinstance(error, Exception)

    def test_swarm_validation_error_with_cause(self):
        """Test exception chaining works correctly."""
        original = ValueError("bad value")
        try:
            raise SwarmValidationError("Validation failed") from original
        except SwarmValidationError as e:
            assert e.__cause__ is original


class TestTaskExecutionError:
    """Tests for TaskExecutionError exception."""

    def test_task_execution_error_raises(self):
        """Test that TaskExecutionError can be raised and caught."""
        with pytest.raises(TaskExecutionError):
            raise TaskExecutionError("Worker failed")

    def test_task_execution_error_message(self):
        """Test that error message is preserved."""
        error = TaskExecutionError("Task timeout after 30s")
        assert "timeout" in str(error)

    def test_task_execution_error_inheritance(self):
        """Test that TaskExecutionError inherits from Exception."""
        error = TaskExecutionError("test")
        assert isinstance(error, Exception)


class TestErrorImports:
    """Test that errors are importable from main package."""

    def test_import_from_package(self):
        """Test errors can be imported from langgraph_swarm."""
        from langgraph_swarm import SwarmValidationError, TaskExecutionError

        assert SwarmValidationError is not None
        assert TaskExecutionError is not None
