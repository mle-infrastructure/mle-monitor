from mle_monitor import MLEResource


def test_resource():
    # Instantiate local resource and get usage data
    resource = MLEResource(resource_name="local")
    resource_data = resource.monitor()
    assert "resource_name" in resource_data.keys()
    assert "user_data" in resource_data.keys()
    assert "host_data" in resource_data.keys()
    assert "util_data" in resource_data.keys()
    return
