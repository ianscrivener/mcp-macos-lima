import subprocess

import pytest


@pytest.mark.integration
def test_limactl_is_available_for_integration():
    proc = subprocess.run(["limactl", "--help"], capture_output=True, text=True, check=False)
    assert proc.returncode == 0
