from mle_monitor import MLEProtocol, MLEResource, MLEDashboard


def test_dashboard():
    # Test data collection and layout generation
    resource = MLEResource(resource_name="local")
    protocol = MLEProtocol(protocol_fname="mle_protocol.db")
    dashboard = MLEDashboard(protocol, resource)
    dashboard.snapshot()
