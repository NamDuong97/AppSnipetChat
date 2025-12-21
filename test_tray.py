import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtGui import QIcon

app = QApplication(sys.argv)

# Kiểm tra xem hệ thống có hỗ trợ system tray không
if not QSystemTrayIcon.isSystemTrayAvailable():
    print("❌ Hệ thống không hỗ trợ system tray!")
else:
    print("✅ System tray available")
    
# Tạo tray icon
tray = QSystemTrayIcon()
icon_path = "resources/icon.png"  # Hoặc icon.ico

if QIcon(icon_path).isNull():
    print(f"❌ Không tìm thấy icon tại: {icon_path}")
else:
    tray.setIcon(QIcon(icon_path))
    tray.setVisible(True)
    print("✅ Đã tạo tray icon")
    
sys.exit(app.exec())