import unittest

import ljjoy


class TestVJoy:

    def __init__(self):
        self.buttons_set = []
        self.axes_set = []

    def setAxis(self, input, value):
        self.axes_set.append({'input': input, 'value': value})

    def setButton(self, input, value):
        self.buttons_set.append({'input': input, 'value': value})


class LJJoyTests(unittest.TestCase):

    def test_binary_output_strategy (self):
        spec = {
            'activateThreshold': 0.5,
            'inactiveValue': 1,
            'activeValue': 10
        }
        test_strategy = ljjoy.BinaryOutputStrategy(spec)
        self.assertEqual(test_strategy.process(0.1), 1)
        self.assertEqual(test_strategy.process(0.7), 10)

    def test_linear_output_strategy (self):
        spec = {
            'minDeviceVal': 1,
            'maxDeviceVal': 2,
            'minJoystickVal': 10,
            'maxJoystickVal': 14
        }
        test_strategy = ljjoy.LinearOutputStrategy(spec)
        self.assertEqual(test_strategy.process(1.5), 12)

    def test_input_mapping (self):
        spec = {
            'activateThreshold': 0.5,
            'inactiveValue': 1,
            'activeValue': 10
        }
        test_strategy = ljjoy.BinaryOutputStrategy(spec)
        test_vjoy = TestVJoy()

        mapping = ljjoy.InputMapping('AIN0', 'axis:0')
        mapping.run_mapping(test_vjoy, 0.1)
        mapping.run_mapping(test_vjoy, 0.7)

        self.assertEqual(len(test_vjoy.buttons_set), 0)
        self.assertEqual(len(test_vjoy.axes_set), 2)
        self.assertEqual(test_vjoy.axes_set[0], {'input': 0, 'value': 0})
        self.assertEqual(test_vjoy.axes_set[1], {'input': 0, 'value': 1})

    def test_try_parse_int_success (self):
        self.assertEqual(ljjoy.try_parse_int('1', '%s was unexpected'), 1)

    def test_try_parse_int_fail (self):
        with self.assertRaises(ValueError):
            ljjoy.try_parse_int('a', '%s was unexpected')

    def test_require_spec_attr (self):
        ljjoy.require_spec_attr({'a': 1}, 'a')
        with self.assertRaises(ValueError):
            ljjoy.require_spec_attr({'a': 1}, 'b')

    def test_create_mapping (self):
        test_spec = {
            'deviceRegister': 'AIN0',
            'outputStrategy': {
                'maxDeviceVal': 5,
                'maxJoystickVal': 2147483647,
                'minDeviceVal': 0,
                'minJoystickVal': 0,
                'name': 'linear'
            },
            'joystickOutputChannel': 'axis:0'
        }
        mapping = ljjoy.create_mapping(test_spec)

        self.assertEqual(mapping.device_register, 'AIN0')
        self.assertEqual(mapping.joystick_output_type, 'axis')
        self.assertEqual(mapping.joystick_output_num, 0)
        self.assertTrue(
            isinstance(mapping.output_strategy, ljjoy.LinearOutputStrategy)
        )

    def test_get_mappings_by_device_register (self):
        mappings = [
            ljjoy.InputMapping('AIN0', 'axis:0'),
            ljjoy.InputMapping('AIN1', 'axis:1')
        ]
        organized_mappings = ljjoy.get_mappings_by_device_register(mappings)
        self.assertEqual(organized_mappings['AIN0'], mappings[0])
        self.assertEqual(organized_mappings['AIN1'], mappings[1])


if __name__ == '__main__':
    unittest.main()
