"""
Module quản lý chế độ multiplayer trong game Race Master 3D.

Sử dụng UrsinaNetworking để kết nối với server và đồng bộ hóa dữ liệu giữa các client:
- Vị trí và rotation xe real-time
- Loại xe và màu sắc
- Username và highscore
- Cosmetics (phụ kiện)

Sử dụng interpolation để làm mượt chuyển động của xe người chơi khác.
"""

from ursinanetworking import *
from ursina import Entity, Vec3, color, destroy
from car import CarRepresentation, CarUsername

class Multiplayer(Entity):
    """Quản lý client multiplayer và đồng bộ hóa dữ liệu với server."""
    
    def __init__(self, car):
        """
        Khởi tạo multiplayer client.
        
        Args:
            car: Đối tượng xe của người chơi hiện tại
        """
        self.car = car

        if str(self.car.ip.text) != "IP" and str(self.car.port.text) != "PORT":
            self.client = UrsinaNetworkingClient(self.car.ip.text, int(self.car.port.text))
            self.easy = EasyUrsinaNetworkingClient(self.client)

            # Dictionaries lưu trữ dữ liệu của người chơi khác
            self.players = {}  # CarRepresentation objects
            self.players_target_name = {}
            self.players_target_pos = {}
            self.players_target_rot = {}
            self.players_target_model = {}
            self.players_target_tex = {}
            self.players_target_score = {}
            self.players_target_cos = {}

            self.selfId = -1

            @self.client.event
            def GetId(id):
                """Nhận ID từ server khi kết nối thành công."""
                self.selfId = id
                print(f"My ID is : {self.selfId}")

            @self.easy.event
            def onReplicatedVariableCreated(variable):
                """
                Event khi người chơi mới join vào game.
                
                Tạo CarRepresentation để hiển thị xe của người chơi đó.
                """
                variable_name = variable.name
                variable_type = variable.content["type"]

                if variable_type == "player":
                    # Khởi tạo dữ liệu mặc định
                    self.players_target_pos[variable_name] = Vec3(-80, -30, 15)
                    self.players_target_rot[variable_name] = Vec3(0, 90, 0)
                    self.players_target_model[variable_name] = "./assets/cars/sports-car.obj"
                    self.players_target_tex[variable_name] = "./assets/cars/garage/sports-car/sports-red.png"
                    self.players_target_name[variable_name] = "Guest"
                    self.players_target_score[variable_name] = 0.0
                    self.players_target_cos[variable_name] = "none"
                    
                    # Tạo xe đại diện cho người chơi
                    self.players[variable_name] = CarRepresentation(self.car, (-80, -30, 15), (0, 90, 0))
                    self.players[variable_name].text_object = CarUsername(self.players[variable_name])
                    
                    # Force enable để đảm bảo xe được hiển thị
                    self.players[variable_name].visible = True
                    self.players[variable_name].enabled = True
                    self.players[variable_name].collider = None  # Tắt collider để không ảnh hưởng physics
                    
                    print(f"Tạo người chơi mới: {variable_name}, ID: {variable.content['id']}")

                    # Chỉ ẩn xe của chính mình (không ẩn text để vẫn thấy tên)
                    if self.selfId == int(variable.content["id"]):
                        self.players[variable_name].visible = False
                        print(f"Ẩn xe của chính mình: {variable_name}")

            @self.easy.event
            def onReplicatedVariableUpdated(variable):
                """Event khi dữ liệu người chơi được cập nhật từ server."""
                self.players_target_pos[variable.name] = variable.content["position"]
                self.players_target_rot[variable.name] = variable.content["rotation"]
                self.players_target_model[variable.name] = variable.content["model"]
                self.players_target_tex[variable.name] = variable.content["texture"]
                self.players_target_name[variable.name] = variable.content["username"]
                self.players_target_score[variable.name] = variable.content["highscore"]
                self.players_target_cos[variable.name] = variable.content["cosmetic"]

            @self.easy.event
            def onReplicatedVariableRemoved(variable):
                """Event khi người chơi disconnect khỏi server."""
                variable_name = variable.name
                variable_type = variable.content["type"]
                
                if variable_type == "player":
                    if variable_name in self.players:
                        destroy(self.players[variable_name].text_object)
                        destroy(self.players[variable_name])
                        del self.players[variable_name]
                        print(f"Xóa người chơi: {variable_name}")

    def update_multiplayer(self):
        """
        Cập nhật trạng thái của tất cả người chơi mỗi frame.
        
        Sử dụng interpolation (chia 25) để làm mượt chuyển động thay vì 
        cập nhật đột ngột. Đồng thời cập nhật leaderboard.
        """
        for p in self.players:
            if p not in self.players_target_pos:
                continue
                
            # Interpolation để làm mượt chuyển động
            self.players[p].position += (Vec3(self.players_target_pos[p]) - self.players[p].position) / 25
            self.players[p].rotation += (Vec3(self.players_target_rot[p]) - self.players[p].rotation) / 25
            
            # Cập nhật model/texture khi có thay đổi
            if self.players_target_model[p] != self.players[p].model or self.players_target_tex[p] != self.players[p].texture:
                self.players[p].model = f"{self.players_target_model[p]}"
                self.players[p].texture = f"{self.players_target_tex[p]}"
                print(f"Cập nhật model/texture cho {p}: {self.players_target_model[p]}, {self.players_target_tex[p]}")
            
            # Cập nhật username và highscore
            self.players[p].text_object.text = f"{self.players_target_name[p]}"
            self.players[p].highscore = f"{self.players_target_score[p]}"

            # Cập nhật cosmetics
            if self.players_target_cos[p] == "viking":
                for cosmetic in self.players[p].cosmetics:
                    cosmetic.disable()
                self.players[p].viking_helmet.enable()
            elif self.players_target_cos[p] == "duck":
                for cosmetic in self.players[p].cosmetics:
                    cosmetic.disable()
                self.players[p].duck.enable()
            elif self.players_target_cos[p] == "banana":
                for cosmetic in self.players[p].cosmetics:
                    cosmetic.disable()
                self.players[p].banana.enable()
            elif self.players_target_cos[p] == "surfinbird":
                for cosmetic in self.players[p].cosmetics:
                    cosmetic.disable()
                self.players[p].surfinbird.enable()

            # Chỉ ẩn khi xe chính bị disable (ví dụ: trong menu)
            # KHÔNG ẩn xe của người chơi khác khi đang chơi
            if self.car.enabled == False:
                self.players[p].disable()
            else:
                # Luôn enable xe người chơi khác khi đang chơi, trừ xe của chính mình
                if p != f"player_{self.selfId}":
                    self.players[p].enable()
                    self.players[p].visible = True

        # Cập nhật leaderboard với thông tin người chơi
        self._update_leaderboard()

        # Xử lý network events
        self.easy.process_net_events()

    def _update_leaderboard(self):
        """Cập nhật leaderboard với thông tin của tất cả người chơi."""
        leaderboard_slots = [
            ("player_0", "leaderboard_01"),
            ("player_1", "leaderboard_02"),
            ("player_2", "leaderboard_03"),
            ("player_3", "leaderboard_04"),
            ("player_4", "leaderboard_05"),
        ]
        
        for player_key, leaderboard_attr in leaderboard_slots:
            if player_key in self.players:
                player = self.players[player_key]
                setattr(self.car, leaderboard_attr, 
                       f"{player.text_object.text} | {player.highscore}")
            else:
                setattr(self.car, leaderboard_attr, "")