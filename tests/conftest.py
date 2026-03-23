import shutil

import pytest


@pytest.fixture
def has_limactl() -> bool:
    return shutil.which("limactl") is not None
