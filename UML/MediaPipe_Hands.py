import cv2
import mediapipe as mp

# Khởi tạo MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Mở webcam
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Lật ảnh để giống gương
        frame = cv2.flip(frame, 1)

        # Chuyển sang RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Xử lý ảnh với MediaPipe
        results = hands.process(rgb_frame)

        # Vẽ landmarks nếu phát hiện tay
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Hiển thị
        cv2.imshow("Hand Tracking", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC để thoát
            break

cap.release()
cv2.destroyAllWindows()