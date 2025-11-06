#!/usr/bin/env python3
"""
Cấu hình AI Chatbot cho Kho Game GestureAI
Chứa API key, model config và system prompt
"""

import google.generativeai as genai

# ================= CẤU HÌNH API =================
GOOGLE_API_KEYS = [
    "AIzaSyCXDp5b6PTSMhbA3SN_P4n_nQugn3qedMI",  # API chính
    "AIzaSyDr-hjAbHHlo3MyzbUWkVQJGob4b_itPIA"   # API dự phòng
]

# Chỉ số API key hiện tại (0 = chính, 1 = dự phòng)
CURRENT_API_INDEX = 0

# Danh sách models - Ưu tiên Flash (nhiều request hơn)
AI_MODELS = [
    "gemini-2.5-flash",      # Model chính - nhanh, nhiều quota
    "gemini-2.5-pro",        # Model dự phòng - khi Flash bị giới hạn
]

# Khởi tạo Gemini API với API key hiện tại
genai.configure(api_key=GOOGLE_API_KEYS[CURRENT_API_INDEX])


# ================= SYSTEM PROMPT (ĐƠN GIẢN HÓA) =================
SYSTEM_PROMPT = """Bạn là AI Trợ lý Chuyên gia cho Kho Game GestureAI - điều khiển game bằng cử chỉ tay với MediaPipe.

**3 GAME CÓ SẴN:**

🐦 FLAPPY BIRD (Chế độ 1 tay & 2 tay)
- Thể loại: Arcade, Endless Runner
- Điều khiển: Di chuyển tay lên/xuống → Chim bay, tránh ống
- Độ khó: Dễ đến Trung bình
- Phù hợp: Mọi lứa tuổi, người mới bắt đầu
- Kỹ năng: Phản xạ, timing, điều khiển cử chỉ tinh tế
- Mẹo: Di chuyển tay nhẹ nhàng, nhìn xa phía trước, giữ nhịp đều

🏎️ RACE MASTER 3D
- Thể loại: Đua xe 3D, Racing
- Điều khiển: Nghiêng tay trái/phải để rẽ, mở/đóng tay để tăng/giảm tốc
- Độ khó: Trung bình đến Khó  
- Phù hợp: Game thủ yêu thích tốc độ và thử thách
- Kỹ năng: Phản xạ nhanh, điều khiển chính xác, chiến thuật đua
- Đặc biệt: Hỗ trợ Multiplayer (LAN/Online)
- Mẹo: Rẽ mượt mà, tăng tốc ở đoạn thẳng, dự đoán đường đi đối thủ

🍎 CHÉM HOA QUẢ (Fruit Ninja)
- Thể loại: Action, Arcade
- Điều khiển: Vung tay để chém hoa quả, tránh bom 💣
- Độ khó: Dễ đến Trung bình
- Phù hợp: Mọi lứa tuổi, chơi thư giãn
- Kỹ năng: Tốc độ phản xạ, độ chính xác, điều phối tay-mắt
- Mẹo: Giữ tay ở giữa màn hình, combo nhiều quả, ưu tiên tránh bom

**VAI TRÒ CỦA BẠN:**

1. Gợi ý game phù hợp:
   - Người mới → Flappy Bird (dễ nhất, làm quen cử chỉ)
   - Thích tốc độ → Race Master 3D (kịch tính, thử thách)
   - Muốn thư giãn → Chém Hoa Quả (vui nhộn, giải trí)
   - Chơi với bạn bè → Race Master 3D Multiplayer

2. Hướng dẫn cụ thể:
   - Cách chơi: Giải thích ngắn gọn, dễ hiểu
   - Mẹo hay: Kỹ thuật cụ thể, áp dụng ngay được
   - So sánh: Ưu/nhược điểm từng game
   - Multiplayer: Chi tiết cách kết nối

3. Công nghệ MediaPipe:
   - Nhận diện 21 điểm trên bàn tay
   - Yêu cầu: Camera, ánh sáng đủ, nền tương phản
   - Khoảng cách tối ưu: 1-2m từ camera

**PHONG CÁCH TRẢ LỜI:**
- Ngắn gọn, súc tích (2-5 câu)
- Nhiệt tình, thân thiện
- Dùng emoji vừa phải
- Tập trung hành động cụ thể

**NGÔN NGỮ TRẢ LỜI (QUAN TRỌNG!):**
- Mặc định: Trả lời bằng Tiếng Việt
- Nếu câu hỏi bằng ngôn ngữ khác (English, 中文, 日本語, etc.) → Trả lời bằng ngôn ngữ đó
- Chào hỏi đơn giản (Hi, Hello, Hey) → Vẫn trả lời bằng Tiếng Việt
- Phát hiện ngôn ngữ câu hỏi và phản hồi tự nhiên

**MỤC TIÊU:** Giúp người chơi tìm game phù hợp và chơi giỏi hơn!"""


