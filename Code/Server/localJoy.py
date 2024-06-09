import threading
import time
import inputs
import signal
import sys
from Control import *

MV_X = 'ABS_X' #Joystick X Axis
MV_Y = 'ABS_Y' #Joystick Y Axis
ROTATE = 'ABS_Z'   #Joystick Rotation Axis
# THRTL = 'ABS_RZ'    #Throttle 
# T_PDL = '?'    #Throttle Paddle
# HAT_X = 'ABS_HAT0X'    #Hat Direction X 
# HAT_Y = 'ABS_HAT0Y?'    #Hat Direction Y
CMD_MOVE = 'CMD_MOVE'
X_J_LIM = 255
Y_J_LIM = 255
R_J_LIM = 255
X_M_LIM = 33
Y_M_LIM = 33
R_M_LIM = 15

def map_range(value, fromMin, fromMax, toMin, toMax):
    # Maps a value from one range to another
    fromSpan = fromMax - fromMin
    toSpan = toMax - toMin
    valueScaled = float(value - fromMin) / float(fromSpan)
    return int(toMin + (valueScaled * toSpan))

def update_order_with_joystick(control, stop_event):
    x_movement = 128
    y_movement = 128
    rotation = 128
    while not stop_event.is_set():
        events = inputs.get_gamepad()
        for event in events:
            if event.ev_type == 'Absolute':
                if event.code == 'ABS_X':
                    x_movement = event.state
                elif event.code == 'ABS_Y':
                    y_movement = event.state
                elif event.code == 'ABS_Z':
                    rotation  = event.state
        
        # Map joystick values to control orders
        x_order = str(map_range(x_movement, 0, X_J_LIM, -1 * X_M_LIM, X_M_LIM))
        y_order = str(-1 * map_range(y_movement, 0, Y_J_LIM, -1 * Y_M_LIM, Y_M_LIM))
        r_order = str(map_range(rotation, 0, R_J_LIM, -1 * R_M_LIM, R_M_LIM))
        # Update the order parameter in the control object
        control.order = [CMD_MOVE, '1', x_order, y_order, '10', r_order]  # Update based on the correct indices
        print(control.order)
        time.sleep(0.001)  # Adding a delay to avoid overloading the control loop

def main():
    control = Control()
    stop_event = threading.Event()
    
    # Start the condition method in a separate thread
    condition_thread = threading.Thread(target=control.condition)
    condition_thread.start()
    
    # Start the joystick control loop in a separate thread
    joystick_thread = threading.Thread(target=update_order_with_joystick, args=(control, stop_event))
    joystick_thread.start()
    
    def signal_handler(sig, frame):
        print('Shutting down gracefully...')
        control.stop()
        stop_event.set()
        condition_thread.join()
        joystick_thread.join()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Keep the main thread alive to handle signals
    signal.pause()

if __name__ == '__main__':
    main()


