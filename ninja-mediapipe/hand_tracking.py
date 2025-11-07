# hand_tracking.py
import cv2
import mediapipe as mp

class HandInput:
    def __init__(self):
        self.hands = None
        self.cap = None

    def setup(self, enabled: bool, cam_index: int):
        self.close()
        if enabled:
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.6
            )
            self.cap = cv2.VideoCapture(cam_index, cv2.CAP_MSMF)

    def read(self, width: int, height: int):
        """
        Trả về (finger_pos | None, rgb | None)
        - finger_pos: (x,y) theo toạ độ màn hình game
        - rgb: frame RGB (numpy) để vẽ nền; None nếu tắt camera
        """
        if self.hands is None or self.cap is None:
            return None, None
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        finger_pos = None
        if results and results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0]
            x = int(lm.landmark[8].x * width)
            y = int(lm.landmark[8].y * height)
            finger_pos = (x, y)
        return finger_pos, rgb

    def close(self):
        try:
            if self.hands is not None:
                self.hands.close()
        except Exception:
            pass
        self.hands = None
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
        self.cap = None
