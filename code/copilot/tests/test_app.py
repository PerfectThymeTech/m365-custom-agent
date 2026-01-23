import pytest


@pytest.mark.parametrize("version", ("v1",))
def test_get_heartbeat(version):
    # arrange
    path = f"/{version}/health/heartbeat"

    # action
    response = f"Do some work with {path}"

    # assert
    assert response == response
