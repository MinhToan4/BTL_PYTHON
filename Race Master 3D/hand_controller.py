"""
Module điều khiển xe bằng cử chỉ tay sử dụng MediaPipe và OpenCV.

Phát hiện và xử lý cử chỉ tay từ webcam để điều khiển xe trong game:
- 2 tay (trung lập): Tiến (W)
- 1 tay: Lùi (S)
- 2 tay nghiêng: Rẽ trái (A) hoặc phải (D)
- Cử chỉ chụm ngón tay: Pause game

Chạy trong thread riêng để không block game loop chính.
"""

import time
import math
import threading
import cv2
import mediapipe as mp
from drive import get_drive_controller
from steering import get_steering_controller

class HandController:
    """Quản lý điều khiển xe bằng nhận diện cử chỉ tay qua MediaPipe."""
    
    def __init__(self, car):
        """
        Khởi tạo hand controller.
        
        Args:
            car: Đối tượng xe cần điều khiển
        """
        self.car = car
        self.enabled = False
        self.running = False
        self.thread = None

        # Ngưỡng nhận diện cử chỉ
        self.CAM_INDEX = 0
        self.FLIP_DISPLAY = False
        self.TURN_THR = 0.12
        self.OPEN_THR = 2.0
        self.PINCH_THR = 0.6
        self.DEBOUNCE_SEC = 0.8  # Thời gian chờ giữa các lần pause để tránh spam

        self.show_debug = True

        # Controllers xử lý việc gửi phím W/A/S/D
        self.drive_controller = get_drive_controller()
        self.steering_controller = get_steering_controller(car)

        # Dictionary lưu trạng thái điều khiển (để tương thích ngược)
        self.controls = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False,
            'pause': False
        }

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_style = mp.solutions.drawing_styles

        self.last_pause = 0.0

    def start(self):
        """Khởi động hand controller trong thread riêng."""
        if not self.running:
            self.enabled = True
            self.running = True
            
            # Lưu window handle để restore sau khi tạo camera window
            try:
                import win32gui
                self.game_window = win32gui.GetForegroundWindow()
                print(f"Đã lưu game window handle: {self.game_window}")
            except ImportError:
                self.game_window = None
                print("Không thể import win32gui - cửa sổ game có thể bị minimize")
            
            self.thread = threading.Thread(target=self._run_detection, daemon=True)
            self.thread.start()
            print("Hand Controller đã bắt đầu!")
            
            # Tự động restore game window sau 1 giây (sau khi camera window được tạo)
            if self.game_window:
                def restore_game_focus():
                    try:
                        import win32gui
                        import win32con
                        win32gui.ShowWindow(self.game_window, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(self.game_window)
                        print("Đã restore game window")
                    except Exception as e:
                        print(f"Lỗi khi restore game window: {e}")
                
                timer = threading.Timer(1.0, restore_game_focus)
                timer.start()

    def stop(self):
        """Dừng hand controller và giải phóng tất cả phím đang nhấn."""
        self.enabled = False
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.drive_controller.stop_drive()
        self.steering_controller.stop_steering()
        print("Hand Controller đã dừng!")

    def get_controls(self):
        """
        Lấy trạng thái điều khiển hiện tại.
        
        Returns:
            dict: Trạng thái các phím điều khiển
        """
        controls = {
            'forward': self.drive_controller.last_drive_state == 'forward',
            'backward': self.drive_controller.last_drive_state == 'backward', 
            'left': self.steering_controller.last_steering_state == 'left',
            'right': self.steering_controller.last_steering_state == 'right',
            'pause': False
        }
        return controls

    def is_enabled(self):
        """Kiểm tra xem controller có đang hoạt động không."""
        return self.enabled and self.running

    def _run_detection(self):
        """
        Vòng lặp chính xử lý nhận diện cử chỉ tay.
        
        Chạy ở ~30 FPS để cân bằng giữa hiệu năng và độ phản hồi.
        Sử dụng MediaPipe để detect hand landmarks và chuyển thành điều khiển.
        """
        cap = cv2.VideoCapture(self.CAM_INDEX, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("Không thể mở webcam!")
            self.running = False
            return

        with self.mp_hands.Hands(
            max_num_hands=2,
            model_complexity=0,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5
        ) as hands:

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_frame.flags.writeable = False
                results = hands.process(rgb_frame)
                
                imageHeight, imageWidth, _ = frame.shape

                new_controls = {
                    'forward': False,
                    'backward': False,
                    'left': False,
                    'right': False,
                    'pause': False
                }

                now = time.time()
                hand_positions = []  # Tọa độ pixel
                hand_positions_normalized = []  # Tọa độ chuẩn hóa [0-1]

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        landmarks = hand_landmarks.landmark

                        cx, cy = self._palm_center(landmarks)
                        if self.FLIP_DISPLAY:
                            cx = 1.0 - cx
                        hand_positions_normalized.append((cx, cy))

                        pixel_cx = int(cx * imageWidth)
                        pixel_cy = int(cy * imageHeight)
                        hand_positions.append((pixel_cx, pixel_cy))

                # Cập nhật controllers (drive dùng normalized, steering dùng pixel)
                hand_count = len(hand_positions)
                self.drive_controller.update_drive(hand_count, hand_positions_normalized)
                self.steering_controller.update_steering(hand_count, hand_positions)

                # Kiểm tra cử chỉ chụm để pause
                min_pinch_ratio = 9999.0
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        landmarks = hand_landmarks.landmark
                        pinch_ratio = self._pinch_ratio(landmarks)
                        min_pinch_ratio = min(min_pinch_ratio, pinch_ratio)

                # Debouncing để tránh spam pause
                if (min_pinch_ratio < self.PINCH_THR and
                    (now - self.last_pause) > self.DEBOUNCE_SEC):
                    new_controls['pause'] = True
                    self.last_pause = now

                self.controls = new_controls

                if hasattr(self, 'show_debug') and self.show_debug:
                    self._draw_debug(frame, results, hand_count, hand_positions)

                time.sleep(0.033)  # ~30 FPS

        cap.release()
        cv2.destroyAllWindows()

    def _palm_center(self, landmarks):
        """
        Tính tâm bàn tay từ landmarks.
        
        Sử dụng trung bình của cổ tay (landmark 0) và khớp giữa ngón giữa (landmark 9).
        """
        wrist = landmarks[0]
        middle_mcp = landmarks[9]
        cx = (wrist.x + middle_mcp.x) * 0.5
        cy = (wrist.y + middle_mcp.y) * 0.5
        return cx, cy

    def _pinch_ratio(self, landmarks):
        """
        Tính tỷ lệ chụm ngón tay (khoảng cách đầu ngón cái - ngón trỏ).
        
        Chuẩn hóa theo khoảng cách cổ tay - ngón giữa để không phụ thuộc kích thước tay.
        """
        base_dist = math.hypot(landmarks[0].x - landmarks[9].x, landmarks[0].y - landmarks[9].y) or 1e-6
        pinch_dist = math.hypot(landmarks[4].x - landmarks[8].x, landmarks[4].y - landmarks[8].y)
        return pinch_dist / base_dist

    def _draw_debug(self, frame, results, hand_count, hand_positions):
        """
        Vẽ debug overlay lên camera frame.
        
        Hiển thị hand landmarks, số tay, vị trí, và trạng thái điều khiển.
        Window được đặt ở góc dưới trái và luôn hiển thị trên cùng (ngay cả khi game fullscreen).
        """
        vis_frame = frame.copy()
        if self.FLIP_DISPLAY:
            vis_frame = cv2.flip(vis_frame, 1)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    vis_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_style.get_default_hand_landmarks_style(),
                    self.mp_style.get_default_hand_connections_style()
                )

        h, w = vis_frame.shape[:2]

        cv2.putText(vis_frame, f"Hands: {hand_count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if hand_positions:
            avg_x = sum(pos[0] for pos in hand_positions) / len(hand_positions)
            cv2.putText(vis_frame, f"Avg X: {avg_x:.2f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        controls_text = []
        if self.controls['pause']: controls_text.append("PAUSE")

        drive_state = self.drive_controller.last_drive_state
        steering_state = self.steering_controller.last_steering_state

        if drive_state == 'forward': controls_text.append("W")
        elif drive_state == 'backward': controls_text.append("S")

        if steering_state == 'left': controls_text.append("A")
        elif steering_state == 'right': controls_text.append("D")

        cv2.putText(vis_frame, f"Keys: {' '.join(controls_text)}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        window_name = "Hand Controller - Camera"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        
        display_width, display_height = 400, 300
        small_frame = cv2.resize(vis_frame, (display_width, display_height))
        cv2.imshow(window_name, small_frame)
        
        # Dùng Win32 API để đảm bảo window luôn hiển thị trên game fullscreen
        try:
            import win32gui
            import win32con
            import time
            
            def find_and_position_window():
                camera_hwnd = win32gui.FindWindow(None, window_name)
                if camera_hwnd:
                    screen_width = win32gui.GetSystemMetrics(0)
                    screen_height = win32gui.GetSystemMetrics(1)
                    
                    x = 20
                    y = screen_height - display_height - 80  # Cách taskbar 80px
                    
                    # Set HWND_TOPMOST để window luôn nổi lên trên
                    win32gui.SetWindowPos(camera_hwnd, win32con.HWND_TOPMOST, 
                                        x, y, display_width, display_height, 
                                        win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE)
                    
                    win32gui.ShowWindow(camera_hwnd, win32con.SW_SHOWNORMAL)
                    
                    current_style = win32gui.GetWindowLong(camera_hwnd, win32con.GWL_EXSTYLE)
                    win32gui.SetWindowLong(camera_hwnd, win32con.GWL_EXSTYLE, 
                                         current_style | win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW)
                    
                    return True
                return False
            
            if not hasattr(self, '_window_positioned') or not self._window_positioned:
                if find_and_position_window():
                    self._window_positioned = True
                else:
                    def delayed_position():
                        time.sleep(0.05)
                        if find_and_position_window():
                            self._window_positioned = True
                    
                    threading.Timer(0.05, delayed_position).start()
            else:
                # Tái khẳng định topmost mỗi ~2 giây
                if not hasattr(self, '_frame_count'):
                    self._frame_count = 0
                self._frame_count += 1
                if self._frame_count % 60 == 0:
                    find_and_position_window()
                    
        except Exception as e:
            try:
                cv2.moveWindow(window_name, 20, screen_height - 440 if 'screen_height' in locals() else 640)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
            except:
                pass
        
        cv2.waitKey(1)


hand_controller = None

def get_hand_controller(car):
    """
    Lấy hoặc tạo instance singleton của hand controller.
    
    Args:
        car: Đối tượng xe cần điều khiển
        
    Returns:
        HandController: Instance duy nhất của hand controller
    """
    global hand_controller
    if hand_controller is None:
        hand_controller = HandController(car)
    return hand_controller