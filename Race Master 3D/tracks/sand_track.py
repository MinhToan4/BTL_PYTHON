"""
Tổng quan về file sand_track.py:

File sand_track.py định nghĩa class SandTrack - đường đua sa mạc trong game Race Master 3D.
Bao gồm model chính, boundaries, walls để phát hiện va chạm, và chi tiết trang trí như xương rồng và đá.
"""

from ursina import *

class SandTrack(Entity):
    """
    Class SandTrack đại diện cho đường đua sa mạc.
    Kế thừa từ Entity để tạo model 3D với collider.
    """
    def __init__(self, car):
        super().__init__(
            model = "sand_track.obj",  # Model chính của đường đua
            texture = "sand_track.png",  # Texture cát
            position = (-80, -50, -75),  # Vị trí
            scale = (18, 18, 18),  # Kích thước
            rotation = (0, 270, 0),  # Xoay
            collider = "mesh"  # Collider dạng mesh
        )

        self.car = car  # Tham chiếu đến xe

        # Đường finish line để phát hiện hoàn thành vòng đua
        self.finish_line = Entity(model = "cube", position = (-50, -50.2, -7), rotation = (0, 0, 0), scale = (3, 8, 30), visible = False)
        
        # Boundaries để phát hiện xe ra ngoài đường đua
        self.boundaries = Entity(model = "sand_track_bounds.obj", collider = "mesh", position = (-80, -50, -75), rotation = (0, 270, 0), scale = (18, 50, 18), visible = False)

        # Các wall để tạo biên giới và logic đặc biệt
        self.wall1 = Entity(model = "cube", position = (-75, -50, -48), rotation = (0, 90, 0), collider = "box", scale = (5, 30, 40), visible = False)
        self.wall2 = Entity(model = "cube", position = (-74, -50, -75), rotation = (0, 90, 0), collider = "box", scale = (5, 30, 40), visible = False)
        self.wall3 = Entity(model = "cube", position = (-61, -50, -60), rotation = (0, 0, 0), collider = "box", scale = (5, 30, 40), visible = False)
        self.wall4 = Entity(model = "cube", position = (-90, -50, -60), rotation = (0, 0, 0), collider = "box", scale = (5, 30, 40), visible = False)

        # Wall trigger để thay đổi logic walls
        self.wall_trigger = Entity(model = "cube", position = (-100, -50, -114), rotation = (0, 0, 0), scale = (5, 20, 30), visible = False)

        # Chi tiết trang trí
        self.cacti = Entity(model = "cacti-sand.obj", texture = "cactus-sand.png", position = (-80, -50, -75), scale = (18, 18, 18), rotation = (0, 270, 0))  # Xương rồng
        self.rocks = Entity(model = "rocks-sand.obj", texture = "rock-sand.png", position = (-80, -50, -75), scale = (18, 18, 18), rotation = (0, 270, 0))  # Đá

        # Danh sách các track elements
        self.track = [
            self.finish_line, self.boundaries, self.wall1, self.wall2, self.wall3, 
            self.wall4, self.wall_trigger
        ]

        # Danh sách chi tiết
        self.details = [
            self.cacti, self.rocks
        ]
        
        self.disable()  # Tắt ban đầu

        # Tắt tất cả elements
        for i in self.track:
            i.disable()
        for i in self.details:
            i.disable()

        self.played = False  # Đã chơi chưa
        self.unlocked = True  # Đã unlock

    def update(self):
        """
        Cập nhật logic đặc biệt của sand track mỗi frame.
        """
        # Kiểm tra xe chạm finish line
        if self.car.simple_intersects(self.finish_line):
            if self.car.anti_cheat == 1:
                self.car.timer_running = True
                self.car.anti_cheat = 0
                if self.car.gamemode != "drift":
                    invoke(self.car.reset_timer, delay = 3)

                self.car.check_highscore()

                # Thay đổi walls
                self.wall1.enable()
                self.wall2.enable()
                self.wall3.disable()
                self.wall4.disable()

        # Kiểm tra xe chạm wall trigger
        if self.car.simple_intersects(self.wall_trigger):
            # Thay đổi walls khác
            self.wall1.disable()
            self.wall2.disable()
            self.wall3.enable()
            self.wall4.enable()
            self.car.anti_cheat = 1