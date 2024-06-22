import threading
import time
import signal
import sys
from Control import *
from pyPS4Controller.controller import Controller

# Constants for joystick and movement limits
MV_X = 'ABS_X'
MV_Y = 'ABS_Y'
ROTATE = 'ABS_Z'
CMD_MOVE = 'CMD_MOVE'
X_J_LIM = 32767
Y_J_LIM = 32767
R_J_LIM = 32767
X_M_LIM = 33
Y_M_LIM = 33
R_M_LIM = 15

# Constants for deadzone, damping, and maximum zone
DEADZONE_PERCENTAGE = 0.09
DAMPING_THRESHOLD_PERCENTAGE = 0.01
MAX_ZONE_PERCENTAGE = 1

# Function to apply deadzone logic to joystick input values
def apply_deadzone(value, limit):
    deadzone = limit * DEADZONE_PERCENTAGE
    max_zone = limit * MAX_ZONE_PERCENTAGE

    # Apply deadzone: if the value is within the deadzone, return 0
    if abs(value) < deadzone:
        return 0
    
    # Apply max zone: if the value exceeds the max zone, cap it at the limit
    if abs(value) > max_zone:
        return limit if value > 0 else -limit

    return value

# Custom controller class extending from pyPS4Controller.Controller
class MyController(Controller):
    def __init__(self, control, stop_event, **kwargs):
        super().__init__(**kwargs)
        self.control = control
        self.stop_event = stop_event
        self.movements = {'x': 0, 'y': 0, 'r': 0}
        self.last_movements = {'x': 0, 'y': 0, 'r': 0}
        self.throttle = 9

    # Handlers for joystick movements
    def on_L3_up(self, value):
        self.handle_movement('y', -value)

    def on_L3_down(self, value):
        self.handle_movement('y', -value)

    def on_L3_left(self, value):
        self.handle_movement('x', value)

    def on_L3_right(self, value):
        self.handle_movement('x', value)

    def on_R3_left(self, value):
        self.handle_movement('r', value)

    def on_R3_right(self, value):
        self.handle_movement('r', value)

    # Handlers for button presses to adjust throttle
    def on_x_press(self):
        if self.throttle > 0:
            self.throttle -= 1

    def on_triangle_press(self):
        if self.throttle < 10:
            self.throttle += 1

    # Overrides to suppress default print statements in pyPS4Controller library
    def on_L3_y_at_rest(self):
        pass

    def on_L3_x_at_rest(self):
        pass

    def on_R3_up(self, value):
        pass

    def on_R3_down(self, value):
        pass

    def on_R3_x_at_rest(self):
        pass

    def on_R3_y_at_rest(self):
        pass

    def on_R2_press(self, value):
        pass

    def on_R2_release(self):
        pass

    def on_L2_press(self, value):
        pass

    def on_L2_release(self):
        pass

    def on_x_release(self):
        pass

    def on_triangle_release(self):
        pass

    # Function to handle joystick movements
    def handle_movement(self, axis, value):
        limit = {'x': X_J_LIM, 'y': Y_J_LIM, 'r': R_J_LIM}[axis]
        self.movements[axis] = apply_deadzone(value, limit)
        self.update_order()

    # Function to check if a significant change in joystick value has occurred
    def has_significant_change(self, current_value, last_value, limit):
        damping_threshold = limit * DAMPING_THRESHOLD_PERCENTAGE
        return abs(current_value - last_value) > damping_threshold

    # Function to update the movement order if significant changes are detected
    def update_order(self):
        send_update = False
        for axis in self.movements:
            limit = {'x': X_J_LIM, 'y': Y_J_LIM, 'r': R_J_LIM}[axis]
            if self.has_significant_change(self.movements[axis], self.last_movements[axis], limit):
                self.last_movements[axis] = self.movements[axis]
                send_update = True

        if send_update:
            x_order = str(round(self.control.map(self.movements['x'], -X_J_LIM, X_J_LIM, -X_M_LIM, X_M_LIM)))
            y_order = str(round(self.control.map(self.movements['y'], -Y_J_LIM, Y_J_LIM, -Y_M_LIM, Y_M_LIM)))
            r_order = str(round(self.control.map(self.movements['r'], -R_J_LIM, R_J_LIM, -R_M_LIM, R_M_LIM)))
            self.control.order = [CMD_MOVE, '1', x_order, y_order, str(self.throttle), r_order]
            print(self.control.order)
            time.sleep(0.01)  # Add a short delay to avoid excessive updates

# Main function to set up and run the controller
def main():
    control = Control()
    stop_event = threading.Event()

    # Start the condition method in a separate thread
    condition_thread = threading.Thread(target=control.condition)
    condition_thread.start()

    # Initialize and start the custom controller
    controller = MyController(control, stop_event, interface="/dev/input/js0", connecting_using_ds4drv=False)
    controller.listen()

    # Signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print('Shutting down gracefully...')
        control.stop()
        stop_event.set()
        condition_thread.join()
        sys.exit(0)

    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()  # Keep the main thread alive to handle signals

if __name__ == '__main__':
    main()