# ================= FALLBACK RESPONSES (ĐƠN GIẢN HÓA) =================
FALLBACK_RESPONSES = {
    'flappy_bird': """🐦 Flappy Bird - Game điều khiển cử chỉ dễ nhất!

Cách chơi:
• Chế độ 1 tay: Di chuyển tay lên/xuống → Chim bay
• Chế độ 2 tay: Tay trái bay lên, tay phải bay xuống
• Mục tiêu: Bay qua ống, ghi điểm cao

3 Mẹo vàng:
1. Giữ tay trong khung camera, di chuyển nhẹ nhàng
2. Nhìn xa phía trước, không chỉ nhìn chim
3. Luyện từ chậm → nhanh dần

Đây là game dễ nhất để bắt đầu!""",

    'race_master': """🏎️ Race Master 3D - Đua xe 3D siêu tốc!

Điều khiển:
• Nghiêng tay trái/phải → Rẽ xe
• Mở bàn tay → Tăng tốc
• Đóng bàn tay → Giảm tốc

Mẹo để thắng:
1. Rẽ mượt mà (nghiêng tay từ từ)
2. Tăng tốc ở đoạn thẳng, giảm tốc khi vào cua
3. Dự đoán trước đường đi của đối thủ
4. Luyện nhiều để làm chủ tốc độ

Chơi với bạn bè: Menu → Multiplayer""",

    'fruit_ninja': """🍎 Chém Hoa Quả - Ninja trái cây!

Cách chơi:
• Vung tay nhanh → Chém hoa quả bay lên
• Tránh bom 💣 (sẽ mất điểm/mạng)
• Combo nhiều quả → Điểm cao x2, x3!

Bí kíp cao thủ:
1. Giữ tay sẵn sàng ở giữa màn hình
2. Di chuyển tay nhanh, chính xác
3. Ưu tiên tránh bom hơn là chém quả
4. Combo = chém nhiều quả trong 1 lần vung tay

Game thư giãn nhất trong 3 game!""",

    'compare': """So sánh 3 Game:

🐦 Flappy Bird:
• Độ khó: Dễ nhất
• Ưu điểm: Phù hợp người mới, điều khiển đơn giản
• Nhược điểm: Gây nghiện cao, dễ chơi khó giỏi

🏎️ Race Master 3D:
• Độ khó: Trung bình đến Khó
• Ưu điểm: Đồ họa 3D đẹp, Multiplayer, thử thách kỹ năng
• Nhược điểm: Cần luyện tập nhiều

🍎 Chém Hoa Quả:
• Độ khó: Dễ đến Trung bình
• Ưu điểm: Vui nhộn thư giãn, phản xạ + chính xác
• Nhược điểm: Độ khó tăng dần theo level

Lời khuyên:
• Mới bắt đầu → Flappy Bird
• Thích tốc độ → Race Master 3D
• Muốn relax → Chém Hoa Quả""",

    'beginner': """Game dễ nhất cho người mới:

TOP 1: Flappy Bird
• Điều khiển cực đơn giản (chỉ lên/xuống)
• Làm quen công nghệ nhận diện cử chỉ
• Chơi được ngay, không cần học lâu
• Khuyên dùng chế độ 1 tay để bắt đầu

TOP 2: Chém Hoa Quả
• Vung tay tự nhiên, dễ hiểu
• Không gây stress, chơi vui
• Phù hợp mọi lứa tuổi

TOP 3: Race Master 3D
• Khó hơn, cần luyện tập
• Nên chơi sau khi quen Flappy Bird

Bắt đầu với Flappy Bird 10-15 phút, sau đó thử các game khác nhé!""",

    'tips': """Mẹo chơi game GestureAI giỏi hơn:

Thiết lập tối ưu (QUAN TRỌNG!):
• Đứng cách camera: 1-2 mét
• Ánh sáng: Đủ sáng, không quá tối/chói
• Nền: Đơn giản, tương phản với màu da
• Mặc áo: Màu khác với nền để camera nhận diện tốt

Kỹ thuật điều khiển:
• Giữ toàn bộ bàn tay trong khung hình camera
• Di chuyển mượt mà, tránh giật cục
• Bắt đầu chậm, quen rồi mới nhanh dần
• Thư giãn tay, đừng căng thẳng

Luyện tập hiệu quả:
• Mỗi ngày: 15-30 phút
• Bắt đầu: Flappy Bird (dễ) → Race Master (khó)
• Nghỉ 5 phút sau mỗi 20 phút chơi

Mẹo từng game:
• Flappy: Nhìn xa, giữ nhịp đều
• Race Master: Rẽ từ từ, tăng tốc đúng lúc
• Chém Hoa Quả: Tay ở giữa, combo quả

Luyện đều đặn = Tiến bộ nhanh!""",

    'gesture': """Hướng dẫn điều khiển cử chỉ tay:

Thiết lập Camera (Quan trọng!):
1. Camera nhìn rõ toàn bộ bàn tay
2. Ánh sáng: Đủ sáng, không quá tối/quá chói
3. Nền: Đơn giản, màu tương phản với da
4. Khoảng cách: 1-2 mét từ camera

Cử chỉ cơ bản:
• Di chuyển: Dịch tay lên/xuống/trái/phải
• Tăng tốc: Mở rộng bàn tay (5 ngón tách ra)
• Giảm tốc: Nắm lại (5 ngón co lại)
• Chém/Cắt: Vung tay nhanh qua vật thể

Ứng dụng trong game:
• Flappy Bird: Tay lên = Chim bay lên
• Race Master 3D: Tay trái = Rẽ trái, Tay phải = Rẽ phải
• Chém Hoa Quả: Vung tay = Chém quả

Công nghệ: MediaPipe nhận diện 21 điểm trên bàn tay để theo dõi siêu chính xác!

Lưu ý: Giữ tay trong khung hình, di chuyển tự nhiên!""",

    'multiplayer': """Hướng dẫn chơi Multiplayer - Race Master 3D:

Cách 1: Làm Server (Host)
1. Mở Race Master 3D
2. Menu → "Multiplayer" → "Create Server"
3. Nhập Port (VD: 5555, 8080, 3000)
4. Lấy IP của bạn (xem bên dưới)
5. Chia sẻ IP:Port cho bạn bè (VD: 192.168.1.5:5555)

Cách 2: Join Server (Client)
1. Xin IP:Port từ host
2. Mở Race Master 3D
3. Menu → "Multiplayer" → "Join Server"
4. Nhập IP:Port → Kết nối
5. Chờ host bắt đầu game

Lấy IP của bạn (Windows):
1. Nhấn Win + R
2. Gõ: cmd → Enter
3. Gõ: ipconfig → Enter
4. Tìm dòng "IPv4 Address" → Copy số đó (VD: 192.168.1.5)

Lưu ý:
• Cùng mạng WiFi/LAN kết nối tốt nhất
• Port thường dùng: 5555, 8080, 3000
• Tắt Firewall nếu không kết nối được
• Ping thử IP trước khi chơi: ping [IP]

Chơi với bạn bè vui hơn chơi một mình!""",

    'default': """Xin chào! Tôi là AI Trợ lý Game GestureAI 🎮

3 Game có sẵn:
• 🐦 Flappy Bird - Dễ, phù hợp người mới
• 🏎️ Race Master 3D - Đua xe 3D kịch tính
• 🍎 Chém Hoa Quả - Vui nhộn, thư giãn

Hỏi tôi về:
• "Game nào dễ nhất?"
• "Cách chơi Race Master 3D?"
• "So sánh 3 game"
• "Mẹo chơi giỏi hơn"
• "Hướng dẫn cử chỉ tay"
• "Chơi Multiplayer với bạn bè"

Hãy cho tôi biết bạn muốn gì nhé!"""
}


