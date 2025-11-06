"""
Tổng quan về file car.py:

File car.py định nghĩa class Car, là đối tượng xe chính của người chơi trong game Race Master 3D.
Class này kế thừa từ Entity của Ursina và quản lý tất cả logic liên quan đến xe như di chuyển, lái, drift, âm thanh, hiệu ứng hạt, camera, và các chế độ chơi khác nhau (race, time trial, drift).
Cấu trúc chính bao gồm: khởi tạo xe với các thuộc tính vật lý, các phương thức thay đổi loại xe, xử lý input, cập nhật trạng thái mỗi frame, và các tiện ích khác như lưu highscore, multiplayer.
"""

from ursina import *
from ursina import curve
from particles import Particles, TrailRenderer
import os, sys, random, json

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)
Text.default_resolution = 1080 * Text.size


"""
Lý do raycast bị gạch chân đỏ là vì PyCharm (hoặc IDE khác) không nhận diện được hàm raycast từ thư viện Ursina. 
Ursina là một wrapper cho Panda3D, và raycast là hàm được định nghĩa động hoặc không có type hints đầy đủ, nên IDE không thể resolve reference.
Tôi đã thêm comment # type: ignore vào cả hai chỗ gọi raycast (trong __init__ và update). 
Điều này sẽ bỏ qua lỗi unresolved reference cho IDE, nhưng code vẫn chạy bình thường vì raycast là hàm hợp lệ trong Ursina.
"""

