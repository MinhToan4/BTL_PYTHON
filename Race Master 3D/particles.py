"""
Module quản lý hiệu ứng hạt (particles) và trail effects trong game.

Bao gồm:
- Particles: Bụi/khói bay lên khi xe chạy
- TrailRenderer: Đường kéo sau xe khi drift
"""

from ursina import *
from ursina import curve

class Particles(Entity):
    """Hiệu ứng hạt bụi/khói khi xe chạy trên bề mặt đường đua."""
    
    def __init__(self, car, position):
        """
        Khởi tạo particle.
        
        Args:
            car: Đối tượng xe (để xác định loại track và texture phù hợp)
            position: Vị trí spawn particle
        """
        super().__init__(
            model = "particles.obj",
            scale = 0.1,
            position = position, 
            rotation_y = random.random() * 360
        )
        
        self.car = car
        self.direction = Vec3(random.random(), random.random(), random.random())

        # Chọn texture phù hợp với loại track hiện tại
        if hasattr(self.car, "sand_track"):
            if car.sand_track.enabled:
                self.texture = "particle_sand_track.png"
            elif car.grass_track.enabled:
                self.texture = "particle_grass_track.png"
            elif car.snow_track.enabled:
                self.texture = "particle_snow_track.png"
            elif car.forest_track.enabled:
                self.texture = "particle_forest_track.png"
            elif car.savannah_track.enabled:
                self.texture = "particle_savannah_track.png"
            elif car.lake_track.enabled:
                self.texture = "particle_lake_track.png"
            else:
                self.texture = "particle_sand_track.png"

    def update(self):
        """Cập nhật vị trí particle mỗi frame (bay lên theo direction)."""
        self.position += self.direction * 5 * time.dt
        if hasattr(self.car, "graphics"):
            if self.car.graphics != "fancy":
                self.scale_x += 0.1 * time.dt
                self.scale_y += 0.1 * time.dt

    def destroy(self, delay = 1):
        """
        Hủy particle với hiệu ứng fade out.
        
        Args:
            delay: Thời gian trước khi hủy hoàn toàn
        """
        self.fade_out(duration = 0.2, delay = 0.7, curve = curve.linear)
        destroy(self, delay)
        del self

class TrailRenderer(Entity):
    """Hiệu ứng trail (đường kéo) khi xe drift."""
    
    def __init__(self, thickness = 10, length = 6, **kwargs):
        """
        Khởi tạo trail renderer.
        
        Args:
            thickness: Độ dày đường trail
            length: Số điểm tạo thành trail
        """
        super().__init__(**kwargs)
        self.thickness = thickness
        self.length = length

        self._t = 0
        self.update_step = 0.025  # Tần suất cập nhật trail
        self.trailing = False

    def update(self):
        """Cập nhật trail mỗi frame nếu đang trailing."""
        if self.trailing:
            self._t += time.dt
            if self._t >= self.update_step:
                self._t = 0
                # Xóa điểm cũ nhất và thêm điểm mới nhất
                self.renderer.model.vertices.pop(0)
                self.renderer.model.vertices.append(self.world_position)
                self.renderer.model.generate()

    def start_trail(self):
        """Bắt đầu tạo trail."""
        self.trailing = True
        self.renderer = Entity(model = Mesh(
            vertices = [self.world_position for i in range(self.length)],
            mode = "line",
            thickness = self.thickness,
            static = False,
        ), color = color.rgba(10, 10, 10, 90))  # Màu đen trong suốt
    
    def end_trail(self, now = False):
        """
        Kết thúc trail, có thể fade out hoặc hủy ngay lập tức.
        """
        if not now:
            # Fade out trong 1 giây, delay 8 giây, sau đó hủy
            self.renderer.fade_out(duration = 1, delay = 8, curve = curve.linear)
            destroy(self.renderer, 10)
        else:
            destroy(self.renderer)
        self.trailing = False