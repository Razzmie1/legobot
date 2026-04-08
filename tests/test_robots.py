import pytest

from legobot.robots import VehicleAction, VehicleBase


@pytest.fixture
def vehicle():
    return VehicleBase()


def test_initial_state(vehicle):
    assert vehicle.current_action == VehicleAction.STOP
    assert vehicle.current_action_count == 0


@pytest.mark.parametrize(
    "method_name, expected_action",
    [
        ("forward", VehicleAction.FORWARD),
        ("backward", VehicleAction.BACKWARD),
        ("left", VehicleAction.LEFT),
        ("right", VehicleAction.RIGHT),
        ("space", VehicleAction.SPACE),
        ("stop", VehicleAction.STOP),
    ],
)
def test_single_action(vehicle, method_name, expected_action):
    method = getattr(vehicle, method_name)
    method()

    assert vehicle.current_action == expected_action
    assert vehicle.current_action_count == 1


def test_repeated_action(vehicle):
    vehicle.forward()
    vehicle.forward()
    assert vehicle.current_action_count == 2

    vehicle.forward()
    assert vehicle.current_action_count == 3
