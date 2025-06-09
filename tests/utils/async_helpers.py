"""Async testing utilities and helpers."""

import asyncio
import functools
import pytest
import time
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any, List, Optional, TypeVar, Union
from unittest.mock import AsyncMock, Mock, patch

T = TypeVar("T")


class AsyncTestHelper:
    """Helper utilities for async testing."""

    @staticmethod
    async def run_with_timeout(coro, timeout: float = 5.0, timeout_message: str = "Async operation timed out"):
        """Run an async operation with a timeout.

        Args:
            coro: Coroutine to run
            timeout: Timeout in seconds
            timeout_message: Message for timeout error

        Returns:
            Result of the coroutine

        Raises:
            asyncio.TimeoutError: If operation times out
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except TimeoutError:
            raise TimeoutError(timeout_message)

    @staticmethod
    async def gather_with_errors(*coros, return_exceptions: bool = True) -> list[Any | Exception]:
        """Gather multiple coroutines, capturing exceptions.

        Args:
            *coros: Coroutines to run
            return_exceptions: If True, exceptions are returned as values

        Returns:
            List of results or exceptions
        """
        return await asyncio.gather(*coros, return_exceptions=return_exceptions)

    @staticmethod
    async def retry_async(
        func: Callable, max_attempts: int = 3, delay: float = 0.1, backoff: float = 2.0, exceptions: tuple = (Exception,)
    ):
        """Retry an async function with exponential backoff.

        Args:
            func: Async function to retry
            max_attempts: Maximum number of attempts
            delay: Initial delay between attempts
            backoff: Backoff multiplier
            exceptions: Tuple of exceptions to catch

        Returns:
            Result of the function

        Raises:
            Last exception if all attempts fail
        """
        last_exception = None
        current_delay = delay

        for attempt in range(max_attempts):
            try:
                return await func()
            except exceptions as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        raise last_exception  # type: ignore[misc]

    @staticmethod
    @asynccontextmanager
    async def async_timeout(seconds: float):
        """Async context manager for timeout operations.

        Usage:
            async with async_timeout(5.0):
                await some_long_operation()
        """
        task = asyncio.current_task()

        def timeout_callback():
            if task and not task.done():
                task.cancel()

        loop = asyncio.get_event_loop()
        handle = loop.call_later(seconds, timeout_callback)

        try:
            yield
        finally:
            handle.cancel()

    @staticmethod
    async def wait_for_condition(
        condition_func: Callable[[], bool],
        timeout: float = 5.0,
        poll_interval: float = 0.1,
        timeout_message: str = "Condition not met within timeout",
    ):
        """Wait for a condition to become true.

        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum time to wait
            poll_interval: Time between condition checks
            timeout_message: Message for timeout error

        Raises:
            asyncio.TimeoutError: If condition not met within timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if condition_func():
                return
            await asyncio.sleep(poll_interval)

        raise TimeoutError(timeout_message)

    @staticmethod
    async def async_map(func: Callable[[T], Any], items: list[T], concurrency: int | None = None) -> list[Any]:
        """Apply an async function to items with optional concurrency limit.

        Args:
            func: Async function to apply
            items: List of items to process
            concurrency: Maximum concurrent operations (None for unlimited)

        Returns:
            List of results in the same order as inputs
        """
        if concurrency is None:
            # No limit, run all concurrently
            return await asyncio.gather(*[func(item) for item in items])

        # Limited concurrency using semaphore
        semaphore = asyncio.Semaphore(concurrency)

        async def limited_func(item):
            async with semaphore:
                return await func(item)

        return await asyncio.gather(*[limited_func(item) for item in items])


