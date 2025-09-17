import logging
import time

import pytest

from core.profiling import log_execution_time

def test_execution_time(caplog: pytest.LogCaptureFixture,monkeypatch: pytest.MonkeyPatch):
    with caplog.at_level(logging.INFO):
        with log_execution_time("Test Stage"):
            time.sleep(0.5)
            
    # Assert
    assert f'[PROFILE] ==> Entering stage: Test Stage' in caplog.text
    assert f'[PROFILE] <== Exiting stage: Test Stage' in caplog.text
    assert f'Duration' in caplog.text
    assert len(caplog.records) == 2
