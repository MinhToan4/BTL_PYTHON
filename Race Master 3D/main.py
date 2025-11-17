# ==================== IMPORTS VÀ CẤU HÌNH BAN ĐẦU ====================
# Import thư viện Ursina - framework 3D game chính
import render
from ursina import *
# Import thread để tải assets song song
from direct.stdpy import thread

# ==================== TẮT CẢNH BÁO PNG ====================
# Tắt cảnh báo về sRGB profile trong PNG để tránh spam console
import os
os.environ['PANDA3D_IGNORE_BAD_PROFILE'] = '1'

# Tắt cảnh báo iCCP và sRGB từ pnmimage
import warnings
warnings.filterwarnings("ignore", message=".*iCCP.*")
warnings.filterwarnings("ignore", message=".*sRGB.*")

# ==================== IMPORT CÁC MODULE GAME ====================
# Import class Car - đối tượng xe chính của người chơi
from car import Car
# Import class AICar - AI điều khiển xe bot
from ai import AICar

# Import Multiplayer - hệ thống chơi mạng
from multiplayer import Multiplayer
# Import MainMenu - giao diện menu chính
from main_menu import MainMenu

# Import SunLight - hệ thống ánh sáng mặt trời
from sun import SunLight

# Import Race Master 3D Achievements - hệ thống thành tựu
from achievements import *

# ==================== IMPORT CÁC TRACK ====================
# Import tất cả các class track - định nghĩa đường đua
from tracks.sand_track import SandTrack
from tracks.grass_track import GrassTrack
from tracks.snow_track import SnowTrack
from tracks.forest_track import ForestTrack
from tracks.savannah_track import SavannahTrack
from tracks.lake_track import LakeTrack

# ==================== CẤU HÌNH TEXT ====================
# Thiết lập font và độ phân giải mặc định cho tất cả text trong game
Text.default_font = "./assets/Roboto.ttf"
Text.default_resolution = 1080 * Text.size

# ==================== KHỞI TẠO ỨNG DỤNG URSINA ====================
# Tạo ứng dụng Ursina - cửa sổ game chính
app = Ursina()
# Thiết lập tiêu đề cửa sổ
window.title = "Race Master 3D"
# Không dùng borderless window
window.borderless = False
# Hiển thị splash screen của Ursina
window.show_ursina_splash = True
# Tắt nút cog (settings)
window.cog_button.disable()
# Tắt FPS counter
window.fps_counter.disable()
# Tắt nút exit
window.exit_button.disable()

# ==================== CẤU HÌNH FULLSCREEN ====================
# Kiểm tra platform để thiết lập fullscreen
if sys.platform != "darwin":  # Nếu không phải macOS
    window.fullscreen = True  # Bật fullscreen
else:  # Nếu là macOS
    window.size = window.fullscreen_size  # Đặt kích thước fullscreen
    window.position = Vec2(  # Căn giữa màn hình
        int((window.screen_resolution[0] - window.fullscreen_size[0]) / 2),
        int((window.screen_resolution[1] - window.fullscreen_size[1]) / 2)
    )

