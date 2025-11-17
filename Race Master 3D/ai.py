"""
Module quản lý xe AI (đối thủ) trong game Race Master 3D.

AI xe tự động lái theo các điểm path được định sẵn trên mỗi đường đua,
tránh vật cản, và điều chỉnh tốc độ dựa trên địa hình. Hỗ trợ nhiều loại
xe khác nhau với thuộc tính vật lý riêng.
"""

from ursina import *
from particles import Particles
import random
from math import sqrt

# Hàm tiện ích để xác định dấu của số (âm hay dương)
sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)

class AICar(Entity):
    """
    Xe AI tự động điều khiển, đua với người chơi.
    
    AI sử dụng pathfinding đơn giản: theo dõi các điểm path và xoay
    về phía điểm tiếp theo. Có khả năng tránh vật cản và điều chỉnh
    tốc độ khi vào cua.
    """
    
    def __init__(self, car, ai_list, sand_track, grass_track, snow_track, forest_track, savannah_track, lake_track):
        """
        Khởi tạo xe AI.
        
        Args:
            car: Xe người chơi (để tham chiếu)
            ai_list: Danh sách tất cả AI cars
            *_track: Các đường đua trong game
        """
        super().__init__(
            model = "sports-car.obj",
            texture = "sports-red.png",
            collider = "box",
            position = (0, 0, 0),
            rotation = (0, 0, 0),
        )

        # Entity để làm mượt chuyển động xoay
        self.rotation_parent = Entity()

        # Tham chiếu đến xe người chơi và loại xe hiện tại
        self.car = car
        self.car_type = "sports"

        # Chọn ngẫu nhiên loại xe và màu sắc cho AI
        self.set_random_car()
        self.set_random_texture()

        # ==================== THÔNG SỐ VẬT LÝ ====================
        # Các giá trị cơ bản để điều khiển xe AI
        self.speed = 0                    # Tốc độ hiện tại
        self.velocity_y = 0              # Vận tốc theo trục Y (nhảy/fall)
        self.rotation_speed = 0          # Tốc độ xoay
        self.max_rotation_speed = 2.6    # Tốc độ xoay tối đa
        self.topspeed = 30               # Tốc độ tối đa
        self.acceleration = 0.35         # Gia tốc
        self.friction = 0.6              # Ma sát
        self.drift_speed = 35            # Tốc độ drift
        self.pivot_rotation_distance = 1 # Khoảng cách xoay pivot

        # ==================== HỆ THỐNG DRIFT ====================
        # Pivot để tạo hiệu ứng drift (trượt)
        self.pivot = Entity()
        self.pivot.position = self.position
        self.pivot.rotation = self.rotation

        # ==================== HIỆU ỨNG HẠT ====================
        # Hệ thống tạo hiệu ứng khói bụi khi xe chạy
        self.particle_time = 0
        self.particle_amount = 0.125      # Càng nhỏ càng nhiều hạt
        self.particle_pivot = Entity(parent = self)
        self.particle_pivot.position = (0, -1, -2)

        # ==================== THAM CHIẾU ĐƯỜNG ĐUA ====================
        # Lưu trữ tham chiếu đến tất cả các đường đua
        self.sand_track = sand_track
        self.grass_track = grass_track
        self.snow_track = snow_track
        self.forest_track = forest_track
        self.savannah_track = savannah_track
        self.lake_track = lake_track

        # Đường đua hiện tại mà AI đang chạy
        self.current_track = self.sand_track

        # Danh sách tất cả đường đua
        self.tracks = [self.sand_track, self.grass_track, self.snow_track, self.forest_track, self.savannah_track, self.lake_track]

        # ==================== QUẢN LÝ AI ====================
        self.ai_list = ai_list           # Danh sách tất cả xe AI
        self.set_enabled = True          # Có bật AI không
        self.hitting_wall = False        # Có đang đụng tường không

        # ==================== HỆ THỐNG CẬP NHẬT ====================
        self.t = 0                       # Thời gian tích lũy
        self.update_step = 0.05          # Khoảng thời gian cập nhật raycast

        # ==================== RAYCAST CHO VÀO CẠN ====================
        # Tia laser để phát hiện mặt đất và vật cản
        self.y_ray = raycast(origin = self.world_position, direction = (0, -1, 0), traverse_target = self.current_track, ignore = [self, self.sand_track.wall1, self.sand_track.wall2, self.sand_track.wall3, self.sand_track.wall4, self.grass_track.wall1, self.grass_track.wall2, self.grass_track.wall3, self.grass_track.wall4, self.snow_track.wall1, self.snow_track.wall2, self.snow_track.wall3, self.snow_track.wall4, self.snow_track.wall5, self.snow_track.wall6, self.snow_track.wall7, self.snow_track.wall8, self.snow_track.wall9, self.snow_track.wall10, self.snow_track.wall11, self.snow_track.wall12, self.forest_track.wall1, self.forest_track.wall2, self.forest_track.wall3, self.forest_track.wall4, self.forest_track.wall1, self.forest_track.wall2, self.forest_track.wall3, self.forest_track.wall4, ]) # type: ignore

        # ==================== PHÒNG TRÁNH BỊ MẮC KẸT ====================
        # Lưu vị trí cũ để kiểm tra xem AI có bị mắc kẹt không
        self.old_pos = round(self.position)

        # ==================== CÁC ĐIỂM PATH CHO TỪNG ĐƯỜNG ĐUA ====================
        # Đây là các điểm mốc mà AI sẽ theo dõi để lái xe
        # Mỗi đường đua có một tập các điểm path riêng

        # Sand Track Points - Điểm path cho đường đua sa mạc
        self.sap1 = PathObject((-41, -50, -7), 90)
        self.sap2 = PathObject((-20, -50, -30), 180)
        self.sap3 = PathObject((-48, -47, -55), 270)
        self.sap4 = PathObject((-100, -50, -61), 270)
        self.sap5 = PathObject((-128, -50, -80), 150)
        self.sap6 = PathObject((-100, -50, -115), 70)
        self.sap7 = PathObject((-80, -46, -86), -30)
        self.sap8 = PathObject((-75, -50, -34), 0)

        # Grass Track Points - Điểm path cho đường đua đồng cỏ
        self.gp1 = PathObject((-47, -41, 15), 90)
        self.gp2 = PathObject((12, -42, 14), 90)
        self.gp3 = PathObject((48, -42, 34), 0)
        self.gp4 = PathObject((25, -42, 68), -90)
        self.gp5 = PathObject((0, -42, 50), -210)
        self.gp6 = PathObject((2, -42, -25), -180)
        self.gp7 = PathObject((-10, -42, -60), -90)
        self.gp8 = PathObject((-70, -39, -67), -70)
        self.gp9 = PathObject((-105, -42, -26), 00)
        self.gp10 = PathObject((-106, -42, -2), 50)
        self.gp11 = PathObject((-60, -42, 15), 120)

        # Snow Track Points - Điểm path cho đường đua tuyết
        self.snp1 = PathObject((32, -44, 94), 90)
        self.snp2 = PathObject((48, -44, 72), 180)
        self.snp3 = PathObject((39, -44, 42), 280)
        self.snp4 = PathObject((-37, -44, 42), 270)
        self.snp5 = PathObject((-73, -43, 25), 180)
        self.snp6 = PathObject((-40, -44, -8), 65)
        self.snp7 = PathObject((20, -44, -8), 90)
        self.snp8 = PathObject((50, -42, -25), 250)
        self.snp9 = PathObject((30, -43, -55), 290)
        self.snp10 = PathObject((5, -44, -51), 290)
        self.snp11 = PathObject((-15, -44, -39), 380)
        self.snp12 = PathObject((-22, -44, 70), 363)
        self.snp13 = PathObject((-21, -44, 106), 340)
        self.snp14 = PathObject((-47, -41, 126), 240)
        self.snp15 = PathObject((-70, -44, 100), 140)
        self.snp16 = PathObject((-30, -44, 90), 90)
        self.snp17 = PathObject((-14, -44, 94), 90)

        # Forrest Track Points - Điểm path cho đường đua rừng
        self.fp1 = PathObject((57, -51, 76), 90)
        self.fp2 = PathObject((82, -51, 63), 180)
        self.fp3 = PathObject((57, -51, 36), 275)
        self.fp4 = PathObject((-29, -51, 36), 270)
        self.fp5 = PathObject((-62, -51, 16), 170)
        self.fp6 = PathObject((-42, -51, -11), 80)
        self.fp7 = PathObject((4, -51, -11), 90)
        self.fp8 = PathObject((41, -51, -40), 180)
        self.fp9 = PathObject((5, -51, -66), 270)
        self.fp10 = PathObject((-17, -51, -53), 360)
        self.fp11 = PathObject((-18, -51, -6), 0)
        self.fp12 = PathObject((-18, -46, 40), 0)
        self.fp13 = PathObject((-3, -51, 75), 120)

        # Savannah Track Points - Điểm path cho đường đua thảo nguyên
        self.svp1 = PathObject((28, -51, 40), 90)
        self.svp2 = PathObject((50, -51, 40), 160)
        self.svp3 = PathObject((61, -51, 18), 260)
        self.svp4 = PathObject((-30, -51, -77), 230)
        self.svp5 = PathObject((-64, -51, -50), 390)
        self.svp6 = PathObject((-64, -45, 0), 360)
        self.svp7 = PathObject((-50, -51, 40), 500)
        self.svp8 = PathObject((-24, -51, 41), 450)

        # Lake Track Points - Điểm path cho đường đua hồ
        self.lp1 = PathObject((-70, -50, 157), 90)
        self.lp2 = PathObject((-51, -50, 165), 45)
        self.lp3 = PathObject((-25, -50, 160), 135)
        self.lp4 = PathObject((-4, -50, 156), 45)
        self.lp5 = PathObject((30, -50, 165), 121)
        self.lp6 = PathObject((84, -38, 163), 90)
        self.lp7 = PathObject((117, -37, 157), 210)
        self.lp8 = PathObject((121, -50, 114), 180)
        self.lp9 = PathObject((150, -50, 88), 60)
        self.lp10 = PathObject((170, -50, 80), 192)
        self.lp11 = PathObject((150, -50, 30), 280)
        self.lp12 = PathObject((131, -50, 20), 150)
        self.lp13 = PathObject((127, -50, -157), 177)
        self.lp14 = PathObject((131, -46, -190), 100)
        self.lp15 = PathObject((170, -39, -170), 0)
        self.lp16 = PathObject((170, -35, -153), -70)
        self.lp17 = PathObject((100, -46, -147), -90)
        self.lp18 = PathObject((-109, -50, -145), -90)
        self.lp19 = PathObject((-146, -50, -122), 60)
        self.lp20 = PathObject((-144, -44, 115), 0)
        self.lp21 = PathObject((-127, -50, 155), 120)

        # ==================== DANH SÁCH ĐIỂM PATH ====================
        # Gom các điểm path thành danh sách để dễ quản lý
        self.sand_path = [self.sap1, self.sap2, self.sap3, self.sap4, self.sap5, self.sap6, self.sap7, self.sap8]
        self.grass_path = [self.gp1, self.gp2, self.gp3, self.gp4, self.gp5, self.gp6, self.gp7, self.gp8, self.gp9, self.gp10, self.gp11]
        self.snow_path = [self.snp1, self.snp2, self.snp3, self.snp4, self.snp5, self.snp6, self.snp7, self.snp8, self.snp9, self.snp10, self.snp11, self.snp12, self.snp13, self.snp14, self.snp15, self.snp16, self.snp17]
        self.forest_path = [self.fp1, self.fp2, self.fp3, self.fp4, self.fp5, self.fp6, self.fp7, self.fp8, self.fp9, self.fp10, self.fp11, self.fp12, self.fp13]
        self.savannah_path = [self.svp1, self.svp2, self.svp3, self.svp4, self.svp5, self.svp6, self.svp7, self.svp8]
        self.lake_path = [self.lp1, self.lp2, self.lp3, self.lp4, self.lp5, self.lp6, self.lp7, self.lp8, self.lp9, self.lp10, self.lp11, self.lp12, self.lp13, self.lp14, self.lp15, self.lp16, self.lp17, self.lp18, self.lp19, self.lp20, self.lp21]
        
        # ==================== QUẢN LÝ ĐIỂM PATH HIỆN TẠI ====================
        # Điểm path tiếp theo mà AI sẽ hướng tới
        self.next_path = self.gp1

        # Độ khó của AI (tốc độ)
        self.difficulty = 50

        # Kiểm tra vị trí AI mỗi 5 giây để tránh bị mắc kẹt
        invoke(self.same_pos, delay = 5)

        # Tắt AI ban đầu, sẽ được bật khi cần
        self.disable()

    # ==================== CÁC HÀM THIẾT LẬP XE ====================
    
    def sports_car(self):
        self.model = "sports-car.obj"
        self.texture = "sports-red.png"
        self.car_type = "sports"
    
    def muscle_car(self):
        self.model = "muscle-car.obj"
        self.texture = "muscle-orange.png"
        self.car_type = "muscle"

    def limo(self):
        self.model = "limousine.obj"
        self.texture = "limo-black.png"
        self.car_type = "limo"

    def lorry(self):
        self.model = "lorry.obj"
        self.texture = "lorry-white.png"
        self.car_type = "lorry"

    def hatchback(self):
        self.model = "hatchback.obj"
        self.texture = "hatchback-green.png"
        self.car_type = "hatchback"

    def rally_car(self):
        self.model = "rally-car.obj"
        self.texture = "rally-red.png"
        self.car_type = "rally"

    # ==================== HÀM CHỌN XE VÀ MÀU NGẪU NHIÊN ====================
    
    def set_random_car(self):
        """
        Chọn ngẫu nhiên loại xe cho AI
        Có 6 loại xe: sports, muscle, limo, lorry, hatchback, rally
        """
        i = random.randint(0, 5)
        if i == 0:
            self.sports_car()
        elif i == 1:
            self.muscle_car()
        elif i == 2:
            self.limo()
        elif i == 3:
            self.lorry()
        elif i == 4:
            self.hatchback()
        elif i == 5:
            self.rally_car()

    def set_random_texture(self):
        """
        Chọn ngẫu nhiên màu sắc cho xe AI
        Có 6 màu: red, blue, orange, green, white, black
        """
        i = random.randint(0, 5)
        if i == 0:
            self.texture = f"{self.car_type}-red.png"
        elif i == 1:
            self.texture = f"{self.car_type}-blue.png"
        elif i == 2:
            self.texture = f"{self.car_type}-orange.png"
        elif i == 3:
            self.texture = f"{self.car_type}-green.png"
        elif i == 4:
            self.texture = f"{self.car_type}-white.png"
        elif i == 5:
            self.texture = f"{self.car_type}-black.png"

    # ==================== HÀM PHÒNG TRÁNH BỊ MẮC KẸT ====================
    
    def same_pos(self):
        """
        Kiểm tra xem AI có bị mắc kẹt ở cùng một vị trí không
        Nếu AI không di chuyển được 2 đơn vị trong 1 giây, sẽ di chuyển ngẫu nhiên
        để tránh bị kẹt trong vật cản
        """
        if self.enabled:
            # Tính khoảng cách giữa vị trí hiện tại và vị trí cũ
            distance = sqrt((self.position[0] - self.old_pos[0]) ** 2 + (self.position[1] - self.old_pos[1]) ** 2 + (self.position[2] - self.old_pos[2]) ** 2)
            if distance <= 2:
                # Di chuyển ngẫu nhiên để thoát khỏi vị trí kẹt
                self.x += random.randint(-10, 10) * time.dt
                self.y += 40 * time.dt
                self.z += random.randint(-10, 10) * time.dt
            # Cập nhật vị trí cũ
            self.old_pos = round(self.position)
        # Gọi lại hàm này sau 1 giây
        invoke(self.same_pos, delay = 1)

    # ==================== HÀM CẬP NHẬT CHÍNH ====================
    
    def update(self):
        """
        Hàm cập nhật chính của xe AI - được gọi mỗi frame (60 lần/giây)
        Điều khiển toàn bộ logic của xe AI: drift, collision, pathfinding, movement
        Đây là "bộ não" chính của xe AI
        """
        # ==================== LOGIC DRIFT (TRƯỢT) ====================
        
        # Thiết lập vị trí pivot (điểm trung tâm) cho logic drift
        self.pivot.position = self.position
        
        # Tính khoảng cách góc quay giữa xe và pivot
        self.pivot_rotation_distance = (self.rotation_y - self.pivot.rotation_y)

        # Logic drift: làm cho xe trượt khi quay
        if self.pivot.rotation_y != self.rotation_y:
            if self.pivot.rotation_y > self.rotation_y:
                # Quay trái - giảm tốc độ quay của pivot
                self.pivot.rotation_y -= (self.drift_speed * ((self.pivot.rotation_y - self.rotation_y) / 40)) * time.dt
                # Tăng tốc độ khi drift
                self.speed += self.pivot_rotation_distance / 4.5 * time.dt
            if self.pivot.rotation_y < self.rotation_y:
                # Quay phải - tăng tốc độ quay của pivot  
                self.pivot.rotation_y += (self.drift_speed * ((self.rotation_y - self.pivot.rotation_y) / 40)) * time.dt
                # Giảm tốc độ khi drift
                self.speed -= self.pivot_rotation_distance / 4.5 * time.dt

        # ==================== LOGIC KHÓ KHĂN THEO ĐƯỜNG ĐUA ====================
        
        # Đặt độ khó dựa trên loại đường đua
        if self.sand_track.enabled or self.grass_track.enabled or self.savannah_track.enabled or self.lake_track.enabled:
            # Đường khó: cát, cỏ, savannah, hồ - độ khó cao
            self.difficulty = 60
        elif self.snow_track.enabled or self.forest_track.enabled:
            # Đường trung bình: tuyết, rừng - độ khó thấp hơn
            self.difficulty = 40

        # ==================== LOGIC XỬ LÝ GÓC QUAY ====================
        
        # Đặt vị trí của rotation_parent (đối tượng quay) bằng vị trí xe
        self.rotation_parent.position = self.position

        # Làm mượt góc quay X và Z bằng hàm lerp (linear interpolation)
        self.rotation_x = lerp(self.rotation_x, self.rotation_parent.rotation_x, 20 * time.dt)
        self.rotation_z = lerp(self.rotation_z, self.rotation_parent.rotation_z, 20 * time.dt)
    
        # ==================== LOGIC RAYCAST (KIỂM TRA ĐỊA HÌNH) ====================
        
        # Cập nhật timer để kiểm tra raycast không liên tục (tối ưu hiệu năng)
        self.t += time.dt
        if self.t >= self.update_step:
            self.t = 0
            # Raycast xuống dưới để kiểm tra mặt đất và khoảng cách
            self.y_ray = raycast(origin=self.world_position, direction=(0, -1, 0), traverse_target=self.current_track, ignore=[self] + self.get_wall_list()) # type: ignore


        # ==================== LOGIC TĂNG TỐC TRÊN ĐỊA HÌNH ====================
        
        # Nếu xe ở gần mặt đất (khoảng cách <= 4), tăng tốc
        if self.y_ray.distance <= 4:
            # Random quyết định có tăng tốc hay không
            r = random.randint(0, 1)
            if r == 0:
                # Tăng tốc dựa trên độ khó của đường đua
                self.speed += self.acceleration * self.difficulty * time.dt

                # Tạo hiệu ứng hạt (bụi) khi tăng tốc
                self.particle_time += time.dt
                if self.particle_time >= self.particle_amount:
                    self.particle_time = 0
                    # Tạo particles tại vị trí bánh xe
                    self.particles = Particles(self, position=self.particle_pivot.world_position - (0, 1, 0))
                    self.particles.destroy(1)  # Tự hủy sau 1 giây

        # ==================== LOGIC AI CHÍNH - THEO ĐƯỜNG ĐUA ====================
        
        # Nếu góc quay Y của AI khác với điểm path tiếp theo, điều chỉnh
        if self.next_path.rotation_y > self.rotation_y:
            self.rotation_y += 80 * time.dt  # Quay phải
        elif self.next_path.rotation_y < self.rotation_y:
            self.rotation_y -= 80 * time.dt  # Quay trái

        # ==================== LOGIC CHUYỂN ĐỔI ĐIỂM PATH ====================
        
        """
        Khi khoảng cách giữa xe và điểm path tiếp theo < ngưỡng nhất định,
        chuyển sang điểm path tiếp theo trong danh sách (đường tròn)
        """
        if self.sand_track.enabled:
            # Đường đua cát: ngưỡng 12 đơn vị
            for p in self.sand_path:
                if distance(p, self) < 12 and self.next_path == p:
                    # Chuyển sang điểm tiếp theo (vòng tròn)
                    self.next_path = self.sand_path[self.sand_path.index(p) - len(self.sand_path) + 1]
                    
        elif self.grass_track.enabled:
            # Đường đua cỏ: ngưỡng 14 đơn vị (rộng hơn)
            for p in self.grass_path:
                if distance(p, self) < 14 and self.next_path == p:
                    self.next_path = self.grass_path[self.grass_path.index(p) - len(self.grass_path) + 1]
                    
        elif self.snow_track.enabled:
            # Đường đua tuyết: ngưỡng 12 đơn vị
            for p in self.snow_path:
                if distance(p, self) < 12 and self.next_path == p:
                    self.next_path = self.snow_path[self.snow_path.index(p) - len(self.snow_path) + 1]
                    
        elif self.forest_track.enabled:
            # Đường đua rừng: có logic đặc biệt tại điểm fp10
            if distance(self.fp10, self) < 12:
                # Tại điểm fp10: đặt góc quay về 0 (đi thẳng)
                self.rotation_y = 0
                self.pivot.rotation_y = self.rotation_y
            for p in self.forest_path:
                if distance(p, self) < 12 and self.next_path == p:
                    self.next_path = self.forest_path[self.forest_path.index(p) - len(self.forest_path) + 1]
                    
        elif self.savannah_track.enabled:
            # Đường đua savannah: có 2 điểm đặc biệt
            if distance(self.svp4, self) < 10:
                # Tại svp4: giảm tốc độ
                self.speed -= 10 * time.dt
            if distance(self.svp8, self) < 12:
                # Tại svp8: quay 90 độ (rẽ phải)
                self.rotation_y = 90
                self.pivot.rotation_y = self.rotation_y
            for p in self.savannah_path:
                if distance(p, self) < 15 and self.next_path == p:
                    self.next_path = self.savannah_path[self.savannah_path.index(p) - len(self.savannah_path) + 1]
                    
        elif self.lake_track.enabled:
            # Đường đua hồ: kiểm tra va chạm với biên hồ
            if self.simple_intersects(self.lake_track.lake_bounds):
                self.reset()  # Reset nếu chạm biên hồ
            for p in self.lake_path:
                if distance(p, self) < 15 and self.next_path == p:
                    self.next_path = self.lake_path[self.lake_path.index(p) - len(self.lake_path) + 1]

        # ==================== LOGIC GIỚI HẠN TỐC ĐỘ ====================
        
        # Giới hạn tốc độ tối đa
        if self.speed >= self.topspeed:
            self.speed = self.topspeed
        # Giới hạn tốc độ tối thiểu (để xe không dừng hẳn)
        if self.speed <= 0.1:
            self.speed = 0.1
            self.pivot.rotation = self.rotation

        # Giới hạn tốc độ drift
        if self.drift_speed <= 20:
            self.drift_speed = 20
        if self.drift_speed >= 40:
            self.drift_speed = 40
        
        # ==================== LOGIC RESET KHI RƠI XUỐNG ====================
        
        # Nếu xe rơi xuống dưới -100 (rơi khỏi đường đua), reset
        if self.y <= -100:
            self.reset()

        # Nếu xe bay lên trên 100 (nhảy quá cao), reset
        if self.y >= 100:
            self.reset()

        # ==================== LOGIC TRỌNG LỰC ====================
        
        # Tính chuyển động theo trục Y (trọng lực)
        movementY = self.velocity_y * time.dt

        # Kiểm tra va chạm với mặt đất
        if self.y_ray.distance <= self.scale_y * 1.7 + abs(movementY):
            # Đặt vận tốc Y về 0 khi chạm đất
            self.velocity_y = 0
            
            # Kiểm tra có đang chạm tường hoặc dốc đứng không
            if self.y_ray.world_normal.y > 0.7 and self.y_ray.world_point.y - self.world_y < 0.5:
                # Đặt vị trí Y bằng mặt đất + offset
                self.y = self.y_ray.world_point.y + 1.4
                self.hitting_wall = False
            else:
                self.hitting_wall = True

            # Xử lý góc quay dựa trên việc có chạm tường không
            if not self.hitting_wall:
                # Không chạm tường: quay theo hướng pháp tuyến của mặt đất
                self.rotation_parent.look_at(self.position + self.y_ray.world_normal, axis="up")
                self.rotation_parent.rotation = (0, self.rotation_y + 180, 0)
            else:
                # Chạm tường: giữ nguyên góc quay
                self.rotation_parent.rotation = self.rotation
        else:
            # Không chạm đất: áp dụng trọng lực
            self.y += movementY * 50 * time.dt
            self.velocity_y -= 50 * time.dt
            self.rotation_parent.rotation = self.rotation

        # ==================== LOGIC DI CHUYỂN CUỐI CÙNG ====================
        
        # Tính chuyển động theo trục X và Z dựa trên hướng pivot
        movementX = self.pivot.forward[0] * self.speed * time.dt
        movementZ = self.pivot.forward[2] * self.speed * time.dt

        # Áp dụng chuyển động
        if movementX != 0:
            self.x += movementX
        if movementZ != 0:
            self.z += movementZ

    # ==================== HÀM RESET VỊ TRÍ ====================
    
    def reset(self):
        """
        Reset vị trí xe AI về điểm xuất phát khi bị kẹt hoặc rơi khỏi đường đua
        Mỗi đường đua có vị trí reset khác nhau
        """
        if self.grass_track.enabled:
            # Reset trên đường cỏ
            self.position = (-80 + random.randint(-5, 5), -30 + random.randint(-3, 5), 15 + random.randint(-5, 5))
            self.rotation = (0, 90, 0)  # Hướng Đông
            self.next_path = self.gp1  # Điểm path đầu tiên
        elif self.sand_track.enabled:
            # Reset trên đường cát
            self.position = (-63 + random.randint(-5, 5), -40 + random.randint(-3, 5), -7 + random.randint(-5, 5))
            self.rotation = (0, 65, 0)  # Hướng Đông-Nam
            self.next_path = self.sap1
        elif self.snow_track.enabled:
            # Reset trên đường tuyết
            self.position = (-5 + random.randint(-5, 5), -35 + random.randint(-3, 5), 90 + random.randint(-5, 5))
            self.rotation = (0, 90, 0)
            self.next_path = self.snp1
        elif self.forest_track.enabled:
            # Reset trên đường rừng
            self.position = (12 + random.randint(-5, 5), -40 + random.randint(-3, 5), 73 + random.randint(-5, 5))
            self.rotation = (0, 90, 0)
            self.next_path = self.fp1
        elif self.lake_track.enabled:
            # Reset trên đường hồ
            self.position = (-121, -40, 158)
            self.rotation = (0, 90, 0)
            self.next_path = self.lp1
        else:
            # Reset mặc định
            self.position = (0, 0, 0)
            self.rotation = (0, 0, 0)
        
        # Reset tốc độ và vận tốc
        self.speed = 0
        self.velocity_y = 0

    # ==================== HÀM KIỂM TRA VA CHẠM ĐƠN GIẢN ====================
    
    def simple_intersects(self, entity):
        """
        Kiểm tra va chạm đơn giản giữa AI và một entity khác
        Sử dụng AABB (Axis-Aligned Bounding Box) - không xét góc quay
        Trả về True nếu 2 hình hộp bao quanh nhau chồng lên nhau
        
        Cách hoạt động:
        - Tạo hình hộp bao quanh cho cả 2 entity (AABB)
        - Kiểm tra xem 2 hình hộp có giao nhau không
        - Nếu có giao nhau = có va chạm
        """
        # Tính giới hạn của entity A (xe AI)
        minXA = self.x - self.scale_x
        maxXA = self.x + self.scale_x
        minYA = self.y - self.scale_y + (self.scale_y / 2)
        maxYA = self.y + self.scale_y - (self.scale_y / 2)
        minZA = self.z - self.scale_z
        maxZA = self.z + self.scale_z

        # Tính giới hạn của entity B (đối tượng cần kiểm tra)
        minXB = entity.x - entity.scale_x + (entity.scale_x / 2)
        maxXB = entity.x + entity.scale_x - (entity.scale_x / 2)
        minYB = entity.y - entity.scale_y + (entity.scale_y / 2)
        maxYB = entity.y + entity.scale_y - (entity.scale_y / 2)
        minZB = entity.z - entity.scale_z + (entity.scale_z / 2)
        maxZB = entity.z + entity.scale_z - (entity.scale_z / 2)
        
        # Kiểm tra giao nhau trên cả 3 trục X, Y, Z
        return (
            (minXA <= maxXB and maxXA >= minXB) and  # X axis overlap
            (minYA <= maxYB and maxYA >= minYB) and  # Y axis overlap
            (minZA <= maxZB and maxZA >= minZB)      # Z axis overlap
        )

    # ==================== HÀM KIỂM TRA ĐƯỜNG ĐUA HIỆN TẠI ====================
    
    def check_track(self):
        """
        Kiểm tra đường đua nào đang được kích hoạt
        Đặt current_track để các logic khác sử dụng
        """
        for track in self.tracks:
            if track.enabled:
                self.current_track = track

    def get_wall_list(self):
        """
        Trả về danh sách các bức tường của đường đua hiện tại
        Dùng để loại bỏ khỏi raycast collision detection
        """
        walls = []
        # Kiểm tra các wall từ 1 đến 12 (tối đa của snow track)
        for i in range(1, 13):
            wall_name = f'wall{i}'
            if hasattr(self.current_track, wall_name):
                walls.append(getattr(self.current_track, wall_name))
        return walls

# ==================== LỚP ĐIỂM PATH ====================

class PathObject(Entity):
    """
    Lớp đại diện cho các điểm path (điểm dẫn đường) trong game
    Đây là các điểm mà xe AI sẽ di chuyển đến theo thứ tự
    
    Mỗi điểm path là một cube vô hình (visible=False) với:
    - Vị trí trong không gian 3D
    - Góc quay Y để chỉ hướng di chuyển tiếp theo
    - Scale lớn (1, 20, 20) để dễ phát hiện
    - Alpha = 50 để có thể thấy khi debug
    """
    def __init__(self, position=(0, 0, 0), rotation_y=0):
        super().__init__(
            model="cube",           # Hình dạng cube
            position=position,      # Vị trí trong không gian
            rotation_y=rotation_y,  # Góc quay Y (hướng)
            texture="white_cube",   # Texture màu trắng
            scale=(1, 20, 20),      # Kích thước (rộng, cao, sâu)
            visible=False,          # Ẩn đi (không hiển thị trong game)
            alpha=50,               # Độ trong suốt (50/255)
        )