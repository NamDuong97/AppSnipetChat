import time
import threading
from pynput import keyboard
from pynput.keyboard import Controller, Key
from database import Database

class TextExpander:
    def __init__(self, db_path="snippets.db"):
        self.db = Database(db_path)
        self.buffer = ""  # Lưu các ký tự đã gõ
        self.is_enabled = True  # Trạng thái bật/tắt
        self.trigger_keys = {
            Key.space: True,
            Key.tab: True,
            Key.enter: True,
        }
        
        # Có thể thêm trigger tùy chỉnh
        self.custom_trigger = "space"  # space/tab/enter
        
        # Giới hạn buffer (tránh lưu quá dài)
        self.max_buffer_length = 20
        
        # Keyboard controller để gõ tự động
        self.controller = Controller()
        
        # Lock để tránh xung đột
        self.buffer_lock = threading.Lock()
        
        print("Text Expander initialized. Press Ctrl+Alt+X to toggle on/off")
    
    def clear_buffer(self):
        """Xóa buffer"""
        with self.buffer_lock:
            self.buffer = ""
    
    def add_to_buffer(self, char: str):
        """Thêm ký tự vào buffer"""
        with self.buffer_lock:
            if len(self.buffer) >= self.max_buffer_length:
                self.buffer = self.buffer[1:]  # Xóa ký tự đầu
            self.buffer += char
    
    def remove_from_buffer(self):
        """Xóa ký tự cuối khỏi buffer"""
        with self.buffer_lock:
            if self.buffer:
                self.buffer = self.buffer[:-1]
    
    def get_current_buffer(self):
        """Lấy buffer hiện tại"""
        with self.buffer_lock:
            return self.buffer
    
    def on_press(self, key):
        """Xử lý khi phím được nhấn"""
        if not self.is_enabled:
            return
        
        try:
            # Phím ký tự
            if hasattr(key, 'char') and key.char:
                self.add_to_buffer(key.char)
                # Debug (có thể tắt)
                # print(f"Buffer: {self.get_current_buffer()}")
                
        except AttributeError:
            # Phím đặc biệt
            if key == Key.backspace:
                self.remove_from_buffer()
            
            # Kiểm tra trigger key
            elif key in self.trigger_keys:
                current_buffer = self.get_current_buffer()
                if current_buffer:
                    self.process_buffer(current_buffer)
                self.clear_buffer()
            
            # Hotkey bật/tắt ứng dụng (Ctrl+Alt+X)
            elif key == KeyCode.from_char('x') and self.is_ctrl_alt_pressed():
                self.toggle_enabled()
    
    def process_buffer(self, buffer_text: str):
        """Xử lý buffer và thay thế nếu tìm thấy snippet"""
        # Loại bỏ khoảng trắng thừa
        keyword = buffer_text.strip()
        
        if not keyword:
            return
        
        # Tìm trong database
        content = self.db.get_snippet(keyword)
        
        if content:
            print(f"Expanding: '{keyword}' -> '{content[:30]}...'")
            self.replace_text(keyword, content)
    
    def replace_text(self, keyword: str, content: str):
        """Xóa keyword và gõ content mới"""
        # Tính số lần backspace cần gõ
        backspace_count = len(keyword)
        
        # Gõ backspace để xóa keyword
        for _ in range(backspace_count):
            self.controller.press(Key.backspace)
            self.controller.release(Key.backspace)
            time.sleep(0.001)  # Delay nhỏ để ổn định
        
        # Gõ nội dung mới
        self.controller.type(content)
    
    def toggle_enabled(self):
        """Bật/tắt ứng dụng"""
        self.is_enabled = not self.is_enabled
        status = "ENABLED" if self.is_enabled else "DISABLED"
        print(f"Text Expander {status}")
        
        # Có thể thêm notification ở đây
        self.show_notification(f"Text Expander {status}")
    
    def is_ctrl_alt_pressed(self):
        """Kiểm tra Ctrl+Alt có đang được nhấn không"""
        # Cần implement listener cho modifier keys
        return False  # Tạm thời
    
    def show_notification(self, message: str):
        """Hiển thị notification (placeholder)"""
        print(f"Notification: {message}")
        # Có thể implement với hệ thống notification
    
    def start(self):
        """Bắt đầu lắng nghe bàn phím"""
        print("Starting keyboard listener...")
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        self.listener.join()
    
    def stop(self):
        """Dừng lắng nghe"""
        if hasattr(self, 'listener'):
            self.listener.stop()