# ==================== HÀM TẢI ASSETS ====================
# Tải tất cả models và textures trong thread riêng để không block main thread
def load_assets():
    # ==================== DANH SÁCH MODELS CẦN TẢI ====================
    models_to_load = [
        # Cars - các model xe với đường dẫn đầy đủ
        "assets/cars/sports-car.obj", "assets/cars/muscle-car.obj", "assets/cars/limousine.obj",
        "assets/cars/lorry.obj", "assets/cars/hatchback.obj", "assets/cars/rally-car.obj",
        # Tracks - các model đường đua
        "assets/sand_track/sand_track.obj", "assets/grass_track/grass_track.obj", "assets/snow_track/snow_track.obj",
        "assets/forest_track/forest_track.obj", "assets/savannah_track/savannah_track.obj", "assets/lake_track/lake_track.obj",
        "assets/particles/particles.obj",
        # Track Bounds - biên giới đường đua để phát hiện va chạm
        "assets/sand_track/sand_track_bounds.obj", "assets/grass_track/grass_track_bounds.obj", "assets/snow_track/snow_track_bounds.obj",
        "assets/forest_track/forest_track_bounds.obj", "assets/savannah_track/savannah_track_bounds.obj", "assets/lake_track/lake_track_bounds.obj",
        # Track Details - chi tiết trang trí đường đua
        "assets/sand_track/rocks-sand.obj", "assets/sand_track/cacti-sand.obj",
        "assets/grass_track/trees-grass.obj", "assets/grass_track/thintrees-grass.obj", "assets/grass_track/rocks-grass.obj", "assets/grass_track/grass-grass_track.obj",
        "assets/snow_track/trees-snow.obj", "assets/snow_track/thintrees-snow.obj", "assets/snow_track/rocks-snow.obj",
        "assets/forest_track/trees-forest.obj", "assets/forest_track/thintrees-forest.obj",
        "assets/savannah_track/rocks-savannah.obj", "assets/savannah_track/trees-savannah.obj",
        "assets/lake_track/trees-lake.obj", "assets/lake_track/thintrees-lake.obj", "assets/lake_track/rocks-lake.obj",
        "assets/lake_track/bigrocks-lake.obj", "assets/lake_track/grass-lake.obj", "assets/lake_track/lake_bounds.obj",
        # Cosmetics - trang phục và phụ kiện cho xe
        "assets/cars/viking_helmet.obj", "assets/cars/duck.obj", "assets/cars/banana.obj", "assets/cars/surfinbird.obj", "assets/cars/surfboard.obj"
    ]

    # ==================== DANH SÁCH TEXTURES CẦN TẢI ====================
    textures_to_load = [
        # Car Textures - texture cho các loại xe
        # Sports Car
        "sports-red.png", "sports-orange.png", "sports-green.png", "sports-white.png", "sports-black.png", "sports-blue.png",
        # Muscle Car
        "muscle-red.png", "muscle-orange.png", "muscle-green.png", "muscle-white.png", "muscle-black.png", "muscle-blue.png",
        # Limo
        "limo-red.png", "limo-orange.png", "limo-green.png", "limo-white.png", "limo-black.png", "limo-blue.png",
        # Lorry
        "lorry-red.png", "lorry-orange.png", "lorry-green.png", "lorry-white.png", "lorry-black.png", "lorry-blue.png",
        # Hatchback
        "hatchback-red.png", "hatchback-orange.png", "hatchback-green.png", "hatchback-white.png", "hatchback-black.png", "hatchback-blue.png",
        # Race Master Car
        "rally-red.png", "rally-orange.png", "rally-green.png", "rally-white.png", "rally-black.png", "rally-blue.png",
        # Track Textures - texture cho đường đua
        "sand_track.png", "grass_track.png", "snow_track.png", "forest_track.png",
        "savannah_track.png", "lake_track.png",
        # Track Detail Textures - texture cho chi tiết đường đua
        "rock-sand.png", "cactus-sand.png", "tree-grass.png", "thintree-grass.png", "rock-grass.png", "grass-grass_track.png", "tree-snow.png",
        "thintree-snow.png", "rock-snow.png", "tree-forest.png", "thintree-forest.png", "rock-savannah.png", "tree-savannah.png",
        "tree-lake.png", "rock-lake.png", "grass-lake.png", "thintree-lake.png", "bigrock-lake.png",
        # Particle Textures - texture cho hiệu ứng hạt
        "particle_sand_track.png", "particle_grass_track.png", "particle_snow_track",
        "particle_forest_track.png", "particle_savannah_track.png", "particle_lake_track.png",
        # Cosmetic Textures + Icons - texture cho cosmetics và icons
        "viking_helmet.png", "surfinbird.png", "surfboard.png", "viking_helmet-icon.png", "duck-icon.png",
        "banana-icon.png", "surfinbird-icon.png"
    ]

    # ==================== TẢI MODELS ====================
    for i, m in enumerate(models_to_load):
        try:
            load_model(m)  # Tải model vào bộ nhớ
        except Exception as e:
            print(f"Failed to load model {m}: {e}")

    # ==================== TẢI TEXTURES ====================
    for i, t in enumerate(textures_to_load):
        try:
            load_texture(t)  # Tải texture vào bộ nhớ
        except Exception as e:
            print(f"Failed to load texture {t}: {e}")

# ==================== HÀM DELAY TẢI ASSETS ====================
# Chờ app khởi tạo xong rồi mới tải assets trong thread riêng
def delayed_load_assets():
    try:
        # Tạo thread mới để tải assets song song
        thread.start_new_thread(function=load_assets, args="")
    except Exception as e:
        print("error starting thread", e)

# Gọi hàm tải assets sau 0.5 giây
invoke(delayed_load_assets, delay=0.5)

# ==================== KHỞI TẠO ĐỐI TƯỢNG CHÍNH ====================
# Tạo đối tượng xe chính của người chơi
car = Car()
car.sports_car()  # Thiết lập xe mặc định là sports car

# ==================== KHỞI TẠO TRACKS ====================
# Tạo tất cả các track (đường đua)
sand_track = SandTrack(car)
grass_track = GrassTrack(car)
snow_track = SnowTrack(car)
forest_track = ForestTrack(car)
savannah_track = SavannahTrack(car)
lake_track = LakeTrack(car)

# ==================== GÁN TRACKS CHO CAR ====================
# Gán các track vào car để car có thể tham chiếu
car.sand_track = sand_track
car.grass_track = grass_track
car.snow_track = snow_track
car.forest_track = forest_track
car.savannah_track = savannah_track
car.lake_track = lake_track

