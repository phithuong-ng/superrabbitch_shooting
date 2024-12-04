import cv2
import mediapipe as mp
from pynput.keyboard import Key, Controller

# Initialize Mediapipe and Pynput
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
keyboard = Controller()

# Flags to track key states
keys_pressed = {"left": False, "right": False, "space": False, "s": False}

# For webcam input:
cap = cv2.VideoCapture(0)  # Adjust this index if the webcam doesn't work
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Process the frame
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            # Draw hand annotations and check finger positions
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Index finger (left key)
                    if hand_landmarks.landmark[8].y < hand_landmarks.landmark[7].y:
                        if not keys_pressed["left"]:
                            keyboard.press(Key.left)
                            keys_pressed["left"] = True
                    else:
                        if keys_pressed["left"]:
                            keyboard.release(Key.left)
                            keys_pressed["left"] = False
                        
                    # Middle finger (right key)
                    if hand_landmarks.landmark[12].y < hand_landmarks.landmark[11].y:
                        if not keys_pressed["right"]:
                            keyboard.press(Key.right)
                            keys_pressed["right"] = True
                    else:
                        if keys_pressed["right"]:
                            keyboard.release(Key.right)
                            keys_pressed["right"] = False
                    
                    # Thumb (space key)
                    if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
                        if not keys_pressed["space"]:
                            keyboard.press(Key.space)
                            keys_pressed["space"] = True
                    else:
                        if keys_pressed["space"]:
                            keyboard.release(Key.space)
                            keys_pressed["space"] = False
                    
                    # Pinky finger (s key)
                    if hand_landmarks.landmark[20].y < hand_landmarks.landmark[19].y:
                        if not keys_pressed["s"]:
                            keyboard.press('s')
                            keys_pressed["s"] = True
                    else:
                        if keys_pressed["s"]:
                            keyboard.release('s')
                            keys_pressed["s"] = False

                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

            # Flip the image horizontally for a selfie-view display
            cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:  # Press 'Esc' to exit
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()