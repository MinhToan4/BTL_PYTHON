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
                             QMessageBox, QTabWidget, QTextEdit, QSlider, QCheckBox,
                             QScrollArea, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# Import AI config
from ai_config import get_ai_model, get_fallback_response, SYSTEM_PROMPT

class ChatThread(QThread):
    """Thread để xử lý chat với AI không block UI"""
    response_ready = pyqtSignal(str)
    
    def __init__(self, message, chat_history):
        super().__init__()
        self.message = message
        self.chat_history = chat_history
    
    def run(self):
        """Thử gọi AI với auto-switch: Flash → Pro → Fallback"""
        model_index = 0  # Bắt đầu với Flash
        
        while model_index < 2:  # Thử tối đa 2 models
            try:
                # Lấy model theo index (0=Flash, 1=Pro)
                model = get_ai_model(model_index)
                
                # Tạo full prompt
                full_prompt = f"{SYSTEM_PROMPT}\n\nCâu hỏi: {self.message}\n\nTrả lời:"
                
                # Gửi request tới Gemini
                response = model.generate_content(full_prompt)
                ai_response = response.text
                
                print(f"✅ AI trả lời thành công!")
                self.response_ready.emit(ai_response)
                return  # Thành công, thoát
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Kiểm tra lỗi giới hạn quota/rate limit
                if any(keyword in error_msg for keyword in ['quota', 'limit', 'rate', '429', 'resource_exhausted']):
                    print(f"⚠️ Model bị giới hạn, chuyển sang model dự phòng...")
                    model_index += 1  # Chuyển sang model tiếp theo
                    continue
                else:
                    # Lỗi khác, không retry
                    print(f"⚠️ Gemini API lỗi: {str(e)[:100]}")
                    break
        
        # Nếu tất cả models đều lỗi, dùng fallback
        print("⚠️ Sử dụng fallback response")
        response = get_fallback_response(self.message)
        self.response_ready.emit(response)

class GameLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 Kho Game GestureAI - Điều Khiển Bằng Cử Chỉ Tay")
        self.setGeometry(100, 100, 1012, 650)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0f0c29, stop: 0.5 #302b63, stop: 1 #24243e);
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #667eea, stop: 1 #764ba2);
                border: none;
                color: white;
                padding: 11px 22px;
                font-size: 11px;
                font-weight: bold;
                border-radius: 9px;
                margin: 6px;
                min-height: 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #f093fb, stop: 1 #f5576c);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #4facfe, stop: 1 #00f2fe);
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 rgba(255, 255, 255, 0.15),
                                          stop: 1 rgba(255, 255, 255, 0.08));
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 14px;
                margin: 11px;
                padding: 11px;
            }
            QFrame:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 rgba(255, 255, 255, 0.2),
                                          stop: 1 rgba(255, 255, 255, 0.12));
                border: 2px solid rgba(255, 255, 255, 0.35);
            }
        """)

        # Chat history
        self.chat_history = []

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout chính
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(14, 14, 14, 14)

        # Header với gradient text effect
        header_layout = QVBoxLayout()
        header_layout.setSpacing(3)

        title_label = QLabel("🎮 KHO GAME GESTURE AI 🎮")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 23, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                  stop: 0 #667eea, stop: 0.5 #f093fb, stop: 1 #f5576c);
            margin: 11px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        """)
        header_layout.addWidget(title_label)

        subtitle_label = QLabel("✨ Điều khiển game bằng cử chỉ tay - Không cần chuột, không cần bàn phím! ✨")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 9))
        subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 8px;
            font-style: italic;
        """)
        header_layout.addWidget(subtitle_label)

        main_layout.addLayout(header_layout)

        # Tab Widget với style hiện đại
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid rgba(255, 255, 255, 0.2);
                background: rgba(0, 0, 0, 0.2);
                border-radius: 11px;
                padding: 3px;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                padding: 9px 18px;
                margin: 3px;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
                min-width: 87px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #667eea, stop: 1 #764ba2);
            }
            QTabBar::tab:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        """)

        # Tab 1: Games
        games_tab = QWidget()
        self.setup_games_tab(games_tab)
        tab_widget.addTab(games_tab, "🎯 Kho Game")

        # Tab 2: AI Chatbot
        chatbot_tab = QWidget()
        self.setup_chatbot_tab(chatbot_tab)
        tab_widget.addTab(chatbot_tab, "🤖 AI Trợ Lý")

        # Tab 3: Cài đặt
        settings_tab = QWidget()
        self.setup_settings_tab(settings_tab)
        tab_widget.addTab(settings_tab, "⚙️ Cài Đặt")

        # Tab 4: Hướng dẫn
        guide_tab = QWidget()
        self.setup_guide_tab(guide_tab)
        tab_widget.addTab(guide_tab, "📖 Hướng Dẫn")

        main_layout.addWidget(tab_widget)

        # Footer với animation effect
        footer_label = QLabel("💫 MediaPipe Hand Tracking Games | Powered by Gemini AI 💫")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            margin: 9px;
            font-size: 10px;
        """)
        main_layout.addWidget(footer_label)

    def setup_games_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title cho game section
        section_title = QLabel("🎮 DANH SÁCH TRÒ CHƠI")
        section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        section_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        section_title.setStyleSheet("""
            color: white;
            margin-bottom: 15px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        """)
        layout.addWidget(section_title)

        # Grid layout cho 3 game với kích thước đồng nhất
        games_grid = QGridLayout()
        games_grid.setSpacing(20)
        games_grid.setContentsMargins(5, 5, 5, 5)

        # === Game 1: Flappy Bird ===
        flappy_frame = QFrame()
        flappy_frame.setMinimumHeight(360)
        flappy_frame.setMaximumHeight(360)
        flappy_layout = QVBoxLayout(flappy_frame)
        flappy_layout.setSpacing(12)

        flappy_title = QLabel("🐦 FLAPPY BIRD")
        flappy_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flappy_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        flappy_title.setStyleSheet("color: #FFD700; margin: 8px;")

        flappy_desc = QLabel("Điều khiển chú chim bay qua các ống bằng cử chỉ tay. Thử thách phản xạ và độ chính xác!")
        flappy_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flappy_desc.setWordWrap(True)
        flappy_desc.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            margin: 18px 10px;
            font-size: 13px;
            line-height: 1.8;
            padding: 12px;
        """)

        flappy_btn = QPushButton("🎮 CHƠI NGAY")
        flappy_btn.setMinimumHeight(37)
        flappy_btn.clicked.connect(lambda: self.launch_flappy_bird())

        flappy_layout.addWidget(flappy_title)
        flappy_layout.addWidget(flappy_desc)
        flappy_layout.addStretch()
        flappy_layout.addWidget(flappy_btn)

        # === Game 2: Ninja Fruit (Chém Hoa Quả) ===
        fruit_frame = QFrame()
        fruit_frame.setMinimumHeight(360)
        fruit_frame.setMaximumHeight(360)
        fruit_layout = QVBoxLayout(fruit_frame)
        fruit_layout.setSpacing(12)

        fruit_title = QLabel("🍎 NINJA FRUIT")
        fruit_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fruit_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        fruit_title.setStyleSheet("color: #FF6347; margin: 8px;")

        fruit_desc = QLabel("Chém hoa quả bay lên bằng cách vung tay. Tránh chạm vào bom và ghi điểm cao nhất!")
        fruit_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fruit_desc.setWordWrap(True)
        fruit_desc.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            margin: 18px 10px;
            font-size: 13px;
            line-height: 1.8;
            padding: 12px;
        """)

        fruit_btn = QPushButton("🎮 CHƠI NGAY")
        fruit_btn.setMinimumHeight(37)
        fruit_btn.clicked.connect(self.launch_fruit_ninja)

        fruit_layout.addWidget(fruit_title)
        fruit_layout.addWidget(fruit_desc)
        fruit_layout.addStretch()
        fruit_layout.addWidget(fruit_btn)

        # === Game 3: Race Master 3D ===
        race_frame = QFrame()
        race_frame.setMinimumHeight(360)
        race_frame.setMaximumHeight(360)
        race_layout = QVBoxLayout(race_frame)
        race_layout.setSpacing(12)

        race_title = QLabel("🏎️ RACE MASTER 3D")
        race_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        race_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        race_title.setStyleSheet("color: #FF4500; margin: 8px;")

        race_desc = QLabel("Đua xe 3D với cử chỉ tay! Rẽ trái/phải, vượt đối thủ và chinh phục đường đua.")
        race_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        race_desc.setWordWrap(True)
        race_desc.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            margin: 18px 10px;
            font-size: 13px;
            line-height: 1.8;
            padding: 12px;
        """)

        race_btn = QPushButton("🎮 CHƠI NGAY")
        race_btn.setMinimumHeight(37)
        race_btn.clicked.connect(self.launch_race_master)

        race_layout.addWidget(race_title)
        race_layout.addWidget(race_desc)
        race_layout.addStretch()
        race_layout.addWidget(race_btn)

        # Thêm các game vào grid (1 hàng, 3 cột)
        games_grid.addWidget(flappy_frame, 0, 0)
        games_grid.addWidget(fruit_frame, 0, 1)
        games_grid.addWidget(race_frame, 0, 2)

        # Set column stretch để các cột có kích thước đồng đều
        games_grid.setColumnStretch(0, 1)
        games_grid.setColumnStretch(1, 1)
        games_grid.setColumnStretch(2, 1)

        layout.addLayout(games_grid)
        layout.addStretch()

    def setup_chatbot_tab(self, tab):
        """Thiết lập tab chatbot AI"""
        layout = QVBoxLayout(tab)

        # Header
        header_label = QLabel("🤖 AI Trợ Lý Game")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("color: #3498db; margin: 10px;")
        layout.addWidget(header_label)

        info_label = QLabel("Hỏi AI về game nào phù hợp với bạn, cách chơi, mẹo hay, hoặc so sánh game!")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #ecf0f1; margin: 5px;")
        layout.addWidget(info_label)

        # Chat display area
        chat_scroll = QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_scroll.setStyleSheet("""
            QScrollArea {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid #34495e;
                border-radius: 10px;
            }
        """)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                padding: 15px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        self.chat_display.setPlainText("👋 Xin chào! Tôi là AI trợ lý game. Hãy hỏi tôi về các game nhé!\n\n💡 Gợi ý câu hỏi:\n• Game nào dễ chơi nhất?\n• Tôi thích đua xe, nên chơi game nào?\n• So sánh Flappy Bird và Chém Hoa Quả\n• Làm sao chơi Race Master 3D tốt hơn?\n• Cử chỉ tay để điều khiển game như thế nào?\n")

        chat_scroll.setWidget(self.chat_display)
        layout.addWidget(chat_scroll)

        # Input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Nhập câu hỏi của bạn...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 2px solid #34495e;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.chat_input.returnPressed.connect(self.send_message)

        send_btn = QPushButton("📤 Gửi")
        send_btn.clicked.connect(self.send_message)
        send_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                padding: 12px 25px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #2ecc71;
            }
        """)

        clear_btn = QPushButton("🗑️ Xóa")
        clear_btn.clicked.connect(self.clear_chat)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                padding: 12px 25px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)
        input_layout.addWidget(clear_btn)

        layout.addLayout(input_layout)

        # Quick questions
        quick_layout = QHBoxLayout()
        quick_label = QLabel("⚡ Câu hỏi nhanh:")
        quick_label.setStyleSheet("color: #ecf0f1; font-weight: bold;")
        quick_layout.addWidget(quick_label)

        quick_questions = [
            "Game nào dễ nhất?",
            "Game đua xe là gì?",
            "So sánh 3 game"
        ]

        for question in quick_questions:
            btn = QPushButton(question)
            btn.clicked.connect(lambda checked, q=question: self.quick_ask(q))
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(52, 152, 219, 0.3);
                    padding: 8px 15px;
                    font-size: 12px;
                    border: 1px solid #3498db;
                }
                QPushButton:hover {
                    background: rgba(52, 152, 219, 0.6);
                }
            """)
            quick_layout.addWidget(btn)

        quick_layout.addStretch()
        layout.addLayout(quick_layout)

    def launch_flappy_bird(self):
        """Khởi chạy game Flappy Bird"""
        try:
            # Kiểm tra file game có tồn tại không
            game_dir = "flappy-mediapipe"
            game_path = os.path.join(game_dir, "game_core.py")
            if not os.path.exists(game_path):
                QMessageBox.warning(self, "Lỗi",
                                  f"Không tìm thấy file game: {game_path}")
                return

            # Khởi chạy game với chế độ 2 tay mặc định và set working directory đúng
            os.environ["GAME_MODE"] = "two_hands"
            subprocess.Popen([sys.executable, "game_core.py"], cwd=game_dir)

            QMessageBox.information(self, "Thông báo",
                                  "Đã khởi chạy Flappy Bird!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi chạy game: {str(e)}")

    def launch_race_master(self):
        """Khởi chạy game Race Master 3D"""
        try:
            # Kiểm tra file game có tồn tại không
            game_path = "Race Master 3D/main.py"
            if not os.path.exists(game_path):
                QMessageBox.warning(self, "Lỗi",
                                  f"Không tìm thấy file game: {game_path}")
                return

            subprocess.Popen([sys.executable, game_path])
            QMessageBox.information(self, "Thông báo", "Đã khởi chạy Race Master 3D!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi chạy game: {str(e)}")

    def launch_fruit_ninja(self):
        """Khởi chạy game Fruit Ninja"""
        try:
            # Kiểm tra file game có tồn tại không
            game_path = "ninja-mediapipe/main.py"
            if not os.path.exists(game_path):
                QMessageBox.warning(self, "Lỗi",
                                  f"Không tìm thấy file game: {game_path}")
                return

            subprocess.Popen([sys.executable, game_path])
            QMessageBox.information(self, "Thông báo", "Đã khởi chạy game Chém Hoa Quả!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi chạy game: {str(e)}")

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
• Điều khiển chú chim bay qua các ống bằng cử chỉ tay
• Mục tiêu: Bay qua các ống mà không va chạm

