import pyWinhook as pyHook
import pythoncom

def onMouseEvent(event):
    # Mouse press
    if event.MessageName == 'mouse left down':
        x, y = event.Position
        print(f"Mouse pressed at ({x}, {y})")
        # Send start position to your overlay application
        send_to_overlay('start', x, y)

    # Mouse move
    elif event.MessageName == 'mouse move':
        x, y = event.Position
        # Send move position to your overlay application
        send_to_overlay('move', x, y)

    # Mouse release
    elif event.MessageName == 'mouse left up':
        x, y = event.Position
        print(f"Mouse released at ({x}, {y})")
        # Send end position to your overlay application
        send_to_overlay('end', x, y)

    return True  # Return True to pass the event to other handlers

def send_to_overlay(action, x, y):
    # Implement the communication to your overlay application
    print(f"Action: {action}, X: {x}, Y: {y}")
    # Example: Use a socket, HTTP request, or other IPC methods to send data

def main():
    # Create a hook manager
    hm = pyHook.HookManager()
    # Set the mouse hook
    hm.SubscribeMouseAllButtonsDown(onMouseEvent)
    hm.SubscribeMouseAllButtonsUp(onMouseEvent)
    hm.SubscribeMouseMove(onMouseEvent)
    # Start the hook
    hm.HookMouse()
    # Enter into a perpetual loop
    pythoncom.PumpMessages()

if __name__ == "__main__":
    main()
