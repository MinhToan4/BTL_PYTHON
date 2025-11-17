"""
Tổng quan về file achievements.py:

File achievements.py định nghĩa hệ thống thành tựu cho game Race Master 3D, sử dụng thư viện UrsinaAchievements.
Nó tạo ra các thành tựu dựa trên hành động của người chơi như hoàn thành đường đua, mở khóa xe mới, đạt thời gian nhanh, v.v.
Cấu trúc chính bao gồm: class Race Master 3D Achievements chính và các class con cho từng track (SandTrackAchievements, GrassTrackAchievements, etc.).
Mỗi thành tựu có điều kiện kiểm tra và khi đạt được sẽ hiển thị thông báo và âm thanh.
"""

# Hệ thống thành tựu cho game
# Sử dụng thư viện UrsinaAchievements để quản lý các thành tựu trong game
# File này định nghĩa tất cả các thành tựu mà người chơi có thể đạt được

from UrsinaAchievements import create_achievement

# Lớp chính quản lý tất cả thành tựu trong game
class RaceMasterAchievements():
    def __init__(self, car, main_menu, sand_track, grass_track, snow_track, forest_track, savannah_track, lake_track):
        # Khởi tạo các tham chiếu đến các đối tượng chính của game
        self.car = car                    # Đối tượng xe player
        self.main_menu = main_menu        # Hệ thống menu chính
        self.sand_track = sand_track      # Đường đua sa mạc
        self.grass_track = grass_track    # Đường đua đồng cỏ
        self.snow_track = snow_track      # Đường đua tuyết
        self.forest_track = forest_track  # Đường đua rừng
        self.savannah_track = savannah_track  # Đường đua thảo nguyên
        self.lake_track = lake_track      # Đường đua hồ

        # Biến đếm thời gian đã chơi (số giây)
        self.time_spent = 0

        # Tạo các instance cho từng loại thành tựu theo đường đua
        # Mỗi instance quản lý thành tựu cho một đường đua cụ thể
        sand_achievements = SandTrackAchievements(self.car, self.main_menu, self.sand_track)
        grass_achievements = GrassTrackAchievements(self.car, self.main_menu, self.grass_track)
        snow_achievements = SnowTrackAchievements(self.car, self.main_menu, self.snow_track)
        forest_achievements = ForestTrackAchievements(self.car, self.main_menu, self.forest_track)
        savannah_achievements = SavannahTrackAchievements(self.car, self.main_menu, self.savannah_track)
        lake_achievements = LakeTrackAchievements(self.car, self.main_menu, self.lake_track)
        car_achievements = CarAchievements(self.car, self.main_menu, self.sand_track, self.grass_track, self.snow_track, self.forest_track, self.savannah_track, self.lake_track)

        # ==================== THÀNH TỰU CƠ BẢN ====================
        # Các thành tựu đơn giản, dễ đạt được khi mới chơi game
        create_achievement("Chơi game nào!", self.play_the_game, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Đua trên đường đua sa mạc lần đầu tiên!", sand_achievements.play_sand_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Đua trên đường đua đồng cỏ lần đầu tiên!", grass_achievements.play_grass_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Đua trên đường đua tuyết lần đầu tiên!", snow_achievements.play_snow_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Đua trên đường đua rừng lần đầu tiên!", forest_achievements.play_forest_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Đua trên đường đua thảo nguyên lần đầu tiên!", savannah_achievements.play_savannah_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Đua trên đường đua hồ lần đầu tiên!", lake_achievements.play_lake_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Đua với AI!", self.race_against_ai, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Chơi Multiplayer!", self.play_multiplayer, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Vào Garage!", self.garage, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Chơi Time Trial!", self.time_trial, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa chế độ Drift!", self.unlock_drift, icon = "confetti.png", ringtone = "unlock.mp3")

        # ==================== THÀNH TỰU THỜI GIAN ====================
        # Các thành tựu dựa trên thời gian hoàn thành đường đua (càng nhanh càng tốt)
        create_achievement("Dưới 20 giây trên đường đua sa mạc!", sand_achievements.twenty_seconds_sand_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 17 giây trên đường đua sa mạc!", sand_achievements.seventeen_seconds_sand_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 15 giây trên đường đua sa mạc!", sand_achievements.fifteen_seconds_sand_track, icon = "confetti.png", ringtone = "unlock.mp3")

        create_achievement("Dưới 22 giây trên đường đua đồng cỏ!", grass_achievements.twentytwo_seconds_grass_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 20 giây trên đường đua đồng cỏ!", grass_achievements.twenty_seconds_grass_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 18 giây trên đường đua đồng cỏ!", grass_achievements.eighteen_seconds_grass_track, icon = "confetti.png", ringtone = "unlock.mp3")

        create_achievement("Dưới 40 giây trên đường đua tuyết!", snow_achievements.fourty_seconds_snow_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 36 giây trên đường đua tuyết!", snow_achievements.thirtysix_seconds_snow_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 33 giây trên đường đua tuyết!", snow_achievements.thirtythree_seconds_snow_track, icon = "confetti.png", ringtone = "unlock.mp3")

        create_achievement("Dưới 30 giây trên đường đua rừng!", forest_achievements.thirty_seconds_forest_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 28 giây trên đường đua rừng!", forest_achievements.twentyeight_seconds_forest_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 26 giây trên đường đua rừng!", forest_achievements.twentysix_seconds_forest_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 25 giây trên đường đua rừng!", forest_achievements.twentyfive_seconds_forest_track, icon = "confetti.png", ringtone = "unlock.mp3")

        create_achievement("Dưới 20 giây trên đường đua thảo nguyên!", savannah_achievements.twenty_seconds_savannah_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 18 giây trên đường đua thảo nguyên!", savannah_achievements.eighteen_seconds_savannah_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 16 giây trên đường đua thảo nguyên!", savannah_achievements.sixteen_seconds_savannah_track, icon = "confetti.png", ringtone = "unlock.mp3")

        create_achievement("Dưới 60 giây trên đường đua hồ!", lake_achievements.sixty_seconds_lake_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 55 giây trên đường đua hồ!", lake_achievements.fiftyfive_seconds_lake_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 50 giây trên đường đua hồ!", lake_achievements.fifty_seconds_lake_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Dưới 47 giây trên đường đua hồ!", lake_achievements.fourtyseven_seconds_lake_track, icon = "confetti.png", ringtone = "unlock.mp3")

        # ==================== THÀNH TỰU MỞ KHÓA XE ====================
        # Mở khóa các loại xe mới bằng cách đạt thành tích trên đường đua
        create_achievement("Mở khóa Muscle Car!", car_achievements.unlock_muscle_car, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa Limo!", car_achievements.unlock_limo, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa Lorry!", car_achievements.unlock_lorry, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa Hatchback!", car_achievements.unlock_hatchback, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa Race Master Car!", car_achievements.unlock_rally, icon = "confetti.png", ringtone = "unlock.mp3")

        # ==================== THÀNH TỰU MÀU SẮC ====================
        # Mở khóa các màu sắc khác nhau cho từng loại xe
        create_achievement("Mở khóa màu xanh cho Sports Car!", car_achievements.sports_green, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu cam cho Sports Car!", car_achievements.sports_orange, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu trắng cho Sports Car!", car_achievements.sports_white, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu đen cho Sports Car!", car_achievements.sports_black, icon = "confetti.png", ringtone = "unlock.mp3")

        create_achievement("Mở khóa màu đỏ cho Muscle Car!", car_achievements.muscle_red, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu xanh cho Muscle Car!", car_achievements.muscle_blue, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu xanh lá cho Muscle Car!", car_achievements.muscle_green, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu trắng cho Muscle Car!", car_achievements.muscle_white, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu đen cho Muscle Car!", car_achievements.muscle_black, icon = "confetti.png", ringtone = "unlock.mp3")

        create_achievement("Mở khóa màu đỏ cho Limo!", car_achievements.limo_red, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu xanh cho Limo!", car_achievements.limo_blue, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu xanh lá cho Limo!", car_achievements.limo_green, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu trắng cho Limo!", car_achievements.limo_white, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu cam cho Limo!", car_achievements.limo_orange, icon = "confetti.png", ringtone = "unlock.mp3")

        create_achievement("Mở khóa màu đỏ cho Lorry!", car_achievements.lorry_red, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu xanh cho Lorry!", car_achievements.lorry_blue, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu xanh lá cho Lorry!", car_achievements.lorry_green, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu cam cho Lorry!", car_achievements.lorry_orange, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu đen cho Lorry!", car_achievements.lorry_black, icon = "confetti.png", ringtone = "unlock.mp3")

        create_achievement("Mở khóa màu đỏ cho Hatchback!", car_achievements.hatchback_red, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu xanh cho Hatchback!", car_achievements.hatchback_blue, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu trắng cho Hatchback!", car_achievements.hatchback_white, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu cam cho Hatchback!", car_achievements.hatchback_orange, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu đen cho Hatchback!", car_achievements.hatchback_black, icon = "confetti.png", ringtone = "unlock.mp3")

        create_achievement("Mở khóa màu trắng cho Rally Car!", car_achievements.rally_white, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu xanh cho Rally Car!", car_achievements.rally_blue, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu xanh lá cho Rally Car!", car_achievements.rally_green, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu cam cho Rally Car!", car_achievements.rally_orange, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa màu đen cho Rally Car!", car_achievements.rally_black, icon = "confetti.png", ringtone = "unlock.mp3")

        # ==================== THÀNH TỰU MỞ KHÓA ĐƯỜNG ĐUA ====================
        # Mở khóa các đường đua mới bằng cách hoàn thành đường đua trước đó
        create_achievement("Mở khóa đường đua đồng cỏ!", self.unlock_grass_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa đường đua tuyết!", self.unlock_snow_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa đường đua rừng!", self.unlock_forest_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa đường đua thảo nguyên!", self.unlock_savannah_track, icon = "confetti.png", ringtone = "unlock.mp3")
        create_achievement("Mở khóa đường đua hồ!", self.unlock_lake_track, icon = "confetti.png", ringtone = "unlock.mp3")
    
    # ==================== CÁC HÀM KIỂM TRA THÀNH TỰU ====================
    
    # Kiểm tra đã chơi game hơn 3 giây chưa
    # Đây là thành tựu cơ bản nhất, chỉ cần bắt đầu chơi
    def play_the_game(self):
        return self.time_spent > 3

    # Kiểm tra có đang chơi với AI không
    # Thành tựu này đạt được khi có xe AI được kích hoạt
    def race_against_ai(self):
        return self.car.ai_list[0].enabled

    # Kiểm tra có chơi multiplayer không
    # Thành tựu này đạt được khi có cập nhật multiplayer
    def play_multiplayer(self):
        return self.car.multiplayer_update

    # Kiểm tra có vào garage không
    # Thành tựu này đạt được khi menu garage được mở
    def garage(self):
        return self.main_menu.garage_menu.enabled

    # Kiểm tra có chơi chế độ time trial không
    # Thành tựu này đạt được khi gamemode là "time trial"
    def time_trial(self):
        return self.car.gamemode == "time trial"

    # Mở khóa chế độ drift khi đã unlock tất cả đường đua
    # Đây là thành tựu cuối cùng, yêu cầu hoàn thành tất cả
    def unlock_drift(self):
        if self.sand_track.unlocked and self.grass_track.unlocked and \
            self.snow_track.unlocked and self.forest_track.unlocked and \
                self.savannah_track.unlocked and self.lake_track.unlocked:
                self.car.drift_unlocked = True
                self.car.save_unlocked()
                return True

    # ==================== HÀM MỞ KHÓA ĐƯỜNG ĐUA ====================
    
    # Mở khóa Grass Track khi hoàn thành Sand Track dưới 22 giây
    def unlock_grass_track(self):
        for menu in self.main_menu.menus:
            if menu.enabled == False:
                if self.car.enabled and self.car.last_count != 0:
                    if self.sand_track.enabled and self.sand_track.unlocked:
                        if self.car.last_count <= 22:
                            # Unlock Grass Track
                            self.grass_track.unlocked = True
                            self.car.save_unlocked()
                            return True
    
    # Mở khóa Snow Track khi hoàn thành Grass Track dưới 23 giây
    def unlock_snow_track(self):
        for menu in self.main_menu.menus:
            if menu.enabled == False:
                if self.car.enabled and self.car.last_count != 0:
                    if self.grass_track.enabled and self.grass_track.unlocked:
                        if self.car.last_count <= 23:
                            # Unlock Snow Track
                            self.snow_track.unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa Forest Track khi hoàn thành Snow Track dưới 40 giây
    def unlock_forest_track(self):
        for menu in self.main_menu.menus:
            if menu.enabled == False:
                if self.car.enabled and self.car.last_count != 0:
                    if self.snow_track.enabled and self.snow_track.unlocked:
                        if self.car.last_count <= 40:
                            # Unlock Forest Track
                            self.forest_track.unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa Savannah Track khi hoàn thành Forest Track dưới 32 giây
    def unlock_savannah_track(self):
        for menu in self.main_menu.menus:
            if menu.enabled == False:
                if self.car.enabled and self.car.last_count != 0:
                    if self.forest_track.enabled and self.forest_track.unlocked:
                        if self.car.last_count <= 32:
                            # Unlock Savannah Track
                            self.savannah_track.unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa Lake Track khi hoàn thành Savannah Track dưới 20 giây
    def unlock_lake_track(self):
        for menu in self.main_menu.menus:
            if menu.enabled == False:
                if self.car.enabled and self.car.last_count != 0:
                    if self.savannah_track.enabled and self.savannah_track.unlocked:
                        if self.car.last_count <= 20:
                            # Unlock Lake Track
                            self.lake_track.unlocked = True
                            self.car.save_unlocked()
                            return True

"""
Sand Track Achievements
"""
class SandTrackAchievements():
    def __init__(self, car, main_menu, sand_track):
        self.car = car
        self.main_menu = main_menu
        self.sand_track = sand_track

    # Kiểm tra đã chơi Sand Track chưa
    def play_sand_track(self):
        return self.sand_track.played

    # Đạt dưới 20 giây trên Sand Track
    def twenty_seconds_sand_track(self):
        if self.sand_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.last_count != 0:
                        return self.car.last_count <= 20

    # Đạt dưới 17 giây trên Sand Track
    def seventeen_seconds_sand_track(self):
        if self.sand_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.last_count != 0:
                        return self.car.last_count <= 17

    # Đạt dưới 15 giây trên Sand Track
    # Bonus: Mở khóa Viking Helmet
    def fifteen_seconds_sand_track(self):
        if self.sand_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.last_count != 0:
                        if self.car.last_count <= 15:
                            # Unlock Viking Helmet
                            self.car.viking_helmet_unlocked = True
                            self.car.save_unlocked()
                        return self.car.last_count <= 15

"""
Grass Track Achievements
"""
class GrassTrackAchievements():
    def __init__(self, car, main_menu, grass_track):
        self.car = car
        self.main_menu = main_menu
        self.grass_track = grass_track

    # Kiểm tra đã chơi Grass Track chưa
    def play_grass_track(self):
        return self.grass_track.played

    # Đạt dưới 22 giây trên Grass Track
    def twentytwo_seconds_grass_track(self):
        if self.grass_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.last_count != 0:
                        return self.car.last_count <= 22

    # Đạt dưới 20 giây trên Grass Track
    def twenty_seconds_grass_track(self):
        if self.grass_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.last_count != 0:
                        return self.car.last_count <= 20

    # Đạt dưới 18 giây trên Grass Track
    def eighteen_seconds_grass_track(self):
        if self.grass_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.last_count != 0:
                        return self.car.last_count <= 18

"""
Snow Track Achievements
"""
class SnowTrackAchievements():
    def __init__(self, car, main_menu, snow_track):
        self.car = car
        self.main_menu = main_menu
        self.snow_track = snow_track

    # Kiểm tra đã chơi Snow Track chưa
    def play_snow_track(self):
        return self.snow_track.played

    # Đạt dưới 40 giây trên Snow Track
    def fourty_seconds_snow_track(self):
        if self.snow_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 40

    # Đạt dưới 36 giây trên Snow Track
    def thirtysix_seconds_snow_track(self):
        if self.snow_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 35

    # Đạt dưới 33 giây trên Snow Track
    def thirtythree_seconds_snow_track(self):
        if self.snow_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 32

"""
Forest Track Achievements
"""
class ForestTrackAchievements():
    def __init__(self, car, main_menu, forest_track):
        self.car = car
        self.main_menu = main_menu
        self.forest_track = forest_track

    # Kiểm tra đã chơi Forest Track chưa
    def play_forest_track(self):
        return self.forest_track.played

    # Đạt dưới 30 giây trên Forest Track
    def thirty_seconds_forest_track(self):
        if self.forest_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 30

    # Đạt dưới 28 giây trên Forest Track
    def twentyeight_seconds_forest_track(self):
        if self.forest_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 28

    # Đạt dưới 26 giây trên Forest Track
    def twentysix_seconds_forest_track(self):
        if self.forest_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 26

    # Đạt dưới 25 giây trên Forest Track
    # Bonus: Mở khóa Duck (vịt)
    def twentyfive_seconds_forest_track(self):
        if self.forest_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            if self.car.last_count <= 25:
                                # Unlock Duck
                                self.car.duck_unlocked = True
                                self.car.save_unlocked()
                            return self.car.last_count <= 25

"""
Savannah Track Achievements
"""
class SavannahTrackAchievements():
    def __init__(self, car, main_menu, savannah_track):
        self.car = car
        self.main_menu = main_menu
        self.savannah_track = savannah_track

    # Kiểm tra đã chơi Savannah Track chưa
    def play_savannah_track(self):
        return self.savannah_track.played

    # Đạt dưới 20 giây trên Savannah Track
    def twenty_seconds_savannah_track(self):
        if self.savannah_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 20

    # Đạt dưới 18 giây trên Savannah Track
    def eighteen_seconds_savannah_track(self):
        if self.savannah_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 18

    # Đạt dưới 16 giây trên Savannah Track
    def sixteen_seconds_savannah_track(self):
        if self.savannah_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 17

"""
Lake Track Achievements
"""
class LakeTrackAchievements():
    def __init__(self, car, main_menu, lake_track):
        self.car = car
        self.main_menu = main_menu
        self.lake_track = lake_track

    # Kiểm tra đã chơi Lake Track chưa
    def play_lake_track(self):
        return self.lake_track.played
    
    # Đạt dưới 60 giây trên Lake Track
    def sixty_seconds_lake_track(self):
        if self.lake_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 60

    # Đạt dưới 55 giây trên Lake Track
    def fiftyfive_seconds_lake_track(self):
        if self.lake_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 55

    # Đạt dưới 50 giây trên Lake Track
    def fifty_seconds_lake_track(self):
        if self.lake_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 50

    # Đạt dưới 47 giây trên Lake Track
    def fourtyseven_seconds_lake_track(self):
        if self.lake_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if menu.enabled == False:
                        if self.car.last_count != 0:
                            return self.car.last_count <= 47

"""
Car Achievements
"""
class CarAchievements():
    def __init__(self, car, main_menu, sand_track, grass_track, snow_track, forest_track, savannah_track, lake_track):
        self.car = car
        self.main_menu = main_menu
        self.sand_track = sand_track
        self.grass_track = grass_track
        self.snow_track = snow_track
        self.forest_track = forest_track
        self.savannah_track = savannah_track
        self.lake_track = lake_track

    # ==================== MỞ KHÓA XE MỚI ====================
    
    # Mở khóa Muscle Car khi hoàn thành Savannah Track dưới 18 giây
    def unlock_muscle_car(self):
        if self.savannah_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if not menu.enabled:
                        if self.car.last_count != 0:
                            if self.car.last_count <= 18:
                                self.car.muscle_unlocked = True
                                self.car.save_unlocked()
                                return True

    # Mở khóa Limo khi hoàn thành Grass Track dưới 20 giây
    def unlock_limo(self):
        if self.grass_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if not menu.enabled:
                        if self.car.last_count != 0:
                            if self.car.last_count <= 20:
                                self.car.limo_unlocked = True
                                self.car.save_unlocked()
                                return True

    # Mở khóa Lorry khi hoàn thành Forest Track dưới 28 giây
    def unlock_lorry(self):
        if self.forest_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if not menu.enabled:
                        if self.car.last_count != 0:
                            if self.car.last_count <= 28:
                                self.car.lorry_unlocked = True
                                self.car.save_unlocked()
                                return True

    # Mở khóa Hatchback khi hoàn thành Sand Track dưới 20 giây
    def unlock_hatchback(self):
        if self.sand_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if not menu.enabled:
                        if self.car.last_count != 0:
                            if self.car.last_count <= 20:
                                self.car.hatchback_unlocked = True
                                self.car.save_unlocked()
                                return True

    # Mở khóa Rally Car khi hoàn thành Lake Track dưới 60 giây
    def unlock_rally(self):
        if self.lake_track.enabled:
            if self.car.enabled:
                for menu in self.main_menu.menus:
                    if not menu.enabled:
                        if self.car.last_count != 0:
                            if self.car.last_count <= 60:
                                self.car.rally_unlocked = True
                                self.car.save_unlocked()
                                return True

    # ==================== MỞ KHÓA MÀU SẮC CHO SPORTS CAR ====================
    
    # Mở khóa màu xanh cho Sports Car khi hoàn thành Grass Track dưới 22 giây
    def sports_green(self):
        if self.grass_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "sports":
                        if self.car.last_count <= 22 and self.car.last_count != 0:
                            # Unlock Sports Car Green Colour
                            self.car.sports_green_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu cam cho Sports Car khi hoàn thành Savannah Track dưới 18 giây
    def sports_orange(self):
        if self.savannah_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "sports":
                        if self.car.last_count <= 18 and self.car.last_count != 0:
                            # Unlock Sports Car Orange Colour
                            self.car.sports_orange_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu trắng cho Sports Car khi hoàn thành Snow Track dưới 37 giây
    def sports_white(self):
        if self.snow_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "sports":
                        if self.car.last_count <= 37 and self.car.last_count != 0:
                            # Unlock Sports Car White Colour
                            self.car.sports_white_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu đen cho Sports Car khi hoàn thành Forest Track dưới 29 giây
    def sports_black(self):
        if self.forest_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "sports":
                        if self.car.last_count <= 29 and self.car.last_count != 0:
                            # Unlock Sports Car Black Colour
                            self.car.sports_black_unlocked = True
                            self.car.save_unlocked()
                            return True

    """
    Muscle Car Textures
    """
    # Mở khóa màu đỏ cho Muscle Car khi hoàn thành Savannah Track dưới 17 giây
    def muscle_red(self):
        if self.savannah_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "muscle":
                        if self.car.last_count <= 17 and self.car.last_count != 0:
                            # Unlock Muscle Car Red Colour
                            self.car.muscle_red_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu xanh cho Muscle Car khi hoàn thành Lake Track dưới 52 giây
    def muscle_blue(self):
        if self.lake_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "muscle":
                        if self.car.last_count <= 52 and self.car.last_count != 0:
                            # Unlock Muscle Car Blue Colour
                            self.car.muscle_blue_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu xanh lá cho Muscle Car khi hoàn thành Grass Track dưới 20 giây
    def muscle_green(self):
        if self.grass_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "muscle":
                        if self.car.last_count <= 20 and self.car.last_count != 0:
                            # Unlock Muscle Car Green Colour
                            self.car.muscle_green_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu trắng cho Muscle Car khi hoàn thành Snow Track dưới 38 giây
    def muscle_white(self):
        if self.snow_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "muscle":
                        if self.car.last_count <= 38 and self.car.last_count != 0:
                            # Unlock Muscle Car White Colour
                            self.car.muscle_white_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu đen cho Muscle Car khi hoàn thành Forest Track dưới 28 giây
    def muscle_black(self):
        if self.forest_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "muscle":
                        if self.car.last_count <= 28 and self.car.last_count != 0:
                            # Unlock Muscle Car Black Colour
                            self.car.muscle_black_unlocked = True
                            self.car.save_unlocked()
                            return True

    """
    Limo Textures
    """
    # Mở khóa màu đỏ cho Limo khi hoàn thành Sand Track dưới 19 giây
    def limo_red(self):
        if self.sand_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "limo":
                        if self.car.last_count <= 19 and self.car.last_count != 0:
                            # Unlock Limo Red Colour
                            self.car.limo_red_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu xanh cho Limo khi hoàn thành Lake Track dưới 60 giây
    def limo_blue(self):
        if self.lake_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "limo":
                        if self.car.last_count <= 60 and self.car.last_count != 0:
                            # Unlock Limo Blue Colour
                            self.car.limo_blue_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu xanh lá cho Limo khi hoàn thành Forest Track dưới 28 giây
    def limo_green(self):
        if self.forest_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "limo":
                        if self.car.last_count <= 28 and self.car.last_count != 0:
                            # Unlock Limo Green Colour
                            self.car.limo_green_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu trắng cho Limo khi hoàn thành Snow Track dưới 38 giây
    def limo_white(self):
        if self.snow_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "limo":
                        if self.car.last_count <= 38 and self.car.last_count != 0:
                            # Unlock Limo White Colour
                            self.car.limo_white_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu cam cho Limo khi hoàn thành Savannah Track dưới 18 giây
    def limo_orange(self):
        if self.savannah_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "limo":
                        if self.car.last_count <= 18 and self.car.last_count != 0:
                            # Unlock Limo Orange Colour
                            self.car.limo_orange_unlocked = True
                            self.car.save_unlocked()
                            return True

    """
    Lorry Textures
    """
    # Mở khóa màu đỏ cho Lorry khi hoàn thành Sand Track dưới 20 giây
    def lorry_red(self):
        if self.sand_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "lorry":
                        if self.car.last_count <= 20 and self.car.last_count != 0:
                            # Unlock Lorry Red Colour
                            self.car.lorry_red_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu xanh cho Lorry khi hoàn thành Lake Track dưới 70 giây
    def lorry_blue(self):
        if self.lake_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "lorry":
                        if self.car.last_count <= 70 and self.car.last_count != 0:
                            # Unlock Lorry Blue Colour
                            self.car.lorry_blue_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu xanh lá cho Lorry khi hoàn thành Grass Track dưới 21 giây
    def lorry_green(self):
        if self.grass_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "lorry":
                        if self.car.last_count <= 21 and self.car.last_count != 0:
                            # Unlock Lorry Green Colour
                            self.car.lorry_green_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu đen cho Lorry khi hoàn thành Snow Track dưới 38 giây
    def lorry_black(self):
        if self.snow_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "lorry":
                        if self.car.last_count <= 38 and self.car.last_count != 0:
                            # Unlock Lorry Black Colour
                            self.car.lorry_black_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu cam cho Lorry khi hoàn thành Savannah Track dưới 19 giây
    def lorry_orange(self):
        if self.savannah_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "lorry":
                        if self.car.last_count <= 19 and self.car.last_count != 0:
                            # Unlock Lorry Orange Colour
                            self.car.lorry_orange_unlocked = True
                            self.car.save_unlocked()
                            return True

    """
    Hatchback Textures
    """
    # Mở khóa màu đỏ cho Hatchback khi hoàn thành Sand Track dưới 18 giây
    def hatchback_red(self):
        if self.sand_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "hatchback":
                        if self.car.last_count <= 18 and self.car.last_count != 0:
                            # Unlock Hatchback Red Colour
                            self.car.hatchback_red_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu xanh cho Hatchback khi hoàn thành Lake Track dưới 65 giây
    def hatchback_blue(self):
        if self.lake_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "hatchback":
                        if self.car.last_count <= 65 and self.car.last_count != 0:
                            # Unlock Hatchback Blue Colour
                            self.car.hatchback_blue_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu trắng cho Hatchback khi hoàn thành Grass Track dưới 20 giây
    def hatchback_white(self):
        if self.grass_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "hatchback":
                        if self.car.last_count <= 20 and self.car.last_count != 0:
                            # Unlock Hatchback White Colour
                            self.car.hatchback_white_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu đen cho Hatchback khi hoàn thành Snow Track dưới 37 giây
    def hatchback_black(self):
        if self.snow_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "hatchback":
                        if self.car.last_count <= 37 and self.car.last_count != 0:
                            # Unlock Hatchback Black Colour
                            self.car.hatchback_black_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu cam cho Hatchback khi hoàn thành Savannah Track dưới 18 giây
    def hatchback_orange(self):
        if self.savannah_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "hatchback":
                        if self.car.last_count <= 18 and self.car.last_count != 0:
                            # Unlock Hatchback Orange Colour
                            self.car.hatchback_orange_unlocked = True
                            self.car.save_unlocked()
                            return True

    """
    Rally Car Textures
    """
    # Mở khóa màu trắng cho Rally Car khi hoàn thành Sand Track dưới 17 giây
    def rally_white(self):
        if self.sand_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "rally":
                        if self.car.last_count <= 17 and self.car.last_count != 0:
                            # Unlock Rally Car White Colour
                            self.car.rally_white_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu xanh cho Rally Car khi hoàn thành Lake Track dưới 52 giây
    def rally_blue(self):
        if self.lake_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "rally":
                        if self.car.last_count <= 52 and self.car.last_count != 0:
                            # Unlock Rally Car Blue Colour
                            self.car.rally_blue_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu xanh lá cho Rally Car khi hoàn thành Grass Track dưới 19 giây
    def rally_green(self):
        if self.grass_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "rally":
                        if self.car.last_count <= 19 and self.car.last_count != 0:
                            # Unlock Rally Car Green Colour
                            self.car.rally_green_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu đen cho Rally Car khi hoàn thành Snow Track dưới 35 giây
    def rally_black(self):
        if self.snow_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "rally":
                        if self.car.last_count <= 35 and self.car.last_count != 0:
                            # Unlock Rally Car Black Colour
                            self.car.rally_black_unlocked = True
                            self.car.save_unlocked()
                            return True

    # Mở khóa màu cam cho Rally Car khi hoàn thành Savannah Track dưới 16 giây
    def rally_orange(self):
        if self.savannah_track.enabled:
            for menu in self.main_menu.menus:
                if menu.enabled == False:
                    if self.car.car_type == "rally":
                        if self.car.last_count <= 16 and self.car.last_count != 0:
                            # Unlock Rally Car Orange Colour
                            self.car.rally_orange_unlocked = True
                            self.car.save_unlocked()
                            return True
