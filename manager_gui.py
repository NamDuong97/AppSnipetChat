import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from database import Database

class SnippetManager(QMainWindow):
    def __init__(self, db_path="snippets.db"):
        super().__init__()
        self.db = Database(db_path)
        self.init_ui()
        self.load_snippets()
    
    def init_ui(self):
        self.setWindowTitle("Quản lý Tin nhắn Nhanh")
        self.setGeometry(300, 200, 900, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # 1. Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Tìm kiếm:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa hoặc nội dung để tìm...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        
        self.total_label = QLabel("Tổng: 0 snippets")
        search_layout.addWidget(self.total_label)
        
        main_layout.addLayout(search_layout)
        
        # 2. Splitter (Danh sách bên trái, chi tiết bên phải)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: List widget
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("📋 Danh sách snippets:"))
        self.snippet_list = QListWidget()
        self.snippet_list.itemClicked.connect(self.on_item_selected)
        left_layout.addWidget(self.snippet_list)
        
        # Right: Detail widget
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Keyword
        right_layout.addWidget(QLabel("✏️ Keyword:"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("vd: cc, email, address")
        right_layout.addWidget(self.keyword_input)
        
        # Content
        right_layout.addWidget(QLabel("📝 Nội dung (Enter để xuống dòng):"))
        self.content_input = QTextEdit()
        self.content_input.setMinimumHeight(150)
        right_layout.addWidget(self.content_input)
        
        # Stats
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Chưa chọn snippet")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        right_layout.addLayout(stats_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Lưu")
        self.save_btn.clicked.connect(self.save_snippet)
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("🗑️ Xóa")
        self.delete_btn.clicked.connect(self.delete_snippet)
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        button_layout.addWidget(self.delete_btn)
        
        self.new_btn = QPushButton("➕ Mới")
        self.new_btn.clicked.connect(self.new_snippet)
        button_layout.addWidget(self.new_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_snippets)
        button_layout.addWidget(self.export_btn)
        
        right_layout.addLayout(button_layout)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 600])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Sẵn sàng")
        
        # Menu bar
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("📁 File")
        
        import_action = QAction("Import từ JSON", self)
        import_action.triggered.connect(self.import_snippets)
        file_menu.addAction(import_action)
        
        export_action = QAction("Export ra JSON", self)
        export_action.triggered.connect(self.export_snippets)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Thoát", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Trợ giúp")
        
        about_action = QAction("Giới thiệu", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def load_snippets(self):
        """Load tất cả snippets vào list"""
        self.snippet_list.clear()
        snippets = self.db.get_all_snippets()
        
        for snippet in snippets:
            keyword = snippet['keyword']
            content = snippet['content']
            usage = snippet['usage_count']
            last_used = snippet['last_used'] or "Chưa dùng"
            
            item_text = f"{keyword} ({usage} lần) - {content[:40]}..."
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, keyword)  # Lưu keyword vào item
            
            # Tô màu theo mức độ sử dụng
            if usage > 20:
                item.setForeground(QColor("#4CAF50"))  # Xanh lá
            elif usage > 5:
                item.setForeground(QColor("#FF9800"))  # Cam
            
            self.snippet_list.addItem(item)
        
        self.total_label.setText(f"Tổng: {len(snippets)} snippets")
    
    def on_search(self, text):
        """Tìm kiếm real-time"""
        if not text:
            self.load_snippets()
            return
        
        self.snippet_list.clear()
        results = self.db.search_snippets(text)
        
        for snippet in results:
            keyword = snippet['keyword']
            content = snippet['content']
            usage = snippet['usage_count']
            
            item_text = f"{keyword} ({usage} lần) - {content[:40]}..."
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, keyword)
            self.snippet_list.addItem(item)
    
    def on_item_selected(self, item):
        """Khi chọn một item trong list"""
        keyword = item.data(Qt.UserRole)
        content = self.db.get_snippet(keyword)
        
        if content:
            self.keyword_input.setText(keyword)
            self.content_input.setPlainText(content)
            
            # Hiển thị stats
            snippets = self.db.get_all_snippets()
            for s in snippets:
                if s['keyword'] == keyword:
                    usage = s['usage_count']
                    last_used = s['last_used'] or "Chưa dùng"
                    self.stats_label.setText(f"Đã dùng: {usage} lần | Lần cuối: {last_used}")
                    break
    
    def save_snippet(self):
        """Lưu snippet mới hoặc cập nhật"""
        keyword = self.keyword_input.text().strip()
        content = self.content_input.toPlainText().strip()
        
        if not keyword or not content:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ keyword và nội dung!")
            return
        
        # Kiểm tra nếu keyword đã tồn tại
        existing_content = self.db.get_snippet(keyword)
        
        if existing_content:
            # Cập nhật
            reply = QMessageBox.question(
                self, "Xác nhận",
                f"Keyword '{keyword}' đã tồn tại. Bạn có muốn cập nhật không?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.db.update_snippet(keyword, content):
                    self.statusBar().showMessage(f"Đã cập nhật: {keyword}")
                    self.load_snippets()
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể cập nhật!")
        else:
            # Thêm mới
            if self.db.add_snippet(keyword, content):
                self.statusBar().showMessage(f"Đã thêm mới: {keyword}")
                self.load_snippets()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể thêm mới!")
    
    def delete_snippet(self):
        """Xóa snippet"""
        keyword = self.keyword_input.text().strip()
        
        if not keyword:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn snippet để xóa!")
            return
        
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa '{keyword}' không?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.delete_snippet(keyword):
                self.statusBar().showMessage(f"Đã xóa: {keyword}")
                self.new_snippet()
                self.load_snippets()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể xóa!")
    
    def new_snippet(self):
        """Tạo snippet mới"""
        self.keyword_input.clear()
        self.content_input.clear()
        self.stats_label.setText("Chưa chọn snippet")
        self.keyword_input.setFocus()
    
    def export_snippets(self):
        """Export snippets ra file JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Snippets", "", "JSON Files (*.json)"
        )
        
        if file_path:
            snippets = self.db.get_all_snippets()
            import json
            
            data = {}
            for snippet in snippets:
                data[snippet['keyword']] = snippet['content']
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Thành công", f"Đã export {len(data)} snippets!")
    
    def import_snippets(self):
        """Import snippets từ file JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Snippets", "", "JSON Files (*.json)"
        )
        
        if file_path:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = 0
            for keyword, content in data.items():
                if self.db.add_snippet(keyword, content):
                    count += 1
            
            QMessageBox.information(self, "Thành công", f"Đã import {count} snippets!")
            self.load_snippets()
    
    def show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        QMessageBox.about(
            self,
            "Giới thiệu",
            "Text Expander\n\n"
            "Ứng dụng giúp bạn gõ nhanh các đoạn tin nhắn thường dùng.\n"
            "Chỉ cần gõ keyword + Space để tự động thay thế.\n\n"
            "Phiên bản: 1.0\n"
            "Tác giả: Text Expander Team"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnippetManager()
    window.show()
    sys.exit(app.exec())