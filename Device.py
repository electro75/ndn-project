import random


class Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.sensors = {f"sensor_{i}": 0 for i in range(1, 9)}
        self.actuator = Actuator()

    def generate_sensor_values(self):
        for sensor in self.sensors:
            # Simulating sensor data generation (replace with actual sensor logic)
            self.sensors[sensor] = random.uniform(0, 100)

    def emit_sensor_values(self):
        return {sensor: value for sensor, value in self.sensors.items()}

    def receive_values(self, values):
        # Simulating receiving values from another device
        print(f"Device {self.device_id} received values: {values}")

    def manipulate_sensors(self):
        # Simulating actuator manipulating sensors (replace with actual actuator logic)
        manipulated_value = self.actuator.manipulate(self.sensors)
        print(
            f"Actuator of Device {self.device_id} manipulated sensors. New value: {manipulated_value}"
        )
        self.sensors["manipulated_sensor"] = manipulated_value


class Actuator:
    def manipulate(self, sensors):
        # Simulating actuator manipulation logic (replace with actual actuator logic)
        return sum(sensors.values()) / len(sensors)


# Example usage:
device1 = Device(device_id=1)
device2 = Device(device_id=2)

device1.generate_sensor_values()
device2.generate_sensor_values()

values_to_emit = device1.emit_sensor_values()
device2.receive_values(values_to_emit)

device1.manipulate_sensors()
