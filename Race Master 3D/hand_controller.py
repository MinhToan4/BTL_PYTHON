"""
Tổng quan về file hand_controller.py:

File hand_controller.py định nghĩa class HandController để điều khiển xe bằng cử chỉ tay sử dụng MediaPipe và OpenCV.
Phát hiện cử chỉ tay qua webcam để lái xe, tăng tốc, và pause game.
"""

# Race Master 3D Hand Controller - Tích hợp MediaPipe vào game
# Cài đặt: pip install mediapipe opencv-python

import time
import math
import threading
import cv2
import mediapipe as mp
from drive import get_drive_controller
from steering import get_steering_controller

class HandController:
    """
    Class HandController quản lý điều khiển xe bằng cử chỉ tay.
    Sử dụng MediaPipe để detect tay và OpenCV để capture camera.
    """
    def __init__(self, car):
        self.car = car  # Reference đến car object
        self.enabled = False  # Có đang enable không
        self.running = False  # Có đang chạy thread không
        self.thread = None  # Thread cho detection

        # Cấu hình
        self.CAM_INDEX = 0  # Index camera
        self.FLIP_DISPLAY = False  # Lật hiển thị camera
        self.TURN_THR = 0.12          # Ngưỡng rẽ trái/phải
        self.OPEN_THR = 2.0           # Ngưỡng mở tay để tăng tốc
        self.PINCH_THR = 0.6          # Ngưỡng chụm để pause
        self.DEBOUNCE_SEC = 0.8       # Chống spam

        # Hiển thị debug camera
        self.show_debug = True        # Luôn hiển thị camera để user thấy cử chỉ

        # Controllers mới
        self.drive_controller = get_drive_controller()  # Controller cho drive
        self.steering_controller = get_steering_controller(car)  # Controller cho steering

        # Trạng thái điều khiển (giữ để tương thích)
        self.controls = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False,
            'pause': False
        }

        # MediaPipe
        self.mp_hands = mp.solutions.hands  # Module hands của MediaPipe
        self.mp_draw = mp.solutions.drawing_utils  # Utils để vẽ landmarks
        self.mp_style = mp.solutions.drawing_styles  # Styles cho drawing

        # Debounce
        self.last_pause = 0.0  # Thời gian pause cuối

    def start(self):
        """Bắt đầu hand controller"""
        if not self.running:
            self.enabled = True
            self.running = True
            
            # Lưu handle của cửa sổ game hiện tại
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
            
            # Tự động restore game window sau khi camera được tạo
            if self.game_window:
                def restore_game_focus():
                    try:
                        import win32gui
                        import win32con
                        # Restore và focus game window
                        win32gui.ShowWindow(self.game_window, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(self.game_window)
                        print("Đã restore game window")
                    except Exception as e:
                        print(f"Lỗi khi restore game window: {e}")
                
                # Delay 1 giây để camera window được tạo xong
                timer = threading.Timer(1.0, restore_game_focus)
                timer.start()

    def stop(self):
        """Dừng hand controller"""
        self.enabled = False
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        # Dừng tất cả controls
        self.drive_controller.stop_drive()
        self.steering_controller.stop_steering()
        print("Hand Controller đã dừng!")

    def get_controls(self):
        """Lấy trạng thái điều khiển hiện tại (dựa trên drive/steering controllers)"""
        controls = {
            'forward': self.drive_controller.last_drive_state == 'forward',
            'backward': self.drive_controller.last_drive_state == 'backward', 
            'left': self.steering_controller.last_steering_state == 'left',
            'right': self.steering_controller.last_steering_state == 'right',
            'pause': False  # Pause vẫn từ logic cũ
        }
        return controls

    def is_enabled(self):
        """Kiểm tra xem controller có đang hoạt động không"""
        return self.enabled and self.running

    def _run_detection(self):
        """Thread chính để detect cử chỉ tay"""
        cap = cv2.VideoCapture(self.CAM_INDEX, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("Không thể mở webcam!")
            self.running = False
            return

        with self.mp_hands.Hands(
            max_num_hands=2,  # Tối đa 2 tay
            model_complexity=0,  # Độ phức tạp model
            min_detection_confidence=0.6,  # Ngưỡng confidence detection
            min_tracking_confidence=0.5  # Ngưỡng confidence tracking
        ) as hands:

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue

                # Xử lý MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_frame.flags.writeable = False
                results = hands.process(rgb_frame)
                
                # Lấy kích thước frame
                imageHeight, imageWidth, _ = frame.shape

                # Reset controls
                new_controls = {
                    'forward': False,
                    'backward': False,
                    'left': False,
                    'right': False,
                    'pause': False
                }

                now = time.time()
                hand_positions = []  # List vị trí tay [(x,y), ...] - pixel coordinates
                hand_positions_normalized = []  # List vị trí tay [(x,y), ...] - normalized

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        landmarks = hand_landmarks.landmark

                        # Tính tâm bàn tay - normalized
                        cx, cy = self._palm_center(landmarks)
                        if self.FLIP_DISPLAY:
                            cx = 1.0 - cx
                        hand_positions_normalized.append((cx, cy))

                        # Tính tâm bàn tay - pixel coordinates
                        pixel_cx = int(cx * imageWidth)
                        pixel_cy = int(cy * imageHeight)
                        hand_positions.append((pixel_cx, pixel_cy))

                # Cập nhật drive và steering controllers
                hand_count = len(hand_positions)
                self.drive_controller.update_drive(hand_count, hand_positions_normalized)  # Drive dùng normalized
                self.steering_controller.update_steering(hand_count, hand_positions)  # Steering dùng pixel

                # Xử lý pause (cử chỉ OK) - giữ nguyên
                min_pinch_ratio = 9999.0
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        landmarks = hand_landmarks.landmark
                        pinch_ratio = self._pinch_ratio(landmarks)
                        min_pinch_ratio = min(min_pinch_ratio, pinch_ratio)

                if (min_pinch_ratio < self.PINCH_THR and
                    (now - self.last_pause) > self.DEBOUNCE_SEC):
                    new_controls['pause'] = True
                    self.last_pause = now

                # Cập nhật controls
                self.controls = new_controls

                # Hiển thị debug window (tùy chọn)
                if hasattr(self, 'show_debug') and self.show_debug:
                    self._draw_debug(frame, results, hand_count, hand_positions)

                # Giới hạn FPS
                time.sleep(0.033)  # ~30 FPS

        cap.release()
        cv2.destroyAllWindows()

    def _palm_center(self, landmarks):
        """Tính tâm bàn tay"""
        wrist = landmarks[0]
        middle_mcp = landmarks[9]
        cx = (wrist.x + middle_mcp.x) * 0.5
        cy = (wrist.y + middle_mcp.y) * 0.5
        return cx, cy

    def _pinch_ratio(self, landmarks):
        """Tính tỷ lệ chụm ngón cái và trỏ"""
        base_dist = math.hypot(landmarks[0].x - landmarks[9].x, landmarks[0].y - landmarks[9].y) or 1e-6
        pinch_dist = math.hypot(landmarks[4].x - landmarks[8].x, landmarks[4].y - landmarks[8].y)
        return pinch_dist / base_dist

    def _draw_debug(self, frame, results, hand_count, hand_positions):
        """Vẽ debug info lên frame"""
        vis_frame = frame.copy()
        if self.FLIP_DISPLAY:
            vis_frame = cv2.flip(vis_frame, 1)

        # Vẽ landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    vis_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_style.get_default_hand_landmarks_style(),
                    self.mp_style.get_default_hand_connections_style()
                )

        # Vẽ thông tin
        h, w = vis_frame.shape[:2]

        # Hiển thị số tay và vị trí
        cv2.putText(vis_frame, f"Hands: {hand_count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if hand_positions:
            avg_x = sum(pos[0] for pos in hand_positions) / len(hand_positions)
            cv2.putText(vis_frame, f"Avg X: {avg_x:.2f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Vẽ trạng thái điều khiển
        controls_text = []
        if self.controls['pause']: controls_text.append("PAUSE")

        # Thêm thông tin từ drive và steering controllers
        drive_state = self.drive_controller.last_drive_state
        steering_state = self.steering_controller.last_steering_state

        if drive_state == 'forward': controls_text.append("W")
        elif drive_state == 'backward': controls_text.append("S")

        if steering_state == 'left': controls_text.append("A")
        elif steering_state == 'right': controls_text.append("D")

        cv2.putText(vis_frame, f"Keys: {' '.join(controls_text)}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Hiển thị cửa sổ camera luôn trên cùng game fullscreen
        window_name = "Hand Controller - Camera"
        
        # Tạo cửa sổ với flags đặc biệt để luôn hiển thị trên cùng
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        
        # Resize frame để có kích thước lớn hơn, dễ nhìn
        display_width, display_height = 400, 300  # Tăng kích thước từ 320x240
        small_frame = cv2.resize(vis_frame, (display_width, display_height))
        
        # Hiển thị frame
        cv2.imshow(window_name, small_frame)
        
        # Đặt vị trí và thuộc tính cửa sổ để luôn hiển thị trên game fullscreen
        try:
            import win32gui
            import win32con
            import time
            
            def find_and_position_window():
                camera_hwnd = win32gui.FindWindow(None, window_name)
                if camera_hwnd:
                    # Lấy kích thước màn hình
                    screen_width = win32gui.GetSystemMetrics(0)
                    screen_height = win32gui.GetSystemMetrics(1)
                    
                    # Đặt vị trí góc dưới bên trái, cách lề 20px
                    x = 20
                    y = screen_height - display_height - 80  # 80px từ dưới để tránh taskbar
                    
                    # Set window attributes để luôn hiển thị trên cùng, ngay cả khi game fullscreen
                    win32gui.SetWindowPos(camera_hwnd, win32con.HWND_TOPMOST, 
                                        x, y, display_width, display_height, 
                                        win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE)
                    
                    # Đảm bảo cửa sổ không bị minimize và luôn visible
                    win32gui.ShowWindow(camera_hwnd, win32con.SW_SHOWNORMAL)
                    
                    # Set extended window style để tránh bị che khuất
                    current_style = win32gui.GetWindowLong(camera_hwnd, win32con.GWL_EXSTYLE)
                    win32gui.SetWindowLong(camera_hwnd, win32con.GWL_EXSTYLE, 
                                         current_style | win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW)
                    
                    return True
                return False
            
            # Đảm bảo cửa sổ được tạo và định vị đúng cách
            if not hasattr(self, '_window_positioned') or not self._window_positioned:
                if find_and_position_window():
                    self._window_positioned = True
                else:
                    # Thử lại sau một chút nếu chưa tìm thấy cửa sổ
                    def delayed_position():
                        time.sleep(0.05)
                        if find_and_position_window():
                            self._window_positioned = True
                    
                    threading.Timer(0.05, delayed_position).start()
            else:
                # Periodically ensure window stays on top (mỗi 60 frames ~ 2 giây)
                if not hasattr(self, '_frame_count'):
                    self._frame_count = 0
                self._frame_count += 1
                if self._frame_count % 60 == 0:  # Mỗi 60 frames
                    find_and_position_window()  # Re-ensure topmost
                    
        except Exception as e:
            # Fallback: sử dụng OpenCV basic positioning
            try:
                cv2.moveWindow(window_name, 20, screen_height - 440 if 'screen_height' in locals() else 640)
                # Thử set window property để stay on top (không phải tất cả OpenCV build đều support)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
            except:
                pass
        
        cv2.waitKey(1)

# Global instance
hand_controller = None

def get_hand_controller(car):
    """Lấy instance của hand controller"""
    global hand_controller
    if hand_controller is None:
        hand_controller = HandController(car)
    return hand_controller