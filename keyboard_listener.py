import time
import threading
import logging
import re
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
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        self.db = Database(db_path)
        
        # Buffer - chỉ lưu word hiện tại
        self.buffer = ""
        self.is_enabled = True
        
        # Trigger keys
        self.trigger_keys = {Key.space, Key.tab, Key.enter}
        
        # Controller
        self.controller = Controller()
        
        # Flags
        self.is_expanding = False
        self.modifiers = set()
        self.buffer_lock = threading.Lock()
        
        # Thời gian debounce cho Unikey
        self.last_char_time = 0
        self.char_debounce = 0.05  # 50ms - giảm xuống để responsive hơn
        
        # Timeout cho buffer - tự động xóa nếu không gõ trong X giây
        self.buffer_timeout = 5.0  # 5 giây
        self.last_activity_time = time.time()
        
        self.logger.info("=" * 60)
        self.logger.info("Text Expander initialized - IMPROVED VERSION")
        self.logger.info("=" * 60)
    
    def is_valid_char(self, char):
        """Kiểm tra ký tự có hợp lệ cho keyword không"""
        if not char:
            return False
        # Chấp nhận: chữ cái, số, dấu gạch dưới, dấu chấm
        return char.isalnum() or char in ['_', '.', '-']
    
    def clear_buffer(self, reason=""):
        """Xóa buffer"""
        with self.buffer_lock:
            if self.buffer:
                self.logger.debug(f"🔄 Clear buffer [{reason}]: '{self.buffer}' -> ''")
                self.buffer = ""
            self.last_activity_time = time.time()
    
    def add_to_buffer(self, char: str):
        """Thêm ký tự vào buffer"""
        current_time = time.time()
        
        # Debounce để xử lý Unikey
        time_since_last = current_time - self.last_char_time
        if time_since_last < self.char_debounce:
            self.logger.debug(f"⚠️ Debounce skip: '{char}' ({time_since_last:.3f}s)")
            return
        
        self.last_char_time = current_time
        
        with self.buffer_lock:
            # Kiểm tra timeout - xóa buffer nếu quá lâu không gõ
            if current_time - self.last_activity_time > self.buffer_timeout:
                if self.buffer:
                    self.logger.debug(f"⏱️ Buffer timeout, clearing: '{self.buffer}'")
                    self.buffer = ""
            
            # Chỉ thêm ký tự hợp lệ
            if self.is_valid_char(char):
                self.buffer += char
                self.logger.debug(f"➕ '{char}' -> buffer: '{self.buffer}'")
            else:
                self.logger.debug(f"❌ Invalid char ignored: '{char}' (ord: {ord(char)})")
            
            self.last_activity_time = current_time
    
    def remove_from_buffer(self, count=1):
        """Xóa ký tự khỏi buffer"""
        with self.buffer_lock:
            if self.buffer:
                old_buffer = self.buffer
                self.buffer = self.buffer[:-count] if len(self.buffer) > count else ""
                self.logger.debug(f"➖ Backspace: '{old_buffer}' -> '{self.buffer}'")
                self.last_activity_time = time.time()
    
    def get_current_buffer(self):
        """Lấy buffer hiện tại (thread-safe)"""
        with self.buffer_lock:
            return self.buffer
    
    def on_press(self, key):
        """Xử lý khi phím được nhấn"""
        # Bỏ qua nếu đang expanding
        if self.is_expanding:
            return
        
        # Bỏ qua nếu disabled
        if not self.is_enabled:
            return
        
        try:
            # ===== XỬ LÝ MODIFIER KEYS =====
            if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r, 
                       Key.alt, Key.alt_l, Key.alt_r,
                       Key.shift, Key.shift_l, Key.shift_r,
                       Key.cmd, Key.cmd_l, Key.cmd_r]:
                self.modifiers.add(key)
                return
            
            # Nếu có modifier (ngoại trừ Shift đơn), xóa buffer
            non_shift_modifiers = self.modifiers - {Key.shift, Key.shift_l, Key.shift_r}
            if non_shift_modifiers:
                self.clear_buffer("modifier key combo")
                return
            
            # ===== XỬ LÝ KÝ TỰ THƯỜNG =====
            if hasattr(key, 'char') and key.char:
                # Chỉ thêm ký tự hợp lệ vào buffer
                if self.is_valid_char(key.char):
                    self.add_to_buffer(key.char)
                else:
                    # Ký tự đặc biệt -> xóa buffer
                    self.clear_buffer(f"special char: '{key.char}'")
                return
        
        except AttributeError:
            # ===== XỬ LÝ PHÍM ĐỆC BIỆT =====
            
            # Backspace
            if key == Key.backspace:
                self.remove_from_buffer()
                return
            
            # Trigger keys (space, tab, enter)
            if key in self.trigger_keys:
                current_buffer = self.get_current_buffer()
                
                self.logger.info("=" * 60)
                self.logger.info(f"🎯 TRIGGER: {key}")
                self.logger.info(f"📝 Buffer: '{current_buffer}'")
                
                if current_buffer:
                    # Xử lý buffer
                    self.process_buffer(current_buffer, key)
                else:
                    self.logger.info("❌ Buffer empty, nothing to process")
                
                # XÓA BUFFER NGAY SAU TRIGGER
                self.clear_buffer("after trigger")
                self.logger.info("=" * 60)
                return
            
            # Hotkey toggle (Ctrl+Alt+X)
            if key == KeyCode.from_char('x') or key == KeyCode.from_char('X'):
                if (Key.ctrl in self.modifiers or Key.ctrl_l in self.modifiers or Key.ctrl_r in self.modifiers) and \
                   (Key.alt in self.modifiers or Key.alt_l in self.modifiers or Key.alt_r in self.modifiers):
                    self.toggle_enabled()
                    return
            
            # Các phím di chuyển con trỏ - KHÔNG xóa buffer
            cursor_keys = {Key.left, Key.right, Key.up, Key.down, Key.home, Key.end, Key.page_up, Key.page_down}
            if key in cursor_keys:
                self.logger.debug(f"🔽 Cursor key: {key}, keeping buffer")
                return
            
            # Các phím khác - xóa buffer
            self.clear_buffer(f"special key: {key}")
    
    def on_release(self, key):
        """Xử lý khi phím được thả"""
        # Xóa modifier
        if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r, 
                   Key.alt, Key.alt_l, Key.alt_r,
                   Key.shift, Key.shift_l, Key.shift_r,
                   Key.cmd, Key.cmd_l, Key.cmd_r]:
            self.modifiers.discard(key)
    
    def process_buffer(self, keyword: str, trigger_key):
        """Xử lý buffer để tìm và thay thế snippet"""
        if not keyword:
            return
        
        # Làm sạch keyword
        keyword = keyword.strip()
        
        self.logger.info(f"🔍 Searching for keyword: '{keyword}'")
        
        # Tìm kiếm theo thứ tự ưu tiên:
        # 1. Exact match (chính xác)
        # 2. Lowercase match (không phân biệt hoa thường)
        # 3. Without Vietnamese accents (bỏ dấu tiếng Việt)
        
        content = None
        match_type = None
        
        # 1. Exact match
        content = self.db.get_snippet(keyword)
        if content:
            match_type = "exact"
            self.logger.info(f"✅ Found [EXACT]: '{keyword}'")
        
        # 2. Lowercase match
        if not content:
            content = self.db.get_snippet(keyword.lower())
            if content:
                match_type = "lowercase"
                self.logger.info(f"✅ Found [LOWERCASE]: '{keyword.lower()}'")
        
        # 3. Without accents
        if not content:
            keyword_no_accents = self.remove_vietnamese_accents(keyword)
            if keyword_no_accents != keyword:
                content = self.db.get_snippet(keyword_no_accents)
                if content:
                    match_type = "no_accents"
                    self.logger.info(f"✅ Found [NO_ACCENTS]: '{keyword_no_accents}'")
        
        # 4. Search in database with LIKE
        if not content:
            search_results = self.db.search_snippets(keyword)
            if search_results:
                # Lấy kết quả đầu tiên
                first_result = search_results[0]
                found_keyword = first_result['keyword']
                content = first_result['content']
                match_type = "search"
                self.logger.info(f"✅ Found [SEARCH]: '{found_keyword}' matches '{keyword}'")
        
        # Thay thế nếu tìm thấy
        if content:
            self.logger.info(f"📤 Content preview: '{content[:100]}{'...' if len(content) > 100 else ''}'")
            self.replace_text(keyword, content, trigger_key)
        else:
            self.logger.info(f"❌ NOT FOUND: '{keyword}'")
    
    def remove_vietnamese_accents(self, text: str) -> str:
        """Loại bỏ dấu tiếng Việt"""
        if not text:
            return text
        
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
        
        result = ''.join(vietnamese_map.get(char, char) for char in text)
        return result
    
    def replace_text(self, keyword: str, content: str, trigger_key):
        """Xóa keyword và gõ content mới"""
        if self.is_expanding:
            self.logger.warning("⚠️ Already expanding, skip")
            return
        
        self.is_expanding = True
        
        try:
            # Số ký tự cần xóa = độ dài keyword
            backspace_count = len(keyword)
            
            self.logger.info(f"🔄 Replacing '{keyword}' ({backspace_count} chars) with '{content[:50]}...'")
            
            # Đợi một chút để đảm bảo trigger key đã được xử lý
            time.sleep(0.05)
            
            # Xóa keyword bằng backspace
            for i in range(backspace_count):
                self.controller.press(Key.backspace)
                self.controller.release(Key.backspace)
                time.sleep(0.01)  # Tăng delay giữa các backspace
            
            # Đợi một chút trước khi gõ
            time.sleep(0.05)
            
            # Gõ content mới
            self.type_text(content)
            
            # Nếu trigger key là space, thêm space sau content
            if trigger_key == Key.space:
                time.sleep(0.02)
                self.controller.press(Key.space)
                self.controller.release(Key.space)
            
            self.logger.info(f"✅ REPLACEMENT DONE")
            
        except Exception as e:
            self.logger.error(f"❌ ERROR in replace_text: {e}", exc_info=True)
        finally:
            # Đợi một chút trước khi bật lại
            time.sleep(0.1)
            self.is_expanding = False
    
    def type_text(self, text: str):
        """Gõ text với xử lý Unicode"""
        self.logger.debug(f"⌨️ Typing {len(text)} characters...")
        
        for char in text:
            try:
                # Xử lý ký tự đặc biệt
                if char == '\n':
                    self.controller.press(Key.enter)
                    self.controller.release(Key.enter)
                elif char == '\t':
                    self.controller.press(Key.tab)
                    self.controller.release(Key.tab)
                else:
                    # Gõ ký tự thường
                    self.controller.press(char)
                    self.controller.release(char)
                
                # Delay nhỏ giữa các ký tự
                time.sleep(0.005)
                
            except Exception as e:
                self.logger.error(f"❌ Error typing char '{char}': {e}")
    
    def toggle_enabled(self):
        """Bật/tắt ứng dụng"""
        self.is_enabled = not self.is_enabled
        status = "BẬT ✅" if self.is_enabled else "TẮT ❌"
        
        self.logger.info("=" * 60)
        self.logger.info(f"🔘 TOGGLE: Text Expander is now {status}")
        self.logger.info("=" * 60)
        
        print(f"\n{'='*60}")
        print(f"Text Expander: {status}")
        print(f"{'='*60}\n")
        
        # Xóa buffer khi toggle
        self.clear_buffer("toggle")
    
    def start(self):
        """Bắt đầu lắng nghe bàn phím"""
        self.logger.info("🎧 Starting keyboard listener...")
        print("\n" + "="*60)
        print("Text Expander STARTED")
        print("Press Ctrl+Alt+X to toggle ON/OFF")
        print("="*60 + "\n")
        
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
            self.logger.info("🛑 Keyboard listener stopped")