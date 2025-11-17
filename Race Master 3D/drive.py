"""
Module xử lý điều khiển tiến/lùi (W/S) cho xe dựa trên số lượng tay phát hiện được.

Logic điều khiển:
- 2 tay (vị trí trung lập): Tiến (W)
- 1 tay: Lùi (S)
- 0 tay: Không điều khiển
"""

import keyinput

class DriveController:
    """Quản lý điều khiển tiến/lùi bằng cách simulate phím W/S."""
    
    def __init__(self):
        """Khởi tạo drive controller."""
        self.last_drive_state = None

    def update_drive(self, hand_count, hand_positions):
        """
        Cập nhật trạng thái drive dựa trên số tay và vị trí.
        
        Args:
            hand_count: Số tay phát hiện được (0, 1, 2)
            hand_positions: List tọa độ normalized [(x, y), ...] với x, y trong khoảng [0, 1]
        """
        new_drive_state = None

        if hand_count == 2:
            # 2 tay - kiểm tra vị trí để phân biệt tiến hay rẽ
            if hand_positions and len(hand_positions) >= 2:
                avg_x = sum(pos[0] for pos in hand_positions) / len(hand_positions)

                # Vị trí trung lập (0.3-0.7) -> Tiến
                if 0.3 <= avg_x <= 0.7:
                    new_drive_state = 'forward'

        elif hand_count == 1:
            new_drive_state = 'backward'

        # Chỉ thay đổi khi trạng thái khác trước đó để tránh spam
        if new_drive_state != self.last_drive_state:
            if self.last_drive_state == 'forward':
                keyinput.release_key('w')
            elif self.last_drive_state == 'backward':
                keyinput.release_key('s')

            if new_drive_state == 'forward':
                keyinput.press_key('w')
            elif new_drive_state == 'backward':
                keyinput.press_key('s')

            self.last_drive_state = new_drive_state

    def stop_drive(self):
        """Giải phóng tất cả phím drive."""
        keyinput.release_key('w')
        keyinput.release_key('s')
        self.last_drive_state = None


drive_controller = None

def get_drive_controller():
    """
    Lấy hoặc tạo instance singleton của drive controller.
    
    Returns:
        DriveController: Instance duy nhất của drive controller
    """
    global drive_controller
    if drive_controller is None:
        drive_controller = DriveController()
    return drive_controller