import sys
import threading
import os
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

# ========== GLOBAL FLAGS ==========
HAS_KEYBOARD = False
HAS_GUI = False

# ========== IMPORT VÀ SET FLAGS ==========
# Import keyboard_listener
try:
    from keyboard_listener import TextExpander
    HAS_KEYBOARD = True
    print("✅ Đã import keyboard_listener")
except ImportError as e:
    print(f"❌ Không import được keyboard_listener: {e}")

# Import manager_gui
try:
    from manager_gui import SnippetManager
    HAS_GUI = True
    print("✅ Đã import manager_gui")
except ImportError as e:
    print(f"❌ Không import được manager_gui: {e}")

# ========== CLASS SystemTrayApp ==========
class SystemTrayApp:
    def __init__(self):
        # Tạo QApplication - BẮT BUỘC phải tạo trước
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        print("✅ Đã tạo QApplication")
        
        # Tìm icon
        icon_path = None
        possible_paths = [
            "resources/icon.png",
            "resources/icon.ico",
            os.path.join(os.path.dirname(__file__), "resources/icon.png"),
            os.path.join(os.path.dirname(__file__), "resources/icon.ico"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                icon_path = path
                print(f"✅ Tìm thấy icon: {path}")
                break
        
        # Tạo icon
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if icon.isNull():
                print("⚠️ Icon tồn tại nhưng không load được")
                icon = self.app.style().standardIcon(QStyle.SP_ComputerIcon)
        else:
            print("⚠️ Không tìm thấy icon file")
            icon = self.app.style().standardIcon(QStyle.SP_ComputerIcon)
        
        # Kiểm tra system tray
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("❌ Hệ thống không hỗ trợ system tray!")
            QMessageBox.critical(None, "Lỗi", "Hệ thống không hỗ trợ system tray!")
            sys.exit(1)
        
        # Tạo tray icon
        self.tray = QSystemTrayIcon(icon, self.app)
        self.tray.setToolTip("Text Expander\nClick phải để mở menu")
        
        # Tạo menu
        self.menu = QMenu()
        
        # Action: Mở quản lý
        self.show_action = QAction("📝 Mở Quản lý", self.menu)
        self.show_action.triggered.connect(self.show_manager)
        self.show_action.setEnabled(HAS_GUI)
        self.menu.addAction(self.show_action)
        
        # Action: Bật/Tắt
        self.toggle_action = QAction("✅ Bật", self.menu)
        self.toggle_action.triggered.connect(self.toggle_expander)
        self.toggle_action.setEnabled(HAS_KEYBOARD)
        self.menu.addAction(self.toggle_action)
        
        self.menu.addSeparator()
        
        # Action: Thống kê
        self.stats_action = QAction("📊 Thống kê", self.menu)
        self.stats_action.triggered.connect(self.show_stats)
        self.menu.addAction(self.stats_action)
        
        self.menu.addSeparator()
        
        # Action: Thoát
        self.quit_action = QAction("🚪 Thoát", self.menu)
        self.quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.quit_action)
        
        # Gán menu cho tray
        self.tray.setContextMenu(self.menu)
        
        # Kết nối sự kiện
        self.tray.activated.connect(self.on_tray_clicked)
        
        # Khởi tạo keyboard listener (chỉ nếu import thành công)
        self.expander = None
        self.listener_thread = None
        
        if HAS_KEYBOARD:
            try:
                self.expander = TextExpander()
                print("✅ Đã tạo TextExpander")
            except Exception as e:
                print(f"❌ Lỗi khởi tạo TextExpander: {e}")
        
        print("✅ Đã khởi tạo xong SystemTrayApp")
    
    def show(self):
        """Hiển thị tray icon"""
        if self.tray:
            self.tray.show()
            print("✅ Đã gọi tray.show()")
            
            # Hiển thị thông báo sau 1 giây
            QTimer.singleShot(1000, self.show_welcome_message)
    
    def show_welcome_message(self):
        """Hiển thị message chào mừng"""
        if self.tray.supportsMessages():
            self.tray.showMessage(
                "Text Expander",
                "Ứng dụng đã khởi động!\nClick phải vào icon để mở menu.",
                QSystemTrayIcon.Information,
                3000
            )
        else:
            print("⚠️ Hệ thống không hỗ trợ tray messages")
    
    def on_tray_clicked(self, reason):
        """Xử lý khi click vào tray icon"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_manager()
    
    def show_manager(self):
        """Hiển thị cửa sổ quản lý"""
        if not HAS_GUI:
            QMessageBox.warning(None, "Lỗi", "Không thể mở trình quản lý!")
            return
        
        try:
            if not hasattr(self, 'manager_window') or not self.manager_window.isVisible():
                self.manager_window = SnippetManager()
                self.manager_window.show()
                print("✅ Đã mở cửa sổ quản lý")
            else:
                self.manager_window.raise_()
                self.manager_window.activateWindow()
        except Exception as e:
            print(f"❌ Lỗi khi mở manager: {e}")
            QMessageBox.critical(None, "Lỗi", f"Không thể mở trình quản lý: {e}")
    
    def toggle_expander(self):
        """Bật/tắt text expander"""
        if not HAS_KEYBOARD or self.expander is None:
            QMessageBox.warning(None, "Lỗi", "Chức năng keyboard listener không khả dụng!")
            return
        
        try:
            self.expander.toggle_enabled()
            if hasattr(self.expander, 'is_enabled') and self.expander.is_enabled:
                self.toggle_action.setText("✅ Bật")
                self.show_message("Đã BẬT", "Chức năng thay thế đã được bật")
            else:
                self.toggle_action.setText("❌ Tắt")
                self.show_message("Đã TẮT", "Chức năng thay thế đã được tắt")
        except Exception as e:
            print(f"❌ Lỗi khi toggle expander: {e}")
    
    def show_message(self, title, message):
        """Hiển thị message"""
        if self.tray.supportsMessages():
            self.tray.showMessage(title, message, QSystemTrayIcon.Information, 2000)
    
    def show_stats(self):
        """Hiển thị thống kê"""
        QMessageBox.information(
            None,
            "Thống kê",
            f"Trạng thái ứng dụng:\n\n"
            f"• Keyboard Listener: {'✅ Sẵn sàng' if HAS_KEYBOARD else '❌ Lỗi'}\n"
            f"• GUI Manager: {'✅ Sẵn sàng' if HAS_GUI else '❌ Lỗi'}\n"
            f"• Tray Icon: {'✅ Hiển thị' if self.tray.isVisible() else '❌ Ẩn'}\n"
            f"• Tray Available: {'✅ Có' if QSystemTrayIcon.isSystemTrayAvailable() else '❌ Không'}"
        )
    
    def start_keyboard_listener(self):
        """Bắt đầu keyboard listener"""
        if HAS_KEYBOARD and self.expander and hasattr(self.expander, 'start'):
            try:
                # Tạo thread mới
                self.listener_thread = threading.Thread(
                    target=self.expander.start,
                    daemon=True,
                    name="KeyboardListener"
                )
                self.listener_thread.start()
                print("✅ Đã bắt đầu keyboard listener")
            except Exception as e:
                print(f"❌ Lỗi khi start keyboard listener: {e}")
    
    def quit_app(self):
        """Thoát ứng dụng"""
        reply = QMessageBox.question(
            None,
            "Xác nhận thoát",
            "Bạn có chắc chắn muốn thoát Text Expander?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            print("🔄 Đang thoát ứng dụng...")
            # Ẩn tray icon
            if self.tray:
                self.tray.hide()
            # Thoát ứng dụng
            self.app.quit()
    
    def run(self):
        """Chạy ứng dụng"""
        # Hiển thị tray icon
        self.show()
        
        # Bắt đầu keyboard listener
        self.start_keyboard_listener()
        
        print("✅ Đang chạy Qt event loop...")
        # Chạy ứng dụng
        return self.app.exec()

# ========== HÀM CHÍNH ==========
def main():
    """Hàm chính"""
    print("=" * 50)
    print("🔄 Đang khởi động Text Expander...")
    print(f"Python: {sys.version}")
    print(f"Current dir: {os.getcwd()}")
    print("=" * 50)
    
    # Tạo và chạy ứng dụng
    try:
        tray_app = SystemTrayApp()
        return_code = tray_app.run()
        print(f"✅ Ứng dụng đã thoát với mã: {return_code}")
        sys.exit(return_code)
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng: {e}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(None, "Lỗi nghiêm trọng", f"Không thể khởi động ứng dụng:\n{e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())