"""
Tổng quan về file multiplayer.py:

File multiplayer.py định nghĩa class Multiplayer, xử lý chế độ chơi mạng trong game Race Master 3D.
Nó sử dụng thư viện UrsinaNetworking để kết nối với server, đồng bộ hóa vị trí, rotation, model, texture, username, highscore của các người chơi khác.
Cấu trúc chính bao gồm: khởi tạo client, xử lý events từ server, cập nhật vị trí người chơi, và cập nhật leaderboard.
"""

from ursinanetworking import *
from ursina import Entity, Vec3, color, destroy
from car import CarRepresentation, CarUsername

class Multiplayer(Entity):
    """
    Class Multiplayer quản lý chế độ chơi mạng.
    Kế thừa từ Entity của Ursina để tích hợp vào game.
    """
    def __init__(self, car):
        """
        Khởi tạo Multiplayer với tham chiếu đến car.
        Tạo client kết nối đến server nếu IP và PORT hợp lệ.
        """
        self.car = car

        # Nếu input field không phải mặc định, tạo client
        if str(self.car.ip.text) != "IP" and str(self.car.port.text) != "PORT":
            # Tạo client kết nối đến server
            self.client = UrsinaNetworkingClient(self.car.ip.text, int(self.car.port.text))
            self.easy = EasyUrsinaNetworkingClient(self.client)

            # Giá trị mục tiêu của người chơi
            self.players = {}  # Dictionary chứa các đối tượng CarRepresentation
            self.players_target_name = {}  # Tên người chơi
            self.players_target_pos = {}  # Vị trí mục tiêu
            self.players_target_rot = {}  # Rotation mục tiêu
            self.players_target_model = {}  # Model xe mục tiêu
            self.players_target_tex = {}  # Texture xe mục tiêu
            self.players_target_score = {}  # Điểm số mục tiêu
            self.players_target_cos = {}  # Trang phục mục tiêu

            self.selfId = -1  # ID của chính mình

            @self.client.event
            def GetId(id):
                """
                Event nhận ID từ server.
                """
                self.selfId = id
                print(f"My ID is : {self.selfId}")

            @self.easy.event
            def onReplicatedVariableCreated(variable):
                """
                Event khi một biến replicated được tạo (người chơi mới tham gia).
                """
                variable_name = variable.name
                variable_type = variable.content["type"]

                if variable_type == "player":
                    # Thiết lập giá trị mặc định cho người chơi mới
                    self.players_target_pos[variable_name] = Vec3(-80, -30, 15)
                    self.players_target_rot[variable_name] = Vec3(0, 90, 0)
                    self.players_target_model[variable_name] = "./assets/cars/sports-car.obj"
                    self.players_target_tex[variable_name] = "./assets/cars/garage/sports-car/sports-red.png"
                    self.players_target_name[variable_name] = "Guest"
                    self.players_target_score[variable_name] = 0.0
                    self.players_target_cos[variable_name] = "none"
                    # Tạo CarRepresentation cho người chơi
                    self.players[variable_name] = CarRepresentation(self.car, (-80, -30, 15), (0, 90, 0))
                    self.players[variable_name].text_object = CarUsername(self.players[variable_name])

                    # Nếu là chính mình, ẩn và đổi màu
                    if self.selfId == int(variable.content["id"]):
                        self.players[variable_name].color = color.red
                        self.players[variable_name].visible = False

            @self.easy.event
            def onReplicatedVariableUpdated(variable):
                """
                Event khi một biến replicated được cập nhật (người chơi di chuyển, thay đổi).
                """
                self.players_target_pos[variable.name] = variable.content["position"]
                self.players_target_rot[variable.name] = variable.content["rotation"]
                self.players_target_model[variable.name] = variable.content["model"]
                self.players_target_tex[variable.name] = variable.content["texture"]
                self.players_target_name[variable.name] = variable.content["username"]
                self.players_target_score[variable.name] = variable.content["highscore"]
                self.players_target_cos[variable.name] = variable.content["cosmetic"]

            @self.easy.event
            def onReplicatedVariableRemoved(variable):
                """
                Event khi một biến replicated bị xóa (người chơi rời đi).
                """
                variable_name = variable.name
                variable_type = variable.content["type"]
                
                if variable_type == "player":
                    # Hủy đối tượng và xóa khỏi dictionary
                    destroy(self.players[variable_name])
                    del self.players[variable_name]

    def update_multiplayer(self):
        """
        Hàm cập nhật multiplayer mỗi frame.
        Đồng bộ hóa vị trí, rotation, model, texture, tên, điểm số của người chơi khác.
        Cập nhật leaderboard.
        """
        # Cập nhật vị trí và rotation của tất cả người chơi
        for p in self.players:
            # Nội suy vị trí và rotation mượt mà
            self.players[p].position += (Vec3(self.players_target_pos[p]) - self.players[p].position) / 25
            self.players[p].rotation += (Vec3(self.players_target_rot[p]) - self.players[p].rotation) / 25
            # Cập nhật model và texture
            self.players[p].model = f"{self.players_target_model[p]}"
            self.players[p].texture = f"{self.players_target_tex[p]}"
            # Cập nhật tên và điểm số
            self.players[p].text_object.text = f"{self.players_target_name[p]}"
            self.players[p].highscore = f"{self.players_target_score[p]}"

            # Cập nhật trang phục
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

            # Ẩn/hiện người chơi dựa trên trạng thái car chính
            if self.car.enabled == False:
                self.players[p].disable()
            elif self.car.enabled == True:
                self.players[p].enable()

        # Cập nhật leaderboard
        if "player_0" in self.players:
            self.car.leaderboard_01 = str(self.players["player_0"].text_object.text) + " | " + str(self.players["player_0"].highscore)
        else:
            self.car.leaderboard_01 = ""
        if "player_1" in self.players:
            self.car.leaderboard_02 = str(self.players["player_1"].text_object.text) + " | " + str(self.players["player_1"].highscore)
        else:
            self.car.leaderboard_02 = ""
        if "player_2" in self.players:
            self.car.leaderboard_03 = str(self.players["player_2"].text_object.text) + " | " + str(self.players["player_2"].highscore)
        else:
            self.car.leaderboard_03 = ""
        if "player_3" in self.players:
            self.car.leaderboard_04 = str(self.players["player_3"].text_object.text) + " | " + str(self.players["player_3"].highscore)
        else:
            self.car.leaderboard_04 = ""
        if "player_4" in self.players:
            self.car.leaderboard_05 = str(self.players["player_4"].text_object.text) + " | " + str(self.players["player_4"].highscore)
        else:
            self.car.leaderboard_05 = ""

        # Xử lý các event mạng
        self.easy.process_net_events()