# ==================== KHỞI TẠO AI ====================
# Tạo danh sách AI cars
ai_list = []

# Tạo 3 AI cars với các track
ai = AICar(car, ai_list, sand_track, grass_track, snow_track, forest_track, savannah_track, lake_track)
ai1 = AICar(car, ai_list, sand_track, grass_track, snow_track, forest_track, savannah_track, lake_track)
ai2 = AICar(car, ai_list, sand_track, grass_track, snow_track, forest_track, savannah_track, lake_track)

# Thêm AI vào danh sách
ai_list.append(ai)
ai_list.append(ai1)
ai_list.append(ai2)

# Gán danh sách AI cho car
car.ai_list = ai_list

# ==================== KHỞI TẠO MAIN MENU ====================
# Tạo menu chính với tất cả các đối tượng
main_menu = MainMenu(car, ai_list, sand_track, grass_track, snow_track, forest_track, savannah_track, lake_track)

# ==================== KHỞI TẠO ACHIEVEMENTS ====================
# Tạo hệ thống thành tựu
achievements = RaceMasterAchievements(car, main_menu, sand_track, grass_track, snow_track, forest_track, savannah_track, lake_track)

# ==================== KHỞI TẠO LIGHTING ====================
# Tạo ánh sáng mặt trời với shadows
sun = SunLight(direction=(-0.7, -0.9, 0.5), resolution=3072, car=car)
# Tạo ánh sáng ambient (môi trường)
ambient = AmbientLight(color=Vec4(0.5, 0.55, 0.66, 0) * 0.75)

# Gán sun cho main_menu
main_menu.sun = sun

# ==================== KHỞI TẠO SKY ====================
# Tạo bầu trời với texture
Sky(texture="sky")

# ==================== HÀM UPDATE CHÍNH ====================
# Hàm này được gọi mỗi frame để cập nhật logic game
def update():
    # ==================== XỬ LÝ MULTIPLAYER ====================
    # Nếu người chơi chọn multiplayer, khởi tạo Multiplayer
    if car.multiplayer:
        global multiplayer
        multiplayer = Multiplayer(car)
        car.multiplayer_update = True
        car.multiplayer = False

    # ==================== CẬP NHẬT MULTIPLAYER ====================
    # Nếu đang trong multiplayer mode, cập nhật trạng thái
    if car.multiplayer_update:
        multiplayer.update_multiplayer()
        # Kiểm tra kết nối và hiển thị text tương ứng
        if multiplayer.client.connected:
            if car.connected_text:
                main_menu.connected.enable()  # Hiển thị "Connected"
                car.connected_text = False
            else:
                invoke(main_menu.connected.disable, delay=2)  # Tắt sau 2 giây
            main_menu.not_connected.disable()  # Tắt "Not Connected"
        else:
            if car.disconnected_text:
                main_menu.not_connected.enable()  # Hiển thị "Not Connected"
                car.disconnected_text = False
            else:
                invoke(main_menu.not_connected.disable, delay=2)  # Tắt sau 2 giây
            main_menu.connected.disable()  # Tắt "Connected"

    # ==================== CẬP NHẬT SERVER ====================
    # Nếu đang host server, cập nhật server
    if car.server_running:
        car.server.update_server()
        if car.server.server_update:
            car.server.easy.process_net_events()

    # ==================== CẬP NHẬT THỜI GIAN CHO ACHIEVEMENTS ====================
    # Tăng thời gian chơi để unlock achievements
    if achievements.time_spent < 10:
        achievements.time_spent += time.dt

# ==================== HÀM INPUT ====================
# Hàm xử lý input từ bàn phím
def input(key):
    # ==================== PHÍM TẮT HAND CONTROLLER ====================
    # Nhấn 'h' để bật/tắt hand controller
    if key == 'h':
        if car.toggle_hand_controller():
            print("Hand Controller: BẬT - Sử dụng cử chỉ tay để điều khiển!")
        else:
            print("Hand Controller: TẮT - Sử dụng bàn phím để điều khiển.")

    # ==================== GỬI DỮ LIỆU MULTIPLAYER ====================
    # Nếu đang trong multiplayer, gửi vị trí, rotation, texture, username, highscore
    if car.multiplayer_update:
        multiplayer.client.send_message("MyPosition", tuple(car.position))
        multiplayer.client.send_message("MyRotation", tuple(car.rotation))
        multiplayer.client.send_message("MyTexture", str(car.texture))
        multiplayer.client.send_message("MyUsername", str(car.username_text))
        multiplayer.client.send_message("MyHighscore", str(round(car.highscore_count, 2)))
        multiplayer.client.send_message("MyCosmetic", str(car.current_cosmetic))
        multiplayer.client.send_message("MyModel", str(car.model_path))

# ==================== CHẠY ỨNG DỤNG ====================
# Khởi động vòng lặp game
app.run()