🏎️ RACE MASTER 3D:
• Di chuyển tay trái/phải để xe rẽ trái/phải
• Cử chỉ tăng/giảm tốc độ bằng cách mở/đóng bàn tay
• Tránh va chạm với các xe khác và vượt qua chúng

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

    def send_message(self):
        """Gửi tin nhắn đến AI"""
        message = self.chat_input.text().strip()
        if not message:
            return

        # Hiển thị tin nhắn người dùng
        self.chat_display.append(f"\n👤 Bạn: {message}\n")
        self.chat_input.clear()

        # Thêm vào lịch sử chat
        self.chat_history.append({"role": "user", "content": message})

        # Hiển thị loading
        self.chat_display.append("🤖 AI: Đang suy nghĩ...")
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

        # Gọi AI trong thread riêng
        self.chat_thread = ChatThread(message, self.chat_history)
        self.chat_thread.response_ready.connect(self.display_response)
        self.chat_thread.start()

    def display_response(self, response):
        """Hiển thị phản hồi từ AI"""
        # Thêm vào lịch sử chat
        if not response.startswith("❌"):
            self.chat_history.append({"role": "assistant", "content": response})

        # Xóa dòng "Đang suy nghĩ..."
        text = self.chat_display.toPlainText()
        if "Đang suy nghĩ..." in text:
            text = text.replace("🤖 AI: Đang suy nghĩ...", f"🤖 AI: {response}")
            self.chat_display.setPlainText(text)
        else:
            self.chat_display.append(f"{response}")

        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def quick_ask(self, question):
        """Hỏi nhanh"""
        self.chat_input.setText(question)
        self.send_message()

    def clear_chat(self):
        """Xóa lịch sử chat"""
        self.chat_display.clear()
        self.chat_display.setPlainText("👋 Xin chào! Tôi là AI trợ lý game. Hãy hỏi tôi về các game nhé!\n")
        self.chat_history = []

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