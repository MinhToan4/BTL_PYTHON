# Race Master 3D Drive Controller - Xử lý logic tiến/lùi (W/S)
# Cài đặt: pip install mediapipe opencv-python

import keyinput

class DriveController:
    def __init__(self):
        """Khởi tạo drive controller"""
        self.last_drive_state = None  # 'forward', 'backward', hoặc None

    def update_drive(self, hand_count, hand_positions):
        """
        Cập nhật trạng thái drive dựa trên cử chỉ tay

        Args:
            hand_count: Số tay phát hiện được (0, 1, 2)
            hand_positions: List vị trí các tay [(x1,y1), (x2,y2), ...]

        Logic theo yêu cầu:
        - W (tiến): Tay ở vị trí trung lập (không thỏa mãn điều kiện rẽ trái hoặc phải)
        - S (lùi): Chỉ phát hiện được một tay
        """
        new_drive_state = None

        if hand_count == 2:
            # 2 tay - kiểm tra xem có nghiêng trái/phải không
            # Nếu không nghiêng (hoặc nghiêng ít), coi là trung lập -> W
            if hand_positions and len(hand_positions) >= 2:
                # Tính vị trí trung bình
                avg_x = sum(pos[0] for pos in hand_positions) / len(hand_positions)

                # Nếu vị trí trung bình không quá lệch (trong khoảng 0.3-0.7), coi là trung lập
                # Điều này cho phép W được press ngay cả khi tay hơi lệch
                if 0.3 <= avg_x <= 0.7:
                    new_drive_state = 'forward'  # W

        elif hand_count == 1:
            # 1 tay - lùi
            new_drive_state = 'backward'  # S

        # Chỉ thay đổi key press nếu trạng thái thay đổi
        if new_drive_state != self.last_drive_state:
            # Release key cũ
            if self.last_drive_state == 'forward':
                keyinput.release_key('w')
            elif self.last_drive_state == 'backward':
                keyinput.release_key('s')

            # Press key mới
            if new_drive_state == 'forward':
                keyinput.press_key('w')
            elif new_drive_state == 'backward':
                keyinput.press_key('s')

            self.last_drive_state = new_drive_state

    def stop_drive(self):
        """Dừng tất cả drive controls"""
        keyinput.release_key('w')
        keyinput.release_key('s')
        self.last_drive_state = None

# Global instance
drive_controller = None

def get_drive_controller():
    """Lấy instance của drive controller"""
    global drive_controller
    if drive_controller is None:
        drive_controller = DriveController()
    return drive_controller