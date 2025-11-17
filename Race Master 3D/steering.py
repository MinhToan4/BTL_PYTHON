"""
Module xử lý điều khiển rẽ trái/phải (A/D) cho xe dựa trên vị trí tương đối của 2 tay.

Logic điều khiển:
- 2 tay nghiêng trái: Rẽ trái (A)
- 2 tay nghiêng phải: Rẽ phải (D)
- 1 tay hoặc 2 tay không nghiêng: Không rẽ
"""

import keyinput

class SteeringController:
    """Quản lý điều khiển rẽ trái/phải bằng cách simulate phím A/D."""
    
    def __init__(self, car):
        """
        Khởi tạo steering controller.
        
        Args:
            car: Đối tượng xe (để lấy setting flip_steering)
        """
        self.car = car
        self.last_steering_state = None

    def update_steering(self, hand_count, hand_positions):
        """
        Cập nhật trạng thái steering dựa trên vị trí tương đối của 2 tay.
        
        Args:
            hand_count: Số tay phát hiện được
            hand_positions: List tọa độ pixel [(x, y), ...]
            
        Logic nghiêng:
        - Nghiêng phải: Tay cao hơn nằm bên phải tay thấp hơn (chênh Y > 65px)
        - Nghiêng trái: Tay cao hơn nằm bên trái tay thấp hơn (chênh Y > 65px)
        """
        new_steering_state = None

        if hand_count == 2 and hand_positions and len(hand_positions) >= 2:
            co = hand_positions

            # Nghiêng phải: tay nào có Y lớn hơn (thấp hơn) cũng có X lớn hơn (bên phải)
            if ((co[0][0] > co[1][0] and co[0][1] > co[1][1] and abs(co[0][1] - co[1][1]) > 65) or
                (co[1][0] > co[0][0] and co[1][1] > co[0][1] and abs(co[1][1] - co[0][1]) > 65)):
                new_steering_state = 'right'

            # Nghiêng trái: tay nào có Y lớn hơn (thấp hơn) lại có X nhỏ hơn (bên trái)
            elif ((co[0][0] > co[1][0] and co[1][1] > co[0][1] and abs(co[1][1] - co[0][1]) > 65) or
                  (co[1][0] > co[0][0] and co[0][1] > co[1][1] and abs(co[0][1] - co[1][1]) > 65)):
                new_steering_state = 'left'

        # Áp dụng flip steering nếu được bật trong settings
        if self.car.flip_steering and new_steering_state:
            if new_steering_state == 'left':
                new_steering_state = 'right'
            elif new_steering_state == 'right':
                new_steering_state = 'left'

        # Chỉ thay đổi khi trạng thái khác trước đó
        if new_steering_state != self.last_steering_state:
            if self.last_steering_state == 'left':
                keyinput.release_key('a')
            elif self.last_steering_state == 'right':
                keyinput.release_key('d')

            if new_steering_state == 'left':
                keyinput.press_key('a')
            elif new_steering_state == 'right':
                keyinput.press_key('d')

            self.last_steering_state = new_steering_state

    def stop_steering(self):
        """Giải phóng tất cả phím steering."""
        keyinput.release_key('a')
        keyinput.release_key('d')
        self.last_steering_state = None


steering_controller = None

def get_steering_controller(car):
    """
    Lấy hoặc tạo instance singleton của steering controller.
    
    Args:
        car: Đối tượng xe
        
    Returns:
        SteeringController: Instance duy nhất của steering controller
    """
    global steering_controller
    if steering_controller is None:
        steering_controller = SteeringController(car)
    return steering_controller