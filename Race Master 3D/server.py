"""
Module quản lý server multiplayer cho game Race Master 3D.

Sử dụng UrsinaNetworking để tạo server và đồng bộ hóa dữ liệu giữa các client:
- Vị trí và rotation xe
- Loại xe và màu sắc
- Username và highscore
- Cosmetics (phụ kiện)
"""

from ursinanetworking import *

print("\nHello from the Race Master 3D Server!\n")

class Server:
    """Quản lý server multiplayer và đồng bộ hóa dữ liệu giữa các client."""
    
    def __init__(self, ip, port):
        """
        Khởi tạo server configuration.
        
        Args:
            ip: Input field chứa IP address
            port: Input field chứa port number
        """
        self.ip = ip
        self.port = port
        self.start_server = False
        self.server_update = False

    def update_server(self):
        """
        Khởi động server và đăng ký các event handlers.
        
        Được gọi khi start_server = True. Tạo replicated variables cho mỗi client
        và handle các sự kiện kết nối/ngắt kết nối/cập nhật dữ liệu.
        """
        if self.start_server:
            self.server = UrsinaNetworkingServer(self.ip.text, int(self.port.text))
            self.easy = EasyUrsinaNetworkingServer(self.server)
            
            @self.server.event
            def onClientConnected(client):
                """
                Event khi client kết nối.
                
                Tạo replicated variable với dữ liệu mặc định cho player mới.
                """
                self.easy.create_replicated_variable(
                    f"player_{client.id}",
                    { "type" : "player", "id" : client.id, "username": "Guest", "position": (0, 0, 0), "rotation" : (0, 0, 0), "model" : "sports-car.obj", "texture" : "sports-red.png", "highscore": 0.0, "cosmetic": "none"}
                )
                print(f"{client} connected!")
                client.send_message("GetId", client.id)

            @self.server.event
            def onClientDisconnected(client):
                """Event khi client ngắt kết nối - xóa replicated variable."""
                self.easy.remove_replicated_variable_by_name(f"player_{client.id}")
                
            @self.server.event
            def MyPosition(client, newpos):
                """Cập nhật vị trí xe của client."""
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "position", newpos)

            @self.server.event
            def MyRotation(client, newrot):
                """Cập nhật rotation xe của client."""
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "rotation", newrot)

            @self.server.event
            def MyModel(client, newmodel):
                """Cập nhật loại xe của client."""
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "model", newmodel)

            @self.server.event
            def MyTexture(client, newtex):
                """Cập nhật màu xe của client."""
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "texture", newtex)

            @self.server.event
            def MyUsername(client, newuser):
                """Cập nhật tên người chơi của client."""
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "username", newuser)
        
            @self.server.event
            def MyHighscore(client, newscore):
                """Cập nhật điểm cao nhất của client."""
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "highscore", newscore)

            @self.server.event
            def MyCosmetic(client, newcos):
                """Cập nhật phụ kiện xe của client."""
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "cosmetic", newcos)

            self.server_update = True
            self.start_server = False

if __name__ == "__main__":
    """
    Chạy server standalone khi file được execute trực tiếp.
    Tạo UI để nhập IP/PORT và start server.
    """
    from ursina import *

    app = Ursina()
    window.title = "Race Master 3D"
    window.borderless = False

    # Input fields cho IP và PORT
    ip = InputField(default_value = "IP", limit_content_to = "0123456789.localhost", color = color.black, alpha = 100, y = 0.1, parent = camera.ui)
    port = InputField(default_value = "PORT", limit_content_to = "0123456789", color = color.black, alpha = 100, y = 0.02, parent = camera.ui)

    server = Server(ip, port)

    Sky()

    def create_server():
        """
        Hàm tạo server khi click button.
        """
        server.start_server = True
        running = Text(text = "Running server...", scale = 1.5, line_height = 2, x = 0, origin = 0, y = 0, parent = camera.ui)
        create_server_button.disable()
        ip.disable()
        port.disable()
        stop_button.enable()

    def stop_server():
        """
        Dừng server và thoát.
        """
        import os
        os._exit(0)

    # Buttons
    create_server_button = Button(text = "C r e a t e", color = color.hex("F58300"), highlight_color = color.gray, scale_y = 0.1, scale_x = 0.3, y = -0.1, parent = camera.ui)
    create_server_button.on_click = Func(create_server)

    stop_button = Button(text = "S t o p", color = color.hex("D22828"), scale_y = 0.1, scale_x = 0.3, y = -0.2, parent = camera.ui)
    stop_button.disable()
    stop_button.on_click = Func(stop_server)
    
    def update():
        """
        Update loop cho server.
        """
        server.update_server()
        if server.server_update == True:
            server.easy.process_net_events()

    app.run()