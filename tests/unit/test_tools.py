from mcp_lima.tools.lifecycle import build_advanced_args, normalize_instance


def test_normalize_instance_defaults_to_default():
    assert normalize_instance(None) == "default"
    assert normalize_instance("") == "default"


def test_build_advanced_args_allowlist():
    args, ignored = build_advanced_args(
        {
            "cpus": 4,
            "memory": "8GiB",
            "mount_writable": True,
            "unknown": "x",
        }
    )
    assert "--cpus" in args
    assert "--memory" in args
    assert "--mount-writable" in args
    assert ignored == ["unknown"]
