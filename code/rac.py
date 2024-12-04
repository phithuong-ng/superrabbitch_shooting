import threading
import subprocess

def run_testing2():
    subprocess.run(["python", "C:\\Users\\Swift3\\Desktop\\superrabbitch_shooting\\code\\testing2.py"])

def run_hand_control():
    subprocess.run(["python", "C:\\Users\\Swift3\\Desktop\\superrabbitch_shooting\\code\\hand_control.py"])

if __name__ == "__main__":
    # Create threads for running both scripts
    testing2_thread = threading.Thread(target=run_testing2)
    hand_control_thread = threading.Thread(target=run_hand_control)

    # Start the threads
    testing2_thread.start()
    hand_control_thread.start()

    # Wait for both threads to complete
    testing2_thread.join()
    hand_control_thread.join()
