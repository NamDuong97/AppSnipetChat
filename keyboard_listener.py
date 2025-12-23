import time
import threading
import logging
from pynput import keyboard
from pynput.keyboard import Controller, Key, KeyCode
from database import Database

class TextExpander:
    def __init__(self, db_path="snippets.db"):
        # THIẾT LẬP LOGGING
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            filename='text_expander.log',
            filemode='w'
        )
        self.logger = logging.getLogger(__name__)
        
        # Cũng in ra console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        
        self.db = Database(db_path)
        self.buffer = ""
        self.is_enabled = True
        self.trigger_keys = {Key.space, Key.tab, Key.enter}
        
        self.max_buffer_length = 50
        self.controller = Controller()
        self.is_expanding = False
        self.modifiers = set()
        self.buffer_lock = threading.Lock()
        
        # THÊM: Theo dõi lần nhấn phím cuối để xử lý tiếng Việt
        self.last_key_time = time.time()
        self.key_debounce_time = 0.1  # 100ms
        
        self.logger.info("Text Expander initialized")
    
    def clear_buffer(self):
        """Xóa buffer và log"""
        with self.buffer_lock:
            if self.buffer:
                self.logger.debug(f"🔄 Clearing buffer: '{self.buffer}'")
                self.buffer = ""
    
    def add_to_buffer(self, char: str):
        """Thêm ký tự vào buffer với xử lý tiếng Việt"""
        current_time = time.time()
        
        # Xử lý debounce cho tiếng Việt
        if current_time - self.last_key_time < self.key_debounce_time:
            self.logger.debug(f"⚠️ Debounce: Ignoring fast key '{char}'")
            return
        
        self.last_key_time = current_time
        
        with self.buffer_lock:
            # KHÔNG bỏ qua space nữa - để xử lý riêng
            if len(self.buffer) >= self.max_buffer_length:
                removed = self.buffer[0]
                self.buffer = self.buffer[1:]
                self.logger.debug(f"Buffer full, removed '{removed}'")
            
            self.buffer += char
            self.logger.debug(f"➕ Added '{char}' → Buffer: '{self.buffer}'")
    
    def remove_from_buffer(self, count=1):
        """Xóa ký tự khỏi buffer"""
        with self.buffer_lock:
            if self.buffer:
                for _ in range(count):
                    if self.buffer:
                        removed = self.buffer[-1]
                        self.buffer = self.buffer[:-1]
                        self.logger.debug(f"➖ Removed '{removed}' → Buffer: '{self.buffer}'")
    
    def get_current_buffer(self):
        """Lấy buffer hiện tại"""
        with self.buffer_lock:
            return self.buffer
    
    def on_press(self, key):
        """Xử lý khi phím được nhấn"""
        if self.is_expanding:
            self.logger.debug("⏸️ Ignored (is_expanding)")
            return
        
        if not self.is_enabled:
            self.logger.debug("⏸️ Ignored (disabled)")
            return
        
        # Xử lý modifier keys
        if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r, 
                   Key.alt, Key.alt_l, Key.alt_r,
                   Key.shift, Key.shift_l, Key.shift_r]:
            self.modifiers.add(key)
            self.logger.debug(f"🔧 Modifier: {key}")
            return
        
        try:
            # Phím ký tự
            if hasattr(key, 'char') and key.char:
                # KHÔNG kiểm tra modifier nữa để hỗ trợ Shift+char
                self.add_to_buffer(key.char)
                    
        except AttributeError:
            # Phím đặc biệt
            if key == Key.backspace:
                current_buffer = self.get_current_buffer()
                self.logger.debug(f"⌫ Backspace on buffer: '{current_buffer}'")
                self.remove_from_buffer()
            
            # Kiểm tra trigger key (space, tab, enter)
            elif key in self.trigger_keys:
                current_buffer = self.get_current_buffer()
                self.logger.info(f"🎯 TRIGGER: {key} | Buffer: '{current_buffer}'")
                
                if current_buffer:
                    # QUAN TRỌNG: Xóa space khỏi buffer nếu có
                    if current_buffer.endswith(' '):
                        current_buffer = current_buffer.rstrip()
                        self.logger.debug(f"Trimmed space from buffer")
                    
                    self.process_buffer(current_buffer)
                else:
                    self.logger.debug("Empty buffer on trigger")
                
                # LUÔN xóa buffer sau trigger
                self.clear_buffer()
            
            # Hotkey bật/tắt ứng dụng (Ctrl+Alt+X)
            elif key == KeyCode.from_char('x'):
                if Key.ctrl in self.modifiers and Key.alt in self.modifiers:
                    self.logger.info("🔘 HOTKEY: Ctrl+Alt+X")
                    self.toggle_enabled()
            else:
                # Các phím đặc biệt khác - XÓA BUFFER
                self.logger.debug(f"🗑️ Special key, clearing buffer: {key}")
                self.clear_buffer()
    
    def on_release(self, key):
        """Xử lý khi phím được thả"""
        # Xóa modifier key
        if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r, 
                   Key.alt, Key.alt_l, Key.alt_r,
                   Key.shift, Key.shift_l, Key.shift_r]:
            if key in self.modifiers:
                self.modifiers.remove(key)
                self.logger.debug(f"🔧 Modifier released: {key}")
    
    def process_buffer(self, buffer_text: str):
        """Xử lý buffer để tìm và thay thế snippet"""
        # Loại bỏ khoảng trắng thừa
        keyword = buffer_text.strip()
        
        # QUAN TRỌNG: Xử lý tiếng Việt - loại bỏ dấu
        keyword_clean = self.remove_vietnamese_accents(keyword)
        self.logger.info(f"🔍 Processing: '{keyword}' → Clean: '{keyword_clean}'")
        
        if not keyword_clean:
            self.logger.debug("Empty keyword after cleaning")
            return
        
        # Tìm trong database với keyword đã làm sạch
        content = self.db.get_snippet(keyword_clean)
        if not content:
            # Thử tìm với keyword gốc
            content = self.db.get_snippet(keyword)
        
        if content:
            self.logger.info(f"✅ FOUND: '{keyword_clean}' → '{content[:50]}...'")
            self.replace_text(keyword, content)
        else:
            self.logger.info(f"❌ NOT FOUND: '{keyword_clean}'")
    
    def remove_vietnamese_accents(self, text: str) -> str:
        """Loại bỏ dấu tiếng Việt để tìm keyword"""
        if not text:
            return text
        
        # Bảng chuyển đổi dấu tiếng Việt
        vietnamese_map = {
            'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'đ': 'd',
            'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
            'À': 'A', 'Á': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
            'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
            'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
            'Đ': 'D',
            'È': 'E', 'É': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
            'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
            'Ì': 'I', 'Í': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
            'Ò': 'O', 'Ó': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
            'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
            'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
            'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
            'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
            'Ỳ': 'Y', 'Ý': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
        }
        
        result = []
        for char in text:
            if char in vietnamese_map:
                result.append(vietnamese_map[char])
            else:
                result.append(char)
        
        return ''.join(result)
    
    def type_unicode(self, text: str):
        """Gõ text an toàn với Unicode"""
        self.logger.debug(f"⌨️ Typing: '{text[:50]}...'")
        for ch in text:
            self.controller.press(ch)
            self.controller.release(ch)
            time.sleep(0.002)
    
    def replace_text(self, keyword: str, content: str):
        """Xóa keyword và gõ content mới"""
        if self.is_expanding:
            self.logger.warning("Already expanding, skipping")
            return
            
        self.is_expanding = True
        
        try:
            # Chỉ xóa số ký tự bằng độ dài keyword (KHÔNG +1 cho space)
            # Vì space đã được trigger xử lý
            backspace_count = len(keyword)
            self.logger.info(f"🔄 Replacing: '{keyword}' ({backspace_count} chars)")
            
            # Xóa keyword
            for i in range(backspace_count):
                self.controller.press(Key.backspace)
                self.controller.release(Key.backspace)
                time.sleep(0.001)
            
            # Gõ content mới
            self.type_unicode(content)
            
            self.logger.info(f"✅ DONE: '{keyword}' → '{content[:50]}...'")
            
        except Exception as e:
            self.logger.error(f"❌ ERROR: {e}")
        finally:
            self.is_expanding = False
            # QUAN TRỌNG: Xóa buffer sau khi thay thế xong
            self.clear_buffer()
    
    def toggle_enabled(self):
        """Bật/tắt ứng dụng"""
        self.is_enabled = not self.is_enabled
        status = "BẬT" if self.is_enabled else "TẮT"
        self.logger.info(f"🔘 TOGGLE: {status}")
        print(f"\n[APP] Text Expander {status}\n")
    
    def start(self):
        """Bắt đầu lắng nghe bàn phím"""
        self.logger.info("🎧 Starting keyboard listener...")
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        self.listener.join()
    
    def stop(self):
        """Dừng lắng nghe"""
        if hasattr(self, 'listener'):
            self.listener.stop()
            self.logger.info("Keyboard listener stopped")