class AsyncMockFactory:
    """Factory for creating async mocks."""

    @staticmethod
    def create_async_mock(return_value: Any = None, side_effect: Any = None, **kwargs) -> AsyncMock:
        """Create an AsyncMock with common configurations.

        Args:
            return_value: Value to return when called
            side_effect: Side effect or exception to raise
            **kwargs: Additional mock attributes

        Returns:
            Configured AsyncMock
        """
        mock = AsyncMock(**kwargs)

        if return_value is not None:
            mock.return_value = return_value

        if side_effect is not None:
            mock.side_effect = side_effect

        return mock

    @staticmethod
    def create_async_iterator_mock(values: list[Any]) -> AsyncMock:
        """Create a mock that returns an async iterator.

        Args:
            values: Values to yield

        Returns:
            AsyncMock that yields values
        """

        async def async_gen():
            for value in values:
                yield value

        mock = AsyncMock()
        mock.return_value = async_gen()
        return mock

    @staticmethod
    def create_async_context_manager_mock(enter_value: Any = None, exit_value: Any = None) -> AsyncMock:
        """Create a mock async context manager.

        Args:
            enter_value: Value to return from __aenter__
            exit_value: Value to return from __aexit__

        Returns:
            AsyncMock context manager
        """
        mock = AsyncMock()
        mock.__aenter__ = AsyncMock(return_value=enter_value)
        mock.__aexit__ = AsyncMock(return_value=exit_value)
        return mock


def async_test(timeout: float = 10.0):
    """Decorator for async tests with timeout.

    Usage:
        @async_test(timeout=5.0)
        async def test_something():
            await some_async_operation()
    """

    def decorator(test_func):
        @functools.wraps(test_func)
        @pytest.mark.asyncio
        async def wrapper(*args, **kwargs):
            return await AsyncTestHelper.run_with_timeout(
                test_func(*args, **kwargs),
                timeout=timeout,
                timeout_message=f"Test {test_func.__name__} timed out after {timeout}s",
            )

        return wrapper

    return decorator


def mock_async_property(obj: Any, property_name: str, return_value: Any):
    """Mock an async property.

    Args:
        obj: Object with the property
        property_name: Name of the property to mock
        return_value: Value to return

    Returns:
        Mock object
    """

    async def async_getter():
        return return_value

    prop_mock = property(lambda self: async_getter())
    return patch.object(type(obj), property_name, prop_mock)


class AsyncTestCase:
    """Base class for async test cases with helper methods."""

    async def assert_async_raises(self, exception_class: type, coro, message_pattern: str | None = None):
        """Assert that an async operation raises an exception.

        Args:
            exception_class: Expected exception class
            coro: Coroutine to execute
            message_pattern: Optional pattern to match in exception message
        """
        with pytest.raises(exception_class) as exc_info:  # type: ignore[var-annotated]
            await coro

        if message_pattern:
            assert message_pattern in str(exc_info.value)

    async def assert_completes_within(self, coro, seconds: float, message: str = "Operation took too long"):
        """Assert that an async operation completes within a time limit.

        Args:
            coro: Coroutine to execute
            seconds: Maximum allowed time
            message: Error message if timeout

        Returns:
            Result of the coroutine
        """
        start_time = time.time()
        result = await AsyncTestHelper.run_with_timeout(coro, timeout=seconds)
        elapsed = time.time() - start_time

        assert elapsed < seconds, f"{message}: took {elapsed:.2f}s"
        return result

    @staticmethod
    async def wait_and_assert(condition_func: Callable[[], bool], timeout: float = 1.0, message: str = "Condition not met"):
        """Wait for a condition and assert it becomes true.

        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum time to wait
            message: Assertion error message
        """
        try:
            await AsyncTestHelper.wait_for_condition(condition_func, timeout=timeout)
        except TimeoutError:
            pytest.fail(message)


# Async test fixtures
@pytest.fixture
async def async_client():
    """Create an async HTTP client mock."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    client.close = AsyncMock()

    # Mock context manager behavior
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    return client


@pytest.fixture
async def async_db_connection():
    """Create an async database connection mock."""
    conn = AsyncMock()
    conn.execute = AsyncMock()
    conn.fetch = AsyncMock(return_value=[])
    conn.fetchone = AsyncMock(return_value=None)
    conn.close = AsyncMock()

    # Mock context manager behavior
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=None)

    return conn


@pytest.fixture
def async_sleep_mock():
    """Mock asyncio.sleep for faster tests."""
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        yield mock_sleep