class Car(Entity):
    """
    Class Car đại diện cho xe của người chơi, kế thừa từ Entity của Ursina.
    Quản lý vật lý xe, điều khiển, hiệu ứng, âm thanh, và tương tác với game.
    """
    def __init__(self, position=(0, 0, 4), rotation=(0, 0, 0), topspeed=30, acceleration=0.35, braking_strength=30, friction=0.6, camera_speed=8, drift_speed=35):
        """
        Khởi tạo đối tượng Car với các tham số vật lý và thiết lập ban đầu.
        """
        super().__init__(
            model="sports-car.obj",
            texture="sports-red.png",
            collider="box",
            position=position,
            rotation=rotation,
        )

        # ==================== THIẾT LẬP CƠ BẢN ====================
        self.rotation_parent = Entity()  # Entity cha cho rotation

        self.controls = "wasd"  # Phím điều khiển
        self.flip_steering = True  # Lật lái

        # ==================== THUỘC TÍNH VẬT LÝ ====================
        self.speed = 0  # Tốc độ hiện tại
        self.velocity_y = 0  # Vận tốc theo trục Y
        self.rotation_speed = 0  # Tốc độ xoay
        self.max_rotation_speed = 2.6  # Tốc độ xoay tối đa
        self.steering_amount = 8  # Độ lái
        self.topspeed = topspeed  # Tốc độ tối đa
        self.braking_strength = braking_strength  # Sức phanh
        self.camera_speed = camera_speed  # Tốc độ camera
        self.acceleration = acceleration  # Gia tốc
        self.friction = friction  # Ma sát
        self.drift_speed = drift_speed  # Tốc độ drift
        self.drift_amount = 4.5  # Độ drift
        self.turning_speed = 5  # Tốc độ quay
        self.max_drift_speed = 40  # Tốc độ drift tối đa
        self.min_drift_speed = 20  # Tốc độ drift tối thiểu
        self.pivot_rotation_distance = 1  # Khoảng cách xoay pivot

        # ==================== THIẾT LẬP CAMERA ====================
        self.camera_angle = "top"  # Góc camera
        self.camera_offset = (0, 60, -70)  # Offset camera
        self.camera_rotation = 40  # Xoay camera
        self.camera_follow = False  # Camera theo dõi
        self.change_camera = False  # Thay đổi camera
        self.c_pivot = Entity()  # Pivot camera
        self.camera_pivot = Entity(parent=self.c_pivot, position=self.camera_offset)  # Pivot camera con

        self.pivot = Entity()  # Pivot chính
        self.pivot.position = self.position
        self.pivot.rotation = self.rotation
        self.drifting = False  # Đang drift

        self.car_type = "sports"  # Loại xe

        # ==================== HIỆU ỨNG HẠT ====================
        self.particle_time = 0  # Thời gian hạt
        self.particle_amount = 0.07  # Số lượng hạt
        self.particle_pivot = Entity(parent=self)  # Pivot hạt
        self.particle_pivot.position = (0, -1, -2)

        self.trail_pivot = Entity(parent=self, position=(0, -1, 2))  # Pivot trail

        # Trail renderers cho hiệu ứng drift
        self.trail_renderer1 = TrailRenderer(parent=self.particle_pivot, position=(0.8, -0.2, 0), color=color.black, alpha=0, thickness=7, length=200)
        self.trail_renderer2 = TrailRenderer(parent=self.particle_pivot, position=(-0.8, -0.2, 0), color=color.black, alpha=0, thickness=7, length=200)
        self.trail_renderer3 = TrailRenderer(parent=self.trail_pivot, position=(0.8, -0.2, 0), color=color.black, alpha=0, thickness=7, length=200)
        self.trail_renderer4 = TrailRenderer(parent=self.trail_pivot, position=(-0.8, -0.2, 0), color=color.black, alpha=0, thickness=7, length=200)

        self.trails = [self.trail_renderer1, self.trail_renderer2, self.trail_renderer3, self.trail_renderer4]  # Danh sách trails
        self.start_trail = True  # Bắt đầu trail

        # ==================== ÂM THANH ====================
        self.audio = True  # Bật âm thanh
        self.volume = 1  # Âm lượng
        self.start_sound = True  # Bắt đầu âm thanh
        self.start_fall = True  # Bắt đầu rơi
        self.drive_sound = Audio("rally.mp3", loop=True, autoplay=False, volume=0.5)  # Âm lái xe
        self.dirt_sound = Audio("dirt-skid.mp3", loop=True, autoplay=False, volume=0.8)  # Âm trượt đất
        self.skid_sound = Audio("skid.mp3", loop=True, autoplay=False, volume=0.5)  # Âm trượt
        self.hit_sound = Audio("hit.wav", autoplay=False, volume=0.5)  # Âm va chạm
        self.drift_swush = Audio("unlock.mp3", autoplay=False, volume=0.8)  # Âm drift

        # ==================== TRẠNG THÁI ====================
        self.copy_normals = False  # Sao chép normals
        self.hitting_wall = False  # Đang va tường

        # ==================== TRACKS ====================
        self.sand_track = None  # Track cát
        self.grass_track = None  # Track cỏ
        self.snow_track = None  # Track tuyết
        self.forest_track = None  # Track rừng
        self.savannah_track = None  # Track savannah
        self.lake_track = None  # Track hồ

        # ==================== COSMETICS ====================
        self.current_cosmetic = "none"  # Trang phục hiện tại
        self.viking_helmet = Entity(model="viking_helmet.obj", texture="viking_helmet.png", parent=self)  # Mũ Viking
        self.duck = Entity(model="duck.obj", parent=self)  # Vịt
        self.banana = Entity(model="banana.obj", parent=self)  # Chuối
        self.surfinbird = Entity(model="surfinbird.obj", texture="surfinbird.png", parent=self)  # Chim lướt sóng
        self.surfboard = Entity(model="surfboard.obj", texture="surfboard.png", parent=self.surfinbird)  # Ván lướt sóng
        self.cosmetics = [self.viking_helmet, self.duck, self.banana, self.surfinbird]  # Danh sách cosmetics
        self.viking_helmet.disable()  # Tắt mũ Viking
        self.duck.disable()  # Tắt vịt
        self.banana.disable()  # Tắt chuối
        self.surfinbird.disable()  # Tắt chim lướt sóng

        self.graphics = "fancy"  # Chất lượng đồ họa

        # ==================== TIMER VÀ HIGHSCORE ====================
        self.timer_running = False  # Timer đang chạy
        self.count = 0.0  # Đếm thời gian
        self.highscore_count = None  # Highscore
        self.last_count = self.count  # Lần đếm cuối
        self.reset_count = 0.0  # Reset đếm
        self.timer = Text(text="", origin=(0, 0), size=0.05, scale=(1, 1), position=(-0.7, 0.43))  # Text timer
        self.highscore = Text(text="", origin=(0, 0), size=0.05, scale=(0.6, 0.6), position=(-0.7, 0.38))  # Text highscore
        self.laps_text = Text(text="", origin=(0, 0), size=0.05, scale=(1.1, 1.1), position=(0, 0.43))  # Text vòng đua
        self.reset_count_timer = Text(text=str(round(self.reset_count, 1)), origin=(0, 0), size=0.05, scale=(1, 1), position=(-0.7, 0.43))  # Text reset timer

        self.timer.disable()  # Tắt timer
        self.highscore.disable()  # Tắt highscore
        self.laps_text.disable()  # Tắt laps
        self.reset_count_timer.disable()  # Tắt reset timer

        # ==================== CHẾ ĐỘ CHƠI ====================
        self.gamemode = "race"  # Chế độ chơi
        self.start_time = False  # Bắt đầu thời gian
        self.laps = 0  # Số vòng
        self.laps_hs = 0  # Highscore vòng
        self.anti_cheat = 1  # Chống cheat

        # ==================== DRIFT ====================
        self.drift_text = Text(text="", origin=(0, 0), color=color.white, size=0.05, scale=(1.1, 1.1), position=(0, 0.43), visible=False)  # Text drift
        self.drift_timer = Text(text="", origin=(0, 0), size=0.05, scale=(1, 1), position=(0.7, 0.43))  # Timer drift
        self.start_drift = False  # Bắt đầu drift
        self.drift_score = 0  # Điểm drift
        self.drift_time = 0  # Thời gian drift
        self.drift_multiplier = 20  # Nhân drift
        self.get_hundred = False  # Đạt 100
        self.get_thousand = False  # Đạt 1000
        self.get_fivethousand = False  # Đạt 5000

        # ==================== TRẠNG THÁI LÁI ====================
        self.driving = False  # Đang lái
        self.braking = False  # Đang phanh

        # ==================== AI VÀ MULTIPLAYER ====================
        self.ai = False  # Là AI
        self.ai_list = []  # Danh sách AI

        self.multiplayer = False  # Chơi mạng
        self.multiplayer_update = False  # Cập nhật mạng
        self.server_running = False  # Server đang chạy

        self.connected_text = True  # Text kết nối
        self.disconnected_text = True  # Text ngắt kết nối

        # ==================== CAMERA SHAKE ====================
        self.shake_amount = 0.1  # Độ rung
        self.can_shake = False  # Có thể rung
        self.camera_shake_option = True  # Tùy chọn rung camera

        # ==================== HIGHSCORE VÀ UNLOCKED ====================
        path = os.path.dirname(sys.argv[0])  # Đường dẫn
        self.highscore_path = os.path.join(path, "./highscore/highscore.json")  # Đường dẫn highscore

        try:
            with open(self.highscore_path, "r") as hs:
                self.highscores = json.load(hs)  # Tải highscore
        except FileNotFoundError:
            with open(self.highscore_path, "w+") as hs:
                self.reset_highscore()  # Reset highscore
                self.highscores = json.load(hs)

        # Gán highscore cho từng track
        self.sand_track_hs = self.highscores["race"]["sand_track"]
        self.grass_track_hs = self.highscores["race"]["grass_track"]
        self.snow_track_hs = self.highscores["race"]["snow_track"]
        self.forest_track_hs = self.highscores["race"]["forest_track"]
        self.savannah_track_hs = self.highscores["race"]["savannah_track"]
        self.lake_track_hs = self.highscores["race"]["lake_track"]

        self.sand_track_laps = self.highscores["time_trial"]["sand_track"]
        self.grass_track_laps = self.highscores["time_trial"]["grass_track"]
        self.snow_track_laps = self.highscores["time_trial"]["snow_track"]
        self.forest_track_laps = self.highscores["time_trial"]["forest_track"]
        self.savannah_track_laps = self.highscores["time_trial"]["savannah_track"]
        self.lake_track_laps = self.highscores["time_trial"]["lake_track"]

        self.sand_track_drift = self.highscores["drift"]["sand_track"]
        self.grass_track_drift = self.highscores["drift"]["grass_track"]
        self.snow_track_drift = self.highscores["drift"]["snow_track"]
        self.forest_track_drift = self.highscores["drift"]["forest_track"]
        self.savannah_track_drift = self.highscores["drift"]["savannah_track"]
        self.lake_track_drift = self.highscores["drift"]["lake_track"]

        self.highscore_count = float(self.sand_track_hs)  # Highscore hiện tại

        # ==================== USERNAME ====================
        self.username_path = os.path.join(path, "./highscore/username.txt")  # Đường dẫn username
        try:
            with open(self.username_path, "r") as username:
                self.username_text = username.read()  # Đọc username
        except FileNotFoundError:
            self.username_text = "Guest"  # Mặc định Guest

        # ==================== UNLOCKED ====================
        self.unlocked_json = os.path.join(path, "./highscore/unlocked.json")  # Đường dẫn unlocked
        try:
            with open(self.unlocked_json, "r") as u:
                self.unlocked = json.load(u)  # Tải unlocked
        except FileNotFoundError:
            with open(self.unlocked_json, "w+") as u:
                self.save_unlocked()  # Lưu unlocked
                self.unlocked = json.load(u)

        # ==================== BEAT MANDAW ====================
        self.beat_mandaw_sand_track = False  # Đánh bại Mandaw trên sand track
        self.beat_mandaw_grass_track = False
        self.beat_mandaw_snow_track = False
        self.beat_mandaw_forest_track = False
        self.beat_mandaw_savannah_track = False
        self.beat_mandaw_lake_track = False

        self.model_path = str(self.model).replace("render/scene/car/", "")  # Đường dẫn model

        self.hand_controller = None  # Điều khiển tay

        self.for_developer = True  # Cho developer, unlock tất cả

        invoke(self.set_unlocked, delay=1)  # Thiết lập unlocked sau 1 giây
        invoke(self.update_model_path, delay=3)  # Cập nhật model path sau 3 giây

    # --- tiện ích âm lượng an toàn ---
    def set_safe_volume(self, sound, volume):
        sound.volume = max(0.0, min(1.0, float(volume)))

    def sports_car(self):
        self.car_type = "sports"
        self.model = "sports-car.obj"
        self.texture = "sports-red.png"
        self.drive_sound.clip = "sports.mp3"
        self.topspeed = 30
        self.acceleration = 0.38
        self.drift_amount = 5
        self.turning_speed = 5
        self.min_drift_speed = 18
        self.max_drift_speed = 38
        self.max_rotation_speed = 3
        self.steering_amount = 8
        self.particle_pivot.position = (0, -1, -1.5)
        self.trail_pivot.position = (0, -1, 1.5)
        for cosmetic in self.cosmetics:
            cosmetic.y = 0

    def muscle_car(self):
        self.car_type = "muscle"
        self.model = "muscle-car.obj"
        self.texture = "muscle-orange.png"
        self.drive_sound.clip = "muscle.mp3"
        self.topspeed = 38
        self.acceleration = 0.32
        self.drift_amount = 6
        self.turning_speed = 10
        self.min_drift_speed = 22
        self.max_drift_speed = 40
        self.max_rotation_speed = 3
        self.steering_amount = 8.5
        self.particle_pivot.position = (0, -1, -1.8)
        self.trail_pivot.position = (0, -1, 1.8)
        for cosmetic in self.cosmetics:
            cosmetic.y = 0

    def limo(self):
        self.car_type = "limo"
        self.model = "limousine.obj"
        self.texture = "limo-black.png"
        self.drive_sound.clip = "limo.mp3"
        self.topspeed = 30
        self.acceleration = 0.33
        self.drift_amount = 5.5
        self.turning_speed = 8
        self.min_drift_speed = 20
        self.max_drift_speed = 40
        self.max_rotation_speed = 3
        self.steering_amount = 8
        self.particle_pivot.position = (0, -1, -3.5)
        self.trail_pivot.position = (0, -1, 3.5)
        for cosmetic in self.cosmetics:
            cosmetic.y = 0.1

    def lorry(self):
        self.car_type = "lorry"
        self.model = "lorry.obj"
        self.texture = "lorry-white.png"
        self.drive_sound.clip = "lorry.mp3"
        self.topspeed = 30
        self.acceleration = 0.3
        self.drift_amount = 7
        self.turning_speed = 7
        self.min_drift_speed = 20
        self.max_drift_speed = 40
        self.max_rotation_speed = 3
        self.steering_amount = 7.5
        self.particle_pivot.position = (0, -1, -3.5)
        self.trail_pivot.position = (0, -1, 3.5)
        for cosmetic in self.cosmetics:
            cosmetic.y = 1.5

    def hatchback(self):
        self.car_type = "hatchback"
        self.model = "hatchback.obj"
        self.texture = "hatchback-green.png"
        self.drive_sound.clip = "hatchback.mp3"
        self.topspeed = 28
        self.acceleration = 0.43
        self.drift_amount = 6
        self.turning_speed = 15
        self.min_drift_speed = 20
        self.max_drift_speed = 40
        self.max_rotation_speed = 3
        self.steering_amount = 8.5
        self.particle_pivot.position = (0, -1, -1.5)
        self.trail_pivot.position = (0, -1, 1.5)
        for cosmetic in self.cosmetics:
            cosmetic.y = 0.4

    def rally_car(self):
        self.car_type = "rally"
        self.model = "rally-car.obj"
        self.texture = "rally-red.png"
        self.drive_sound.clip = "rally.mp3"
        self.topspeed = 34
        self.acceleration = 0.46
        self.drift_amount = 4
        self.turning_speed = 7
        self.min_drift_speed = 22
        self.max_drift_speed = 40
        self.max_rotation_speed = 3
        self.steering_amount = 8.5
        self.particle_pivot.position = (0, -1, -1.5)
        self.trail_pivot.position = (0, -1, 1.5)
        for cosmetic in self.cosmetics:
            cosmetic.y = 0.3

    def update(self):
        if self.gamemode == "race":
            self.highscore.text = str(round(self.highscore_count, 1))
            self.laps_text.disable()
            if self.timer_running:
                self.count += time.dt
                self.reset_count += time.dt
        elif self.gamemode == "time trial":
            self.highscore.text = str(self.laps_hs)
            self.laps_text.text = str(self.laps)
            if self.timer_running:
                self.count -= time.dt
                self.reset_count -= time.dt
                if self.count <= 0.0:
                    self.count = 100.0
                    self.reset_count = 100.0
                    self.timer_running = False

                    if self.laps >= self.laps_hs:
                        self.laps_hs = self.laps

                    self.laps = 0

                    if self.sand_track and self.sand_track.enabled:
                        self.sand_track_laps = self.laps_hs
                    elif self.grass_track and self.grass_track.enabled:
                        self.grass_track_laps = self.laps_hs
                    elif self.snow_track and self.snow_track.enabled:
                        self.snow_track_laps = self.laps_hs
                    elif self.forest_track and self.forest_track.enabled:
                        self.forest_track_laps = self.laps_hs
                    elif self.savannah_track and self.savannah_track.enabled:
                        self.savannah_track_laps = self.laps_hs
                    elif self.lake_track and self.lake_track.enabled:
                        self.lake_track_laps = self.laps_hs

                    self.start_time = False

                    self.save_highscore()
                    self.reset_car()
        elif self.gamemode == "drift":
            self.timer.text = str(int(self.drift_score))
            self.drift_text.text = str(int(self.count))
            self.drift_timer.text = str(float(round(self.drift_time, 1)))
            self.laps_text.disable()
            if self.timer_running:
                self.drift_time -= time.dt
                if self.drifting and held_keys["w"]:
                    self.count += self.drift_multiplier * time.dt
                    self.drift_multiplier += time.dt * 10
                    self.start_drift = True
                    self.drift_text.visible = True
                    self.drift_text.x = 0

                    if abs(100 - self.count) <= 5 or abs(200 - self.count) <= 20:
                        if not self.get_hundred:
                            self.animate_text(self.drift_text, 1.7, 1.1)
                            self.get_hundred = True
                    if abs(1000 - self.count) <= 10 or abs(2000 - self.count) <= 50:
                        if not self.get_thousand:
                            self.animate_text(self.drift_text, 1.7, 1.1)
                            self.get_thousand = True
                    if abs(5000 - self.count) <= 20 or abs(10000 - self.count) <= 100:
                        if not self.get_fivethousand:
                            self.animate_text(self.drift_text, 1.7, 1.1)
                            self.get_fivethousand = True

                    if 100 <= self.count < 1000:
                        self.drift_text.color = color.hex("#6eb1ff")
                    elif 1000 <= self.count < 5000:
                        self.drift_text.color = color.gold
                    elif self.count >= 5000:
                        self.drift_text.color = color.red
                    else:
                        self.drift_text.color = color.white
                else:
                    if self.start_drift:
                        self.reset_drift()
                        self.start_drift = False
                if self.drift_time <= 0:
                    self.drift_timer.shake()
                    self.reset_car()

        if self.gamemode != "drift":
            self.timer.text = str(round(self.count, 1))
            self.reset_count_timer.text = str(round(self.reset_count, 1))
        else:
            self.reset_count_timer.text = str(int(self.reset_count))

        self.pivot.position = self.position
        self.c_pivot.position = self.position
        self.c_pivot.rotation_y = self.rotation_y
        self.camera_pivot.position = self.camera_offset

        if self.camera_follow:
            if self.camera_angle == "side":
                camera.rotation = (35, -20, 0)
                self.camera_speed = 8
                self.change_camera = False
                camera.world_position = lerp(camera.world_position, self.world_position + (20, 40, -50), time.dt * self.camera_speed)
            elif self.camera_angle == "top":
                if self.change_camera:
                    camera.rotation_x = 35
                    self.camera_rotation = 40
                self.camera_offset = (0, 60, -70)
                self.camera_speed = 4
                self.change_camera = False
                camera.rotation_x = lerp(camera.rotation_x, self.camera_rotation, 2 * time.dt)
                camera.world_position = lerp(camera.world_position, self.camera_pivot.world_position, time.dt * self.camera_speed / 2)
                camera.world_rotation_y = lerp(camera.world_rotation_y, self.world_rotation_y, time.dt * self.camera_speed / 2)
            elif self.camera_angle == "behind":
                if self.change_camera:
                    camera.rotation_x = 12
                    self.camera_rotation = 40
                self.camera_offset = (0, 10, -30)
                self.change_camera = False
                self.camera_speed = 8
                camera.rotation_x = lerp(camera.rotation_x, self.camera_rotation / 3, 2 * time.dt)
                camera.world_position = lerp(camera.world_position, self.camera_pivot.world_position, time.dt * self.camera_speed / 2)
                camera.world_rotation_y = lerp(camera.world_rotation_y, self.world_rotation_y, time.dt * self.camera_speed / 2)
            elif self.camera_angle == "first-person":
                self.change_camera = False
                self.camera_speed = 8
                camera.world_position = lerp(camera.world_position, self.world_position + (0.5, 0, 0), time.dt * 30)
                camera.world_rotation = lerp(camera.world_rotation, self.world_rotation, time.dt * 30)

        self.pivot_rotation_distance = (self.rotation_y - self.pivot.rotation_y)

        if self.pivot.rotation_y != self.rotation_y:
            if self.pivot.rotation_y > self.rotation_y:
                self.pivot.rotation_y -= (self.drift_speed * ((self.pivot.rotation_y - self.rotation_y) / 40)) * time.dt
                if self.speed > 1 or self.speed < -1:
                    self.speed += self.pivot_rotation_distance / self.drift_amount * time.dt
                self.camera_rotation -= self.pivot_rotation_distance / 3 * time.dt
                self.rotation_speed -= 1 * time.dt
                if self.pivot_rotation_distance >= 50 or self.pivot_rotation_distance <= -50:
                    self.drift_speed += self.pivot_rotation_distance / 5 * time.dt
                else:
                    self.drift_speed -= self.pivot_rotation_distance / 5 * time.dt
            if self.pivot.rotation_y < self.rotation_y:
                self.pivot.rotation_y += (self.drift_speed * ((self.rotation_y - self.pivot.rotation_y) / 40)) * time.dt
                if self.speed > 1 or self.speed < -1:
                    self.speed -= self.pivot_rotation_distance / self.drift_amount * time.dt
                self.camera_rotation += self.pivot_rotation_distance / 3 * time.dt
                self.rotation_speed += 1 * time.dt
                if self.pivot_rotation_distance >= 50 or self.pivot_rotation_distance <= -50:
                    self.drift_speed -= self.pivot_rotation_distance / 5 * time.dt
                else:
                    self.drift_speed += self.pivot_rotation_distance / 5 * time.dt

        movementY = self.velocity_y / 50
        direction = (0, sign(movementY), 0)

        y_ray = raycast(origin=self.world_position, direction=(0, -1, 0), ignore=[self, ]) # type: ignore

        if y_ray.distance <= 5:
            if held_keys[self.controls[0]] or held_keys["up arrow"] or (self.hand_controller and self.hand_controller.get_controls()['forward']):
                self.speed += self.acceleration * 50 * time.dt
                self.speed += -self.velocity_y * 4 * time.dt

                self.camera_rotation -= self.acceleration * 30 * time.dt
                self.driving = True

                self.particle_time += time.dt
                if self.particle_time >= self.particle_amount:
                    self.particle_time = 0
                    self.particles = Particles(self, self.particle_pivot.world_position - (0, 1, 0))
                    self.particles.destroy(1)

                if self.graphics != "ultra fast":
                    if self.drift_speed <= self.min_drift_speed + 2 and self.start_trail:
                        if (self.pivot_rotation_distance > 60 or self.pivot_rotation_distance < -60) and self.speed > 10:
                            for trail in self.trails:
                                trail.start_trail()
                            if self.audio:
                                self.set_safe_volume(self.skid_sound, self.volume / 2)
                                self.skid_sound.play()
                            self.start_trail = False
                            self.drifting = True
                        else:
                            self.drifting = False
                    elif self.drift_speed > self.min_drift_speed + 2 and not self.start_trail:
                        if self.pivot_rotation_distance < 60 or self.pivot_rotation_distance > -60:
                            for trail in self.trails:
                                if trail.trailing:
                                    trail.end_trail()
                            if self.audio:
                                self.skid_sound.stop(False)
                            self.start_trail = True
                            self.drifting = False
                        self.drifting = False
                    if self.speed < 10:
                        self.drifting = False
            else:
                self.driving = False
                if self.speed > 1:
                    self.speed -= self.friction * 5 * time.dt
                elif self.speed < -1:
                    self.speed += self.friction * 5 * time.dt
                self.camera_rotation += self.friction * 20 * time.dt

            # --- SỬA NGOẶC Ở ĐIỀU KIỆN PHANH ---
            if held_keys[self.controls[2]] or held_keys["down arrow"] or (self.hand_controller and self.hand_controller.get_controls()['backward']):
                self.speed -= self.braking_strength * time.dt
                self.drift_speed -= 20 * time.dt
                self.braking = True
            else:
                self.braking = False

            if self.driving or self.braking:
                if self.start_sound and self.audio:
                    if not self.drive_sound.playing:
                        self.drive_sound.loop = True
                        self.drive_sound.play()
                    if not self.dirt_sound.playing:
                        self.dirt_sound.loop = True  # sửa đúng biến
                        self.dirt_sound.play()
                    self.start_sound = False

                if self.speed != 0:
                    self.set_safe_volume(self.drive_sound, abs(self.speed) / 80 * self.volume)

                if self.pivot_rotation_distance != 0:
                    self.set_safe_volume(self.dirt_sound, abs(self.pivot_rotation_distance) / 110 * self.volume)
            else:
                self.set_safe_volume(self.drive_sound, self.drive_sound.volume - 0.5 * time.dt)
                self.set_safe_volume(self.dirt_sound, self.dirt_sound.volume - 0.5 * time.dt)
                if self.skid_sound.playing:
                    self.skid_sound.stop(False)

            if held_keys["space"]:
                if self.rotation_speed < 0:
                    self.rotation_speed -= 3 * time.dt
                elif self.rotation_speed > 0:
                    self.rotation_speed += 3 * time.dt
                self.drift_speed -= 40 * time.dt
                self.speed -= 20 * time.dt
                self.max_rotation_speed = 3.0

        if self.graphics != "ultra fast":
            if y_ray.distance > 2.5:
                if self.trail_renderer1.trailing:
                    for trail in self.trails:
                        trail.end_trail()
                    self.start_trail = True

        self.rotation_y += self.rotation_speed * 50 * time.dt

        if self.rotation_speed > 0:
            self.rotation_speed -= self.speed / 6 * time.dt
        elif self.rotation_speed < 0:
            self.rotation_speed += self.speed / 6 * time.dt

        if self.speed > 1 or self.speed < -1:
            if held_keys[self.controls[1]] or held_keys["left arrow"] or (self.hand_controller and self.hand_controller.get_controls()['left']):
                self.rotation_speed -= self.steering_amount * time.dt
                self.drift_speed -= 5 * time.dt
                if self.speed > 1:
                    self.speed -= self.turning_speed * time.dt
                elif self.speed < 0:
                    self.speed += self.turning_speed / 5 * time.dt
            elif held_keys[self.controls[3]] or held_keys["right arrow"] or (self.hand_controller and self.hand_controller.get_controls()['right']):
                self.rotation_speed += self.steering_amount * time.dt
                self.drift_speed -= 5 * time.dt
                if self.speed > 1:
                    self.speed -= self.turning_speed * time.dt
                elif self.speed < 0:
                    self.speed += self.turning_speed / 5 * time.dt
            else:
                self.drift_speed += 15 * time.dt
                if self.rotation_speed > 0:
                    self.rotation_speed -= 5 * time.dt
                elif self.rotation_speed < 0:
                    self.rotation_speed += 5 * time.dt
        else:
            self.rotation_speed = 0

        if self.speed >= self.topspeed:
            self.speed = self.topspeed
        if self.speed <= -15:
            self.speed = -15
        if self.speed <= 0:
            self.pivot.rotation_y = self.rotation_y

        if self.drift_speed <= self.min_drift_speed:
            self.drift_speed = self.min_drift_speed
        if self.drift_speed >= self.max_drift_speed:
            self.drift_speed = self.max_drift_speed

        if self.rotation_speed >= self.max_rotation_speed:
            self.rotation_speed = self.max_rotation_speed
        if self.rotation_speed <= -self.max_rotation_speed:
            self.rotation_speed = -self.max_rotation_speed

        if held_keys["g"]:
            self.reset_car()

        if self.y <= -100:
            self.reset_car()

        if self.y >= 300:
            self.reset_car()

        if self.camera_rotation >= 40:
            self.camera_rotation = 40
        elif self.camera_rotation <= 30:
            self.camera_rotation = 30

        if self.speed >= 1 and self.driving:
            self.can_shake = True
            if self.pivot_rotation_distance > 0:
                self.shake_amount = self.speed * self.pivot_rotation_distance / 200
            elif self.pivot_rotation_distance < 0:
                self.shake_amount = self.speed * -self.pivot_rotation_distance / 200
        else:
            self.can_shake = False

        if self.shake_amount <= 0:
            self.shake_amount = 0
        if self.shake_amount >= 0.03:
            self.shake_amount = 0.03

        if self.can_shake and self.camera_shake_option and self.camera_angle != "first-person":
            self.shake_camera()

        self.rotation_parent.position = self.position

        self.rotation_x = lerp(self.rotation_x, self.rotation_parent.rotation_x, 20 * time.dt)
        self.rotation_z = lerp(self.rotation_z, self.rotation_parent.rotation_z, 20 * time.dt)

        if self.visible:
            if y_ray.distance <= self.scale_y * 1.7 + abs(movementY):
                self.velocity_y = 0
                if y_ray.world_normal.y > 0.7 and y_ray.world_point.y - self.world_y < 0.5:
                    self.y = y_ray.world_point.y + 1.4
                    self.hitting_wall = False
                else:
                    self.hitting_wall = True

                if self.copy_normals:
                    self.ground_normal = self.position + y_ray.world_normal
                else:
                    self.ground_normal = self.position + (0, 180, 0)

                if not self.hitting_wall:
                    self.rotation_parent.look_at(self.ground_normal, axis="up")
                    self.rotation_parent.rotation = (0, self.rotation_y + 180, 0)
                else:
                    self.rotation_parent.rotation = self.rotation

                if self.start_fall and self.audio:
                    self.set_safe_volume(self.hit_sound, self.volume / 2)
                    self.hit_sound.play()
                    self.start_fall = False
            else:
                self.y += movementY * 50 * time.dt
                self.velocity_y -= 50 * time.dt
                self.rotation_parent.rotation = self.rotation
                self.start_fall = True

        movementX = self.pivot.forward[0] * self.speed * time.dt
        movementZ = self.pivot.forward[2] * self.speed * time.dt

        if movementX != 0:
            direction = (sign(movementX), 0, 0)
            x_ray = raycast(origin=self.world_position, direction=direction, ignore=[self, ]) # type: ignore
            if x_ray.distance > self.scale_x / 2 + abs(movementX):
                self.x += movementX

        if movementZ != 0:
            direction = (0, 0, sign(movementZ))
            z_ray = raycast(origin=self.world_position, direction=direction, ignore=[self, ]) # type: ignore
            if z_ray.distance > self.scale_z / 2 + abs(movementZ):
                self.z += movementZ

    def reset_car(self):
        if self.sand_track and self.sand_track.enabled:
            self.position = (-63, -40, -7)
            self.rotation = (0, 90, 0)
        elif self.grass_track and self.grass_track.enabled:
            self.position = (-80, -30, 18.5)
            self.rotation = (0, 90, 0)
        elif self.snow_track and self.snow_track.enabled:
            self.position = (-5, -35, 93)
            self.rotation = (0, 90, 0)
        elif self.forest_track and self.forest_track.enabled:
            self.position = (12, -35, 76)
            self.rotation = (0, 90, 0)
        elif self.savannah_track and self.savannah_track.enabled:
            self.position = (-14, -35, 42)
            self.rotation = (0, 90, 0)
        elif self.lake_track and self.lake_track.enabled:
            self.position = (-121, -40, 158)
            self.rotation = (0, 90, 0)
        camera.world_rotation_y = self.rotation_y
        self.speed = 0
        self.velocity_y = 0
        self.anti_cheat = 1
        self.timer_running = False
        if self.gamemode == "race":
            self.count = 0.0
            self.reset_count = 0.0
        elif self.gamemode == "time trial":
            self.count = 100.0
            self.reset_count = 100.0
            self.laps = 0
            self.start_time = False
        elif self.gamemode == "drift":
            self.reset_drift_score()
        for trail in self.trails:
            if trail.trailing:
                trail.end_trail()
        self.start_trail = True
        self.start_sound = True
        if self.audio:
            if self.skid_sound.playing:
                self.skid_sound.stop(False)
            if self.dirt_sound.playing:
                self.dirt_sound.stop(False)

    def simple_intersects(self, entity):
        minXA = self.x - self.scale_x
        maxXA = self.x + self.scale_x
        minYA = self.y - self.scale_y + (self.scale_y / 2)
        maxYA = self.y + self.scale_y - (self.scale_y / 2)
        minZA = self.z - self.scale_z
        maxZA = self.z + self.scale_z

        minXB = entity.x - entity.scale_x + (entity.scale_x / 2)
        maxXB = entity.x + entity.scale_x - (entity.scale_x / 2)
        minYB = entity.y - entity.scale_y + (entity.scale_y / 2)
        maxYB = entity.y + entity.scale_y - (entity.scale_y / 2)
        minZB = entity.z - entity.scale_z + (entity.scale_z / 2)
        maxZB = entity.z + entity.scale_z - (entity.scale_z / 2)

        return (
            (minXA <= maxXB and maxXA >= minXB) and
            (minYA <= maxYB and maxYA >= minYB) and
            (minZA <= maxZB and maxZA >= minZB)
        )

    def check_highscore(self):
        if self.gamemode == "race":
            self.last_count = self.count
            self.reset_count = 0.0
            self.timer.disable()
            self.reset_count_timer.enable()

            if self.highscore_count == 0:
                if self.last_count >= 5:
                    self.highscore_count = self.last_count
                    self.animate_text(self.highscore)
            if self.last_count <= self.highscore_count and self.last_count != 0:
                if self.last_count >= 5:
                    self.highscore_count = self.last_count
                    self.animate_text(self.highscore)
                if self.highscore_count <= 6:
                    self.highscore_count = self.last_count
                    self.animate_text(self.highscore)

            if self.sand_track and self.sand_track.enabled:
                self.sand_track_hs = float(self.highscore_count)
            elif self.grass_track and self.grass_track.enabled:
                self.grass_track_hs = float(self.highscore_count)
            elif self.snow_track and self.snow_track.enabled:
                self.snow_track_hs = float(self.highscore_count)
            elif self.forest_track and self.forest_track.enabled:
                self.forest_track_hs = float(self.highscore_count)
            elif self.savannah_track and self.savannah_track.enabled:
                self.savannah_track_hs = float(self.highscore_count)
            elif self.lake_track and self.lake_track.enabled:
                self.lake_track_hs = float(self.highscore_count)
            self.save_highscore()

        elif self.gamemode == "time trial":
            self.last_count = self.count
            if self.start_time:
                self.laps += 1
                self.animate_text(self.laps_text, 1.7, 1.1)
            self.start_time = True

        elif self.gamemode == "drift":
            self.drift_score += self.count

            if self.drift_score >= self.highscore_count:
                self.highscore_count = self.drift_score
                if self.highscore_count != 0:
                    self.animate_text(self.highscore)

            self.reset_count = self.drift_score
            self.reset_count_timer.enable()
            self.timer.disable()
            invoke(self.reset_count_timer.disable, delay=3)
            invoke(self.timer.enable, delay=3)

            self.reset_drift_score()

            self.highscore.text = str(int(self.highscore_count))

            if self.sand_track and self.sand_track.enabled:
                self.sand_track_drift = int(self.highscore_count)
            elif self.grass_track and self.grass_track.enabled:
                self.grass_track_drift = int(self.highscore_count)
            elif self.snow_track and self.snow_track.enabled:
                self.snow_track_drift = int(self.highscore_count)
            elif self.forest_track and self.forest_track.enabled:
                self.forest_track_drift = int(self.highscore_count)
            elif self.savannah_track and self.savannah_track.enabled:
                self.savannah_track_drift = int(self.highscore_count)
            elif self.lake_track and self.lake_track.enabled:
                self.lake_track_drift = int(self.highscore_count)

            self.save_highscore()

    def save_highscore(self):
        self.highscore_dict = {
            "race": {
                "sand_track": self.sand_track_hs,
                "grass_track": self.grass_track_hs,
                "snow_track": self.snow_track_hs,
                "forest_track": self.forest_track_hs,
                "savannah_track": self.savannah_track_hs,
                "lake_track": self.lake_track_hs
            },

            "time_trial": {
                "sand_track": self.sand_track_laps,
                "grass_track": self.grass_track_laps,
                "snow_track": self.snow_track_laps,
                "forest_track": self.forest_track_laps,
                "savannah_track": self.savannah_track_laps,
                "lake_track": self.lake_track_laps
            },

            "drift": {
                "sand_track": self.sand_track_drift,
                "grass_track": self.grass_track_drift,
                "snow_track": self.snow_track_drift,
                "forest_track": self.forest_track_drift,
                "savannah_track": self.savannah_track_drift,
                "lake_track": self.lake_track_drift
            }
        }

        with open(self.highscore_path, "w") as hs:
            json.dump(self.highscore_dict, hs, indent=4)

    def reset_highscore(self):
        self.sand_track_hs = 0.0
        self.grass_track_hs = 0.0
        self.snow_track_hs = 0.0
        self.forest_track_hs = 0.0
        self.savannah_track_hs = 0.0
        self.lake_track_hs = 0.0

        self.sand_track_laps = 0
        self.grass_track_laps = 0
        self.snow_track_laps = 0
        self.forest_track_laps = 0
        self.savannah_track_laps = 0
        self.lake_track_laps = 0

        self.sand_track_drift = 0.0
        self.grass_track_drift = 0.0
        self.snow_track_drift = 0.0
        self.forest_track_drift = 0.0
        self.savannah_track_drift = 0.0
        self.lake_track_drift = 0.0

        self.save_highscore()

    def set_unlocked(self):
        self.sand_track.unlocked = self.unlocked["tracks"]["sand_track"]
        self.grass_track.unlocked = self.unlocked["tracks"]["grass_track"]
        self.snow_track.unlocked = self.unlocked["tracks"]["snow_track"]
        self.forest_track.unlocked = self.unlocked["tracks"]["forest_track"]
        self.savannah_track.unlocked = self.unlocked["tracks"]["savannah_track"]
        self.lake_track.unlocked = self.unlocked["tracks"]["lake_track"]

        self.beat_mandaw_sand_track = self.unlocked["beat_mandaw"]["sand_track"]
        self.beat_mandaw_grass_track = self.unlocked["beat_mandaw"]["grass_track"]
        self.beat_mandaw_snow_track = self.unlocked["beat_mandaw"]["snow_track"]
        self.beat_mandaw_forest_track = self.unlocked["beat_mandaw"]["forest_track"]
        self.beat_mandaw_savannah_track = self.unlocked["beat_mandaw"]["savannah_track"]
        self.beat_mandaw_lake_track = self.unlocked["beat_mandaw"]["lake_track"]

        self.sports_unlocked = self.unlocked["cars"]["sports_car"]
        self.muscle_unlocked = self.unlocked["cars"]["muscle_car"]
        self.limo_unlocked = self.unlocked["cars"]["limo"]
        self.lorry_unlocked = self.unlocked["cars"]["lorry"]
        self.hatchback_unlocked = self.unlocked["cars"]["hatchback"]
        self.rally_unlocked = self.unlocked["cars"]["rally_car"]

        self.sports_red_unlocked = self.unlocked["textures"]["sports_car"]["red"]
        self.sports_blue_unlocked = self.unlocked["textures"]["sports_car"]["blue"]
        self.sports_green_unlocked = self.unlocked["textures"]["sports_car"]["green"]
        self.sports_orange_unlocked = self.unlocked["textures"]["sports_car"]["orange"]
        self.sports_black_unlocked = self.unlocked["textures"]["sports_car"]["black"]
        self.sports_white_unlocked = self.unlocked["textures"]["sports_car"]["white"]

        self.muscle_red_unlocked = self.unlocked["textures"]["muscle_car"]["red"]
        self.muscle_blue_unlocked = self.unlocked["textures"]["muscle_car"]["blue"]
        self.muscle_green_unlocked = self.unlocked["textures"]["muscle_car"]["green"]
        self.muscle_orange_unlocked = self.unlocked["textures"]["muscle_car"]["orange"]
        self.muscle_black_unlocked = self.unlocked["textures"]["muscle_car"]["black"]
        self.muscle_white_unlocked = self.unlocked["textures"]["muscle_car"]["white"]

        self.limo_red_unlocked = self.unlocked["textures"]["limo"]["red"]
        self.limo_blue_unlocked = self.unlocked["textures"]["limo"]["blue"]
        self.limo_green_unlocked = self.unlocked["textures"]["limo"]["green"]
        self.limo_orange_unlocked = self.unlocked["textures"]["limo"]["orange"]
        self.limo_black_unlocked = self.unlocked["textures"]["limo"]["black"]
        self.limo_white_unlocked = self.unlocked["textures"]["limo"]["white"]

        self.lorry_red_unlocked = self.unlocked["textures"]["lorry"]["red"]
        self.lorry_blue_unlocked = self.unlocked["textures"]["lorry"]["blue"]
        self.lorry_green_unlocked = self.unlocked["textures"]["lorry"]["green"]
        self.lorry_orange_unlocked = self.unlocked["textures"]["lorry"]["orange"]
        self.lorry_black_unlocked = self.unlocked["textures"]["lorry"]["black"]
        self.lorry_white_unlocked = self.unlocked["textures"]["lorry"]["white"]

        self.hatchback_red_unlocked = self.unlocked["textures"]["hatchback"]["red"]
        self.hatchback_blue_unlocked = self.unlocked["textures"]["hatchback"]["blue"]
        self.hatchback_green_unlocked = self.unlocked["textures"]["hatchback"]["green"]
        self.hatchback_orange_unlocked = self.unlocked["textures"]["hatchback"]["orange"]
        self.hatchback_black_unlocked = self.unlocked["textures"]["hatchback"]["black"]
        self.hatchback_white_unlocked = self.unlocked["textures"]["hatchback"]["white"]

        self.rally_red_unlocked = self.unlocked["textures"]["rally_car"]["red"]
        self.rally_blue_unlocked = self.unlocked["textures"]["rally_car"]["blue"]
        self.rally_green_unlocked = self.unlocked["textures"]["rally_car"]["green"]
        self.rally_orange_unlocked = self.unlocked["textures"]["rally_car"]["orange"]
        self.rally_black_unlocked = self.unlocked["textures"]["rally_car"]["black"]
        self.rally_white_unlocked = self.unlocked["textures"]["rally_car"]["white"]

        self.viking_helmet_unlocked = self.unlocked["cosmetics"]["viking_helmet"]
        self.duck_unlocked = self.unlocked["cosmetics"]["duck"]
        self.banana_unlocked = self.unlocked["cosmetics"]["banana"]
        self.surfinbird_unlocked = self.unlocked["cosmetics"]["surfinbird"]

        self.drift_unlocked = self.unlocked["gamemodes"]["drift"]

        # Load settings
        self.controls = self.unlocked.get("settings", {}).get("controls", "wasd")
        self.flip_steering = self.unlocked.get("settings", {}).get("flip_steering", False)

        # Developer mode: unlock everything
        if self.for_developer:
            self.sand_track.unlocked = True
            self.grass_track.unlocked = True
            self.snow_track.unlocked = True
            self.forest_track.unlocked = True
            self.savannah_track.unlocked = True
            self.lake_track.unlocked = True

            self.beat_mandaw_sand_track = True
            self.beat_mandaw_grass_track = True
            self.beat_mandaw_snow_track = True
            self.beat_mandaw_forest_track = True
            self.beat_mandaw_savannah_track = True
            self.beat_mandaw_lake_track = True

            self.sports_unlocked = True
            self.muscle_unlocked = True
            self.limo_unlocked = True
            self.lorry_unlocked = True
            self.hatchback_unlocked = True
            self.rally_unlocked = True

            self.sports_red_unlocked = True
            self.sports_blue_unlocked = True
            self.sports_green_unlocked = True
            self.sports_orange_unlocked = True
            self.sports_black_unlocked = True
            self.sports_white_unlocked = True

            self.muscle_red_unlocked = True
            self.muscle_blue_unlocked = True
            self.muscle_green_unlocked = True
            self.muscle_orange_unlocked = True
            self.muscle_black_unlocked = True
            self.muscle_white_unlocked = True

            self.limo_red_unlocked = True
            self.limo_blue_unlocked = True
            self.limo_green_unlocked = True
            self.limo_orange_unlocked = True
            self.limo_black_unlocked = True
            self.limo_white_unlocked = True

            self.lorry_red_unlocked = True
            self.lorry_blue_unlocked = True
            self.lorry_green_unlocked = True
            self.lorry_orange_unlocked = True
            self.lorry_black_unlocked = True
            self.lorry_white_unlocked = True

            self.hatchback_red_unlocked = True
            self.hatchback_blue_unlocked = True
            self.hatchback_green_unlocked = True
            self.hatchback_orange_unlocked = True
            self.hatchback_black_unlocked = True
            self.hatchback_white_unlocked = True

            self.rally_red_unlocked = True
            self.rally_blue_unlocked = True
            self.rally_green_unlocked = True
            self.rally_orange_unlocked = True
            self.rally_black_unlocked = True
            self.rally_white_unlocked = True

            self.viking_helmet_unlocked = True
            self.duck_unlocked = True
            self.banana_unlocked = True
            self.surfinbird_unlocked = True

            self.drift_unlocked = True

    def save_unlocked(self):
        self.unlocked_dict = {
            "tracks": {
                "sand_track": self.sand_track.unlocked if self.sand_track else False,
                "grass_track": self.grass_track.unlocked if self.grass_track else False,
                "snow_track": self.snow_track.unlocked if self.snow_track else False,
                "forest_track": self.forest_track.unlocked if self.forest_track else False,
                "savannah_track": self.savannah_track.unlocked if self.savannah_track else False,
                "lake_track": self.lake_track.unlocked if self.lake_track else False
            },
            "beat_mandaw": {
                "sand_track": self.beat_mandaw_sand_track,
                "grass_track": self.beat_mandaw_grass_track,
                "snow_track": self.beat_mandaw_snow_track,
                "forest_track": self.beat_mandaw_forest_track,
                "savannah_track": self.beat_mandaw_savannah_track,
                "lake_track": self.beat_mandaw_lake_track
            },
            "cars": {
                "sports_car": getattr(self, "sports_unlocked", True),
                "muscle_car": getattr(self, "muscle_unlocked", True),
                "limo": getattr(self, "limo_unlocked", True),
                "lorry": getattr(self, "lorry_unlocked", True),
                "hatchback": getattr(self, "hatchback_unlocked", True),
                "rally_car": getattr(self, "rally_unlocked", True)
            },
            "textures": {
                "sports_car": {
                    "red": getattr(self, "sports_red_unlocked", True),
                    "blue": getattr(self, "sports_blue_unlocked", False),
                    "green": getattr(self, "sports_green_unlocked", False),
                    "orange": getattr(self, "sports_orange_unlocked", False),
                    "black": getattr(self, "sports_black_unlocked", False),
                    "white": getattr(self, "sports_white_unlocked", False)
                },
                "muscle_car": {
                    "red": getattr(self, "muscle_red_unlocked", True),
                    "blue": getattr(self, "muscle_blue_unlocked", False),
                    "green": getattr(self, "muscle_green_unlocked", False),
                    "orange": getattr(self, "muscle_orange_unlocked", False),
                    "black": getattr(self, "muscle_black_unlocked", False),
                    "white": getattr(self, "muscle_white_unlocked", False)
                },
                "limo": {
                    "red": getattr(self, "limo_red_unlocked", True),
                    "blue": getattr(self, "limo_blue_unlocked", False),
                    "green": getattr(self, "limo_green_unlocked", False),
                    "orange": getattr(self, "limo_orange_unlocked", False),
                    "black": getattr(self, "limo_black_unlocked", False),
                    "white": getattr(self, "limo_white_unlocked", False)
                },
                "lorry": {
                    "red": getattr(self, "lorry_red_unlocked", True),
                    "blue": getattr(self, "lorry_blue_unlocked", False),
                    "green": getattr(self, "lorry_green_unlocked", False),
                    "orange": getattr(self, "lorry_orange_unlocked", False),
                    "black": getattr(self, "lorry_black_unlocked", False),
                    "white": getattr(self, "lorry_white_unlocked", False)
                },
                "hatchback": {
                    "red": getattr(self, "hatchback_red_unlocked", True),
                    "blue": getattr(self, "hatchback_blue_unlocked", False),
                    "green": getattr(self, "hatchback_green_unlocked", False),
                    "orange": getattr(self, "hatchback_orange_unlocked", False),
                    "black": getattr(self, "hatchback_black_unlocked", False),
                    "white": getattr(self, "hatchback_white_unlocked", False)
                },
                "rally_car": {
                    "red": getattr(self, "rally_red_unlocked", True),
                    "blue": getattr(self, "rally_blue_unlocked", False),
                    "green": getattr(self, "rally_green_unlocked", False),
                    "orange": getattr(self, "rally_orange_unlocked", False),
                    "black": getattr(self, "rally_black_unlocked", False),
                    "white": getattr(self, "rally_white_unlocked", False)
                }
            },
            "cosmetics": {
                "viking_helmet": getattr(self, "viking_helmet_unlocked", False),
                "duck": getattr(self, "duck_unlocked", False),
                "banana": getattr(self, "banana_unlocked", False),
                "surfinbird": getattr(self, "surfinbird_unlocked", False)
            },
            "gamemodes": {
                "drift": getattr(self, "drift_unlocked", True)
            },
            "settings": {
                "controls": self.controls,
                "flip_steering": self.flip_steering
            }
        }

        with open(self.unlocked_json, "w") as hs:
            json.dump(self.unlocked_dict, hs, indent=4)

    def reset_timer(self):
        self.count = self.reset_count
        self.timer.enable()
        self.reset_count_timer.disable()

    def reset_drift(self):
        self.animate_text(self.drift_text, 1.7, 1.1)
        invoke(self.drift_text.animate_position, (-0.8, 0.43), 0.3, curve=curve.out_expo, delay=0.3)
        invoke(self.reset_drift_text, delay=0.4)
        self.drift_swush.play()
        self.get_hundred = False
        self.get_thousand = False
        self.get_fivethousand = False

    def reset_drift_text(self):
        self.drift_score += self.count
        self.drift_multiplier = 20
        self.count = 0
        self.drifting = False
        invoke(setattr, self.drift_text, "visible", False, delay=0.1)
        invoke(setattr, self.drift_text, "position", (0, 0.43), delay=0.3)

    def reset_drift_score(self):
        self.count = 0
        self.drift_score = 0
        self.drift_multiplier = 20
        self.drifting = False

        if self.sand_track and self.sand_track.enabled:
            self.drift_time = 25.0
        elif self.grass_track and self.grass_track.enabled:
            self.drift_time = 30.0
        elif self.snow_track and self.snow_track.enabled:
            self.drift_time = 50.0
        elif self.forest_track and self.forest_track.enabled:
            self.drift_time = 40.0
        elif self.savannah_track and self.savannah_track.enabled:
            self.drift_time = 25.0
        elif self.lake_track and self.lake_track.enabled:
            self.drift_time = 75.0

    def animate_text(self, text, top=1.2, bottom=0.6):
        if self.gamemode != "drift":
            if self.last_count > 1:
                text.animate_scale((top, top, top), curve=curve.out_expo)
                invoke(text.animate_scale, (bottom, bottom, bottom), delay=0.2)
        else:
            text.animate_scale((top, top, top), curve=curve.out_expo)
            invoke(text.animate_scale, (bottom, bottom, bottom), delay=0.2)

    def shake_camera(self):
        camera.x += random.randint(-1, 1) * self.shake_amount
        camera.y += random.randint(-1, 1) * self.shake_amount
        camera.z += random.randint(-1, 1) * self.shake_amount

    def update_model_path(self):
        self.model_path = str(self.model).replace("render/scene/car/", "")
        invoke(self.update_model_path, delay=3)

    def toggle_hand_controller(self):
        """
        Chuyển đổi trạng thái hand controller.
        Trả về True nếu BẬT (enabled), False nếu TẮT (disabled).
        """
        if self.hand_controller is None:
            from hand_controller import get_hand_controller
            self.hand_controller = get_hand_controller(self)
        if self.hand_controller.is_enabled():
            self.hand_controller.stop()
            return False
        else:
            self.hand_controller.start()
            return True


