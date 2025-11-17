from panda3d.core import DirectionalLight
from ursina import Entity

class SunLight(Entity):
    """
    Lớp SunLight quản lý ánh sáng định hướng (directional light) trong game
    - Tạo hiệu ứng ánh sáng mặt trời
    - Tạo bóng đổ cho các đối tượng trong game
    - Tự động di chuyển theo vị trí của xe để ánh sáng luôn soi đúng vùng chơi
    """
    def __init__(self, direction, resolution, car):
        """
        Khởi tạo nguồn sáng mặt trời
        
        Tham số:
        - direction: Hướng của ánh sáng (vector chỉ hướng sáng chiếu xuống)
        - resolution: Độ phân giải của bóng đổ (càng cao thì bóng càng sắc nét nhưng tốn hiệu năng)
        - car: Đối tượng xe, dùng để ánh sáng theo dõi vị trí của xe
        """
        super().__init__()

        # Lưu tham chiếu đến xe và độ phân giải
        self.car = car
        self.resolution = resolution

        # Tạo nguồn sáng định hướng (giống như ánh sáng mặt trời)
        self.dlight = DirectionalLight("sun")
        # Bật tính năng tạo bóng đổ với độ phân giải đã cho
        # resolution x resolution là kích thước shadow map (bản đồ bóng)
        self.dlight.setShadowCaster(True, self.resolution, self.resolution)

        # Lấy lens (ống kính) của nguồn sáng để thiết lập các thông số
        lens = self.dlight.getLens()
        # Thiết lập khoảng cách gần-xa mà ánh sáng có thể chiếu
        # -80 đến 200: vùng từ -80 đến 200 đơn vị sẽ được chiếu sáng và tạo bóng
        lens.setNearFar(-80, 200)
        # Thiết lập kích thước vùng chiếu sáng (100x100 đơn vị)
        # Vùng này quyết định diện tích mà ánh sáng có thể chiếu và tạo bóng
        lens.setFilmSize((100, 100))

        # Gắn nguồn sáng vào scene (render node) của Panda3D
        self.dlnp = base.render.attachNewNode(self.dlight) # type: ignore
        # Xoay nguồn sáng theo hướng đã chỉ định
        self.dlnp.lookAt(direction)
        # Kích hoạt nguồn sáng này cho toàn bộ scene
        base.render.setLight(self.dlnp) # type: ignore

    def update(self):
        """
        Cập nhật vị trí của nguồn sáng mỗi frame
        - Được gọi tự động mỗi frame bởi Ursina engine
        - Di chuyển nguồn sáng theo vị trí xe để ánh sáng luôn bao phủ khu vực chơi
        - Giữ cho bóng đổ luôn hiển thị chính xác quanh xe
        """
        self.dlnp.setPos(self.car.world_position)

    def update_resolution(self):
        """
        Cập nhật độ phân giải của bóng đổ
        - Được gọi khi người chơi thay đổi cài đặt đồ họa
        - Áp dụng độ phân giải mới cho shadow map
        """
        self.dlight.setShadowCaster(True, self.resolution, self.resolution)