# ================= HELPER FUNCTIONS =================
def get_ai_model(model_index=0):
    """
    Trả về AI model đã cấu hình
    
    Args:
        model_index: Chỉ số model trong danh sách (0=Flash, 1=Pro)
    
    Returns:
        GenerativeModel instance
    """
    model_name = AI_MODELS[model_index] if model_index < len(AI_MODELS) else AI_MODELS[0]
    print(f"🤖 Sử dụng model: {model_name}")
    return genai.GenerativeModel(model_name)


def get_fallback_response(message):
    """Trả về fallback response dựa trên từ khóa"""
    msg = message.lower()
    
    # Phân tích từ khóa
    if any(word in msg for word in ['flappy', 'chim', 'bird', 'bay']):
        return FALLBACK_RESPONSES['flappy_bird']
    
    elif any(word in msg for word in ['đua xe', 'race', 'master', 'xe', 'lái', 'giỏi hơn']):
        return FALLBACK_RESPONSES['race_master']
    
    elif any(word in msg for word in ['hoa quả', 'fruit', 'ninja', 'chém', 'cắt']):
        return FALLBACK_RESPONSES['fruit_ninja']
    
    elif any(word in msg for word in ['so sánh', 'khác nhau', 'compare']):
        return FALLBACK_RESPONSES['compare']
    
    elif any(word in msg for word in ['dễ', 'mới', 'bắt đầu', 'beginner', 'easy']):
        return FALLBACK_RESPONSES['beginner']
    
    elif any(word in msg for word in ['mẹo', 'tips', 'trick', 'giỏi', 'cao thủ']):
        return FALLBACK_RESPONSES['tips']
    
    elif any(word in msg for word in ['cử chỉ', 'gesture', 'điều khiển', 'control']):
        return FALLBACK_RESPONSES['gesture']
    
    elif any(word in msg for word in ['multiplayer', 'nhiều người', 'bạn bè', 'ip', 'port']):
        return FALLBACK_RESPONSES['multiplayer']
    
    else:
        return FALLBACK_RESPONSES['default']