class CarRepresentation(Entity):
    def __init__(self, car, position=(0, 0, 0), rotation=(0, 65, 0)):
        super().__init__(
            parent=scene,
            model="sports-car.obj",
            texture="sports-red.png",
            position=position,
            rotation=rotation,
            scale=(1, 1, 1)
        )

        self.model_path = str(self.model).replace("render/scene/car_representation/", "")

        self.viking_helmet = Entity(model="viking_helmet.obj", texture="viking_helmet.png", parent=self)
        self.duck = Entity(model="duck.obj", parent=self)
        self.banana = Entity(model="banana.obj", parent=self)
        self.surfinbird = Entity(model="surfinbird.obj", texture="surfinbird.png", parent=self)
        self.surfboard = Entity(model="surfboard.obj", texture="surfboard.png", parent=self.surfinbird)
        self.viking_helmet.disable()
        self.duck.disable()
        self.banana.disable()
        self.surfinbird.disable()

        self.cosmetics = [self.viking_helmet, self.duck, self.banana, self.surfinbird]

        self.text_object = None
        self.highscore = 0.0

        invoke(self.update_representation, delay=5)

    def update_representation(self):
        for cosmetic in self.cosmetics:
            if cosmetic.enabled:
                if self.model_path == "lorry.obj":
                    cosmetic.y = 1.5
                elif self.model_path == "limo.obj":
                    cosmetic.y = 0.1
                elif self.model_path == "sports-car.obj" or self.model_path == "muscle-car.obj":
                    cosmetic.y = 0
        invoke(self.update_representation, delay=5)


class CarUsername(Text):
    def __init__(self, car):
        super().__init__(
            parent=car,
            text="Guest",
            y=3,
            scale=30,
            color=color.white,
            billboard=True
        )
        self.username_text = "Guest"

    def update(self):
        self.text = self.username_text
