"""
Module quản lý hệ thống ánh sáng mặt trời và bóng đổ trong game.

Sử dụng DirectionalLight của Panda3D để tạo ánh sáng mặt trời với bóng đổ động.
Ánh sáng tự động di chuyển theo xe để đảm bảo vùng chơi luôn được chiếu sáng đúng cách.
"""

from panda3d.core import DirectionalLight
from ursina import Entity

class SunLight(Entity):
    """Quản lý directional light (ánh sáng mặt trời) với bóng đổ động."""
    
    def __init__(self, direction, resolution, car):
        """
        Khởi tạo ánh sáng mặt trời.
        
        Args:
            direction: Vector hướng chiếu sáng
            resolution: Độ phân giải shadow map (càng cao càng sắc nét nhưng tốn performance)
            car: Đối tượng xe để ánh sáng theo dõi
        """
        super().__init__()

        self.car = car
        self.resolution = resolution

        self.dlight = DirectionalLight("sun")
        self.dlight.setShadowCaster(True, self.resolution, self.resolution)

        lens = self.dlight.getLens()
        lens.setNearFar(-80, 200)  # Phạm vi chiều sâu cho shadow casting
        lens.setFilmSize((100, 100))  # Kích thước vùng chiếu sáng

        self.dlnp = base.render.attachNewNode(self.dlight) # type: ignore
        self.dlnp.lookAt(direction)
        base.render.setLight(self.dlnp) # type: ignore

    def update(self):
        """
        Cập nhật vị trí ánh sáng mỗi frame.
        
        Di chuyển ánh sáng theo xe để bóng đổ luôn được tính toán đúng cho vùng quanh xe.
        """
        self.dlnp.setPos(self.car.world_position)

    def update_resolution(self):
        """
        Cập nhật độ phân giải bóng đổ.
        
        Được gọi khi người chơi thay đổi graphics settings.
        """
        self.dlight.setShadowCaster(True, self.resolution, self.resolution)