#!/usr/bin/env python3
"""
Kho Game Điều Khiển Bằng Cử Chỉ Tay Với MediaPipe
Giao diện menu chính sử dụng PyQt6
"""

import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout,
                             QMessageBox, QTabWidget, QTextEdit, QSlider, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPalette, QIcon

class GameLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kho Game GestureAI - Điều Khiển Bằng Cử Chỉ Tay")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2c3e50, stop: 1 #34495e);
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                border: none;
                color: white;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #e74c3c, stop: 1 #c0392b);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #2ecc71);
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout chính
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("🎮 KHO GAME GESTURE AI 🎮")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #f39c12; margin: 20px;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Điều khiển game bằng cử chỉ tay!")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("color: #ecf0f1; margin-bottom: 20px;")
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(subtitle_label)
        
        # Tab Widget
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #34495e;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #34495e;
                color: white;
                padding: 10px 20px;
                margin: 2px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #3498db;
            }
        """)
        
        # Tab 1: Games
        games_tab = QWidget()
        self.setup_games_tab(games_tab)
        tab_widget.addTab(games_tab, "🎯 Games")
        
        # Tab 2: Cài đặt
        settings_tab = QWidget()
        self.setup_settings_tab(settings_tab)
        tab_widget.addTab(settings_tab, "⚙️ Cài đặt")
        
        # Tab 3: Hướng dẫn
        guide_tab = QWidget()
        self.setup_guide_tab(guide_tab)
        tab_widget.addTab(guide_tab, "📖 Hướng dẫn")
        
        main_layout.addWidget(tab_widget)
        
        # Footer
        footer_label = QLabel("MediaPipe Hand Tracking Games | Phát triển bởi Nhóm 3 thành viên")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #95a5a6; margin: 10px;")
        main_layout.addWidget(footer_label)
        
    def setup_games_tab(self, tab):
        layout = QGridLayout(tab)
        
        # Game 1: Flappy Bird
        flappy_frame = QFrame()
        flappy_layout = QVBoxLayout(flappy_frame)
        
        flappy_title = QLabel("🐦 FLAPPY BIRD")
        flappy_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flappy_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        flappy_title.setStyleSheet("color: #f1c40f; margin: 10px;")
        
        flappy_desc = QLabel("Điều khiển chú chim bay qua các ống bằng cách di chuyển tay lên xuống")
        flappy_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flappy_desc.setWordWrap(True)
        flappy_desc.setStyleSheet("color: #ecf0f1; margin: 10px;")
        
        flappy_btn_one = QPushButton("🖐️ Chơi với 1 tay")
        flappy_btn_one.clicked.connect(lambda: self.launch_flappy_bird("one_hand"))
        
        flappy_btn_two = QPushButton("✋ Chơi với 2 tay")
        flappy_btn_two.clicked.connect(lambda: self.launch_flappy_bird("two_hands"))
        
        flappy_layout.addWidget(flappy_title)
        flappy_layout.addWidget(flappy_desc)
        flappy_layout.addWidget(flappy_btn_one)
        flappy_layout.addWidget(flappy_btn_two)
        
        # Game 2: Ninja (Placeholder)
        ninja_frame = QFrame()
        ninja_layout = QVBoxLayout(ninja_frame)
        
        ninja_title = QLabel("🥷 NINJA GAME")
        ninja_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ninja_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        ninja_title.setStyleSheet("color: #e74c3c; margin: 10px;")
        
        ninja_desc = QLabel("Di chuyển ninja bằng cử chỉ tay, tấn công kẻ thù và vượt qua các thử thách")
        ninja_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ninja_desc.setWordWrap(True)
        ninja_desc.setStyleSheet("color: #ecf0f1; margin: 10px;")
        
        ninja_btn = QPushButton("🎮 Chơi")
        ninja_btn.setEnabled(True)
        ninja_btn.clicked.connect(self.launch_ninja_game)
        
        ninja_layout.addWidget(ninja_title)
        ninja_layout.addWidget(ninja_desc)
        ninja_layout.addWidget(ninja_btn)
        
        # Game 3: Fruit Ninja (Placeholder)
        fruit_frame = QFrame()
        fruit_layout = QVBoxLayout(fruit_frame)
        
        fruit_title = QLabel("🍎 CHÉM HOA QUẢ")
        fruit_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fruit_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        fruit_title.setStyleSheet("color: #27ae60; margin: 10px;")
        
        fruit_desc = QLabel("Chém hoa quả bay lên bằng cách vung tay, tránh chạm vào bom")
        fruit_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fruit_desc.setWordWrap(True)
        fruit_desc.setStyleSheet("color: #ecf0f1; margin: 10px;")
        
        fruit_btn = QPushButton("🎮 Chơi")
        fruit_btn.setEnabled(True)
        fruit_btn.clicked.connect(self.launch_fruit_ninja)
        
        fruit_layout.addWidget(fruit_title)
        fruit_layout.addWidget(fruit_desc)
        fruit_layout.addWidget(fruit_btn)
        
        # Thêm các frame vào grid
        layout.addWidget(flappy_frame, 0, 0)
        layout.addWidget(ninja_frame, 0, 1)
        layout.addWidget(fruit_frame, 1, 0, 1, 2)
        
    def setup_settings_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # Cài đặt Camera
        camera_frame = QFrame()
        camera_layout = QVBoxLayout(camera_frame)
        
        camera_title = QLabel("📹 Cài đặt Camera")
        camera_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        camera_title.setStyleSheet("color: #3498db; margin: 10px;")
        
        self.camera_checkbox = QCheckBox("Bật camera để điều khiển")
        self.camera_checkbox.setChecked(True)
        self.camera_checkbox.setStyleSheet("color: white; margin: 5px;")
        
        sensitivity_label = QLabel("Độ nhạy cử chỉ:")
        sensitivity_label.setStyleSheet("color: white; margin: 5px;")
        
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(5)
        self.sensitivity_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #34495e;
                height: 10px;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                width: 20px;
                border-radius: 10px;
            }
        """)
        
        camera_layout.addWidget(camera_title)
        camera_layout.addWidget(self.camera_checkbox)
        camera_layout.addWidget(sensitivity_label)
        camera_layout.addWidget(self.sensitivity_slider)
        
        # Cài đặt Âm thanh
        audio_frame = QFrame()
        audio_layout = QVBoxLayout(audio_frame)
        
        audio_title = QLabel("🔊 Cài đặt Âm thanh")
        audio_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        audio_title.setStyleSheet("color: #e74c3c; margin: 10px;")
        
        self.audio_checkbox = QCheckBox("Bật âm thanh game")
        self.audio_checkbox.setChecked(True)
        self.audio_checkbox.setStyleSheet("color: white; margin: 5px;")
        
        volume_label = QLabel("Âm lượng:")
        volume_label.setStyleSheet("color: white; margin: 5px;")
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #34495e;
                height: 10px;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #e74c3c;
                width: 20px;
                border-radius: 10px;
            }
        """)
        
        audio_layout.addWidget(audio_title)
        audio_layout.addWidget(self.audio_checkbox)
        audio_layout.addWidget(volume_label)
        audio_layout.addWidget(self.volume_slider)
        
        # Nút lưu cài đặt
        save_btn = QPushButton("💾 Lưu cài đặt")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                padding: 15px;
                font-size: 16px;
                margin: 20px;
            }
            QPushButton:hover {
                background: #2ecc71;
            }
        """)
        
        layout.addWidget(camera_frame)
        layout.addWidget(audio_frame)
        layout.addWidget(save_btn)
        layout.addStretch()
        
    def setup_guide_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        guide_text = QTextEdit()
        guide_text.setReadOnly(True)
        guide_text.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        
        guide_content = """
📖 HƯỚNG DẪN SỬ DỤNG KHO GAME MEDIAPIPE

🎯 TỔNG QUAN:
Kho game này sử dụng công nghệ MediaPipe để nhận diện cử chỉ tay và điều khiển game mà không cần chuột hay bàn phím.

🐦 FLAPPY BIRD:
• Chế độ 1 tay: Di chuyển tay lên/xuống để điều khiển chim bay
• Chế độ 2 tay: Tay trái điều khiển bay lên, tay phải điều khiển bay xuống
• Mục tiêu: Bay qua các ống mà không va chạm

🥷 NINJA GAME:
• Di chuyển tay trái/phải để ninja di chuyển
• Cử chỉ đóng/mở bàn tay để nhảy
• Vung tay để tấn công kẻ thù

🍎 CHÉM HOA QUẢ:
• Theo dõi ngón trỏ để tạo đường cắt
• Chém hoa quả bay lên bằng cách vung tay
• Tránh chạm vào bom

⚙️ CÀI ĐẶT:
• Điều chỉnh độ nhạy cử chỉ trong tab Cài đặt
• Bật/tắt âm thanh theo ý muốn
• Đảm bảo camera hoạt động tốt và có đủ ánh sáng

💡 TIPS:
• Đứng cách camera 1-2 mét để nhận diện tốt nhất
• Đảm bảo ánh sáng đủ sáng
• Mặc áo có màu tương phản với nền để nhận diện tay tốt hơn
• Giữ tay trong khung hình camera

🔧 YÊU CẦU HỆ THỐNG:
• Python 3.8+
• Webcam
• Các thư viện: PyQt6, MediaPipe, OpenCV, Pygame

❗ LƯU Ý:
• Đây là dự án nghiên cứu và phát triển
• Một số game vẫn đang trong quá trình hoàn thiện
• Báo cáo lỗi và góp ý tại GitHub repository

🎮 CHÚC BẠN CHƠI GAME VUI VẺ!
        """
        
        guide_text.setPlainText(guide_content)
        layout.addWidget(guide_text)
        
    def launch_flappy_bird(self, mode):
        """Khởi chạy game Flappy Bird"""
        try:
            # Kiểm tra file game có tồn tại không
            game_path = "flappy-mediapipe/game_core.py"
            if not os.path.exists(game_path):
                QMessageBox.warning(self, "Lỗi", 
                                  f"Không tìm thấy file game: {game_path}")
                return
                
            # Khởi chạy game với mode được chọn
            if mode == "one_hand":
                os.environ["GAME_MODE"] = "one_hand"
            else:
                os.environ["GAME_MODE"] = "two_hands"
                
            subprocess.Popen([sys.executable, game_path])
            
            QMessageBox.information(self, "Thông báo", 
                                  f"Đã khởi chạy Flappy Bird ở chế độ {mode}!")
                                  
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi chạy game: {str(e)}")
            
    def launch_ninja_game(self):
        """Khởi chạy game Ninja"""
        try:
            # Kiểm tra file game có tồn tại không
            game_path = "ninja-mediapipe/main.py"
            if not os.path.exists(game_path):
                QMessageBox.warning(self, "Lỗi", 
                                  f"Không tìm thấy file game: {game_path}")
                return
                
            subprocess.Popen([sys.executable, game_path])
            QMessageBox.information(self, "Thông báo", "Đã khởi chạy game Ninja!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi chạy game: {str(e)}")
            
    def launch_fruit_ninja(self):
        """Khởi chạy game Fruit Ninja"""
        try:
            # Kiểm tra file game có tồn tại không
            game_path = "fruit-ninja-mediapipe/main.py"
            if not os.path.exists(game_path):
                QMessageBox.warning(self, "Lỗi", 
                                  f"Không tìm thấy file game: {game_path}")
                return
                
            subprocess.Popen([sys.executable, game_path])
            QMessageBox.information(self, "Thông báo", "Đã khởi chạy game Chém Hoa Quả!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi chạy game: {str(e)}")
            
    def save_settings(self):
        """Lưu cài đặt"""
        settings = {
            "camera_enabled": self.camera_checkbox.isChecked(),
            "sensitivity": self.sensitivity_slider.value(),
            "audio_enabled": self.audio_checkbox.isChecked(),
            "volume": self.volume_slider.value()
        }
        
        try:
            # Lưu cài đặt vào file hoặc registry
            # Ở đây chỉ hiển thị thông báo
            QMessageBox.information(self, "Thành công", 
                                  "Đã lưu cài đặt thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu cài đặt: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Kho Game MediaPipe")
    
    # Set application icon nếu có
    # app.setWindowIcon(QIcon("icon.png"))
    
    launcher = GameLauncher()
    launcher.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()