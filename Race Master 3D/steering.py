"""
Tổng quan về file steering.py:

File steering.py định nghĩa class SteeringController để xử lý logic rẽ trái/phải (A/D) trong hand controller.
Sử dụng vị trí tay để quyết định hướng rẽ và simulate nhấn phím tương ứng.
"""

# Race Master 3D Steering Controller - Xử lý logic rẽ trái/phải (A/D)
# Cài đặt: pip install mediapipe opencv-python

import keyinput

class SteeringController:
    """
    Class SteeringController quản lý logic rẽ trái/phải dựa trên cử chỉ tay.
    """
    def __init__(self, car):
        """Khởi tạo steering controller"""
        self.car = car  # Reference đến car object để lấy flip_steering
        self.last_steering_state = None  # 'left', 'right', hoặc None

    def update_steering(self, hand_count, hand_positions):
        """
        Cập nhật trạng thái steering dựa trên cử chỉ tay

        Args:
            hand_count: Số tay phát hiện được (0, 1, 2)
            hand_positions: List vị trí các tay [(x1,y1), (x2,y2), ...]

        Logic theo yêu cầu:
        - A (rẽ trái): Tay nghiêng trái với điều kiện cụ thể
        - D (rẽ phải): Tay nghiêng phải với điều kiện cụ thể
        """
        new_steering_state = None

        if hand_count >= 1 and hand_positions:
            # Cần ít nhất 1 tay để steering
            # Logic dựa trên vị trí tương đối của 2 tay (nếu có)

            if hand_count == 2 and len(hand_positions) >= 2:
                # 2 tay - kiểm tra vị trí tương đối
                co = hand_positions  # co[0] = tay 1, co[1] = tay 2

                # Logic rẽ phải (đã sửa): co[0][0] > co[1][0] và co[0][1] > co[1][1] với chênh lệch Y > 65
                # hoặc co[1][0] > co[0][0] và co[1][1] > co[0][1] với chênh lệch Y > 65
                if ((co[0][0] > co[1][0] and co[0][1] > co[1][1] and abs(co[0][1] - co[1][1]) > 65) or
                    (co[1][0] > co[0][0] and co[1][1] > co[0][1] and abs(co[1][1] - co[0][1]) > 65)):
                    new_steering_state = 'right'   # D (đã đổi từ left thành right)

                # Logic rẽ trái (đã sửa): co[0][0] > co[1][0] và co[1][1] > co[0][1] với chênh lệch Y > 65
                # hoặc co[1][0] > co[0][0] và co[0][1] > co[1][1] với chênh lệch Y > 65
                elif ((co[0][0] > co[1][0] and co[1][1] > co[0][1] and abs(co[1][1] - co[0][1]) > 65) or
                      (co[1][0] > co[0][0] and co[0][1] > co[1][1] and abs(co[0][1] - co[1][1]) > 65)):
                    new_steering_state = 'left'  # A (đã đổi từ right thành left)

            # Với 1 tay, có thể không steering hoặc steering dựa trên vị trí
            # Hiện tại để None (không steering)

        # Áp dụng flip steering nếu được bật
        if self.car.flip_steering and new_steering_state:
            if new_steering_state == 'left':
                new_steering_state = 'right'
            elif new_steering_state == 'right':
                new_steering_state = 'left'

        # Chỉ thay đổi key press nếu trạng thái thay đổi
        if new_steering_state != self.last_steering_state:
            # Release key cũ
            if self.last_steering_state == 'left':
                keyinput.release_key('a')
            elif self.last_steering_state == 'right':
                keyinput.release_key('d')

            # Press key mới
            if new_steering_state == 'left':
                keyinput.press_key('a')
            elif new_steering_state == 'right':
                keyinput.press_key('d')

            self.last_steering_state = new_steering_state

    def stop_steering(self):
        """Dừng tất cả steering controls"""
        keyinput.release_key('a')
        keyinput.release_key('d')
        self.last_steering_state = None

# Global instance
steering_controller = None

def get_steering_controller(car):
    """Lấy instance của steering controller"""
    global steering_controller
    if steering_controller is None:
        steering_controller = SteeringController(car)
    return steering_controller