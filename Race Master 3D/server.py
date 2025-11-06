"""
Tổng quan về file server.py:

File server.py định nghĩa class Server để tạo và quản lý server multiplayer cho game Race Master 3D.
Sử dụng UrsinaNetworking để handle kết nối client, đồng bộ hóa dữ liệu người chơi.
"""

from ursinanetworking import *

print("\nHello from the Race Master 3D Server!\n")

class Server:
    """
    Class Server quản lý server multiplayer.
    Tạo server, handle client connections, và đồng bộ hóa dữ liệu.
    """
    def __init__(self, ip, port):
        self.ip = ip  # Input field cho IP
        self.port = port  # Input field cho PORT
        self.start_server = False  # Cờ để bắt đầu server
        self.server_update = False  # Cờ cập nhật server

    def update_server(self):
        """
        Khởi tạo và cập nhật server khi start_server = True.
        """
        if self.start_server:
            # Tạo server với IP và PORT
            self.server = UrsinaNetworkingServer(self.ip.text, int(self.port.text))
            self.easy = EasyUrsinaNetworkingServer(self.server)
            
            @self.server.event
            def onClientConnected(client):
                """
                Event khi client kết nối.
                Tạo replicated variable cho player mới.
                """
                self.easy.create_replicated_variable(
                    f"player_{client.id}",
                    { "type" : "player", "id" : client.id, "username": "Guest", "position": (0, 0, 0), "rotation" : (0, 0, 0), "model" : "sports-car.obj", "texture" : "sports-red.png", "highscore": 0.0, "cosmetic": "none"}
                )
                print(f"{client} connected!")
                client.send_message("GetId", client.id)

            @self.server.event
            def onClientDisconnected(client):
                """
                Event khi client ngắt kết nối.
                Xóa replicated variable của player.
                """
                self.easy.remove_replicated_variable_by_name(f"player_{client.id}")
                
            @self.server.event
            def MyPosition(client, newpos):
                """
                Cập nhật vị trí player.
                """
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "position", newpos)

            @self.server.event
            def MyRotation(client, newrot):
                """
                Cập nhật rotation player.
                """
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "rotation", newrot)

            @self.server.event
            def MyModel(client, newmodel):
                """
                Cập nhật model xe player.
                """
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "model", newmodel)

            @self.server.event
            def MyTexture(client, newtex):
                """
                Cập nhật texture xe player.
                """
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "texture", newtex)

            @self.server.event
            def MyUsername(client, newuser):
                """
                Cập nhật username player.
                """
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "username", newuser)
        
            @self.server.event
            def MyHighscore(client, newscore):
                """
                Cập nhật highscore player.
                """
                self.easy.update_replicated_variable_by_name(f"player_{client.id}", "highscore", newscore)

            @self.server.event
            def MyCosmetic(client, newcos):
                """
                Cập nhật cosmetic player.
                """
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