import pytest
from pynput.keyboard import Key, KeyCode

from legobot.controller import KeyboardController
from legobot.robots import VehicleAction, VehicleBase


@pytest.fixture
def vehicle():
    return VehicleBase()


@pytest.fixture
def controller(vehicle):
    return KeyboardController(vehicle)


@pytest.mark.parametrize(
    "key, expected_action",
    [
        (KeyCode.from_char("w"), VehicleAction.FORWARD),
        (KeyCode.from_char("s"), VehicleAction.BACKWARD),
        (KeyCode.from_char("a"), VehicleAction.LEFT),
        (KeyCode.from_char("d"), VehicleAction.RIGHT),
        (Key.up, VehicleAction.FORWARD),
        (Key.down, VehicleAction.BACKWARD),
        (Key.left, VehicleAction.LEFT),
        (Key.right, VehicleAction.RIGHT),
        (Key.space, VehicleAction.SPACE),
    ],
)
def test_single_keys(controller, vehicle, key, expected_action):
    controller.on_press(key)
    assert vehicle.current_action == expected_action
    controller.on_release(key)
    assert vehicle.current_action == VehicleAction.STOP


def test_esc_key(controller, vehicle):
    controller.on_press(Key.esc)
    output = controller.on_release(Key.esc)
    assert vehicle.current_action == VehicleAction.STOP
    assert output is False


def test_unmapped_key(controller, vehicle):
    controller.on_press(KeyCode.from_char("x"))
    assert vehicle.current_action == VehicleAction.STOP

    controller.on_release(KeyCode.from_char("x"))
    assert vehicle.current_action == VehicleAction.STOP


def test_multiple_keys(controller, vehicle):
    controller.on_press(Key.up)
    controller.on_press(Key.left)
    assert vehicle.current_action == VehicleAction.LEFT

    controller.on_press(Key.right)
    assert vehicle.current_action == VehicleAction.RIGHT

    controller.on_release(Key.left)
    assert vehicle.current_action == VehicleAction.RIGHT
    assert vehicle.current_action_count == 1

    controller.on_release(Key.right)
    assert vehicle.current_action == VehicleAction.FORWARD


def test_key_repeat(controller, vehicle):
    controller.on_press(Key.up)
    controller.on_press(Key.up)
    assert vehicle.current_action == VehicleAction.FORWARD
    assert vehicle.current_action_count == 1


def test_equal_actions(controller, vehicle):
    controller.on_press(Key.up)
    controller.on_press(KeyCode.from_char("w"))
    assert vehicle.current_action == VehicleAction.FORWARD
    assert vehicle.current_action_count == 1

    controller.on_release(Key.up)
    assert vehicle.current_action == VehicleAction.FORWARD
    assert vehicle.current_action_count == 1
