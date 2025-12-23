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
        self.setWindowTitle("Quản lý Tin nhắn Nhanh - Text Expander")
        self.setGeometry(300, 200, 1000, 650)
        
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
        self.total_label.setStyleSheet("font-weight: bold; color: #2196F3;")
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
        self.snippet_list.setAlternatingRowColors(True)
        left_layout.addWidget(self.snippet_list)
        
        # Right: Detail widget
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Keyword
        right_layout.addWidget(QLabel("✏️ Keyword (từ khóa tắt):"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("vd: cc, email, addr, tel...")
        self.keyword_input.setMaxLength(50)
        right_layout.addWidget(self.keyword_input)
        
        # Content
        right_layout.addWidget(QLabel("📝 Nội dung (content):"))
        self.content_input = QTextEdit()
        self.content_input.setMinimumHeight(200)
        self.content_input.setPlaceholderText("Nhập nội dung cần thay thế...\n\nVí dụ:\n- Địa chỉ email\n- Số điện thoại\n- Địa chỉ nhà\n- Câu trả lời thường dùng")
        right_layout.addWidget(self.content_input)
        
        # Stats
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Chưa chọn snippet")
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        right_layout.addLayout(stats_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Lưu")
        self.save_btn.clicked.connect(self.save_snippet)
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")
        self.save_btn.setMinimumHeight(40)
        button_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("🗑️ Xóa")
        self.delete_btn.clicked.connect(self.delete_snippet)
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px; font-weight: bold;")
        self.delete_btn.setMinimumHeight(40)
        button_layout.addWidget(self.delete_btn)
        
        self.new_btn = QPushButton("➕ Mới")
        self.new_btn.clicked.connect(self.new_snippet)
        self.new_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; font-weight: bold;")
        self.new_btn.setMinimumHeight(40)
        button_layout.addWidget(self.new_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_snippets)
        self.export_btn.setMinimumHeight(40)
        button_layout.addWidget(self.export_btn)
        
        right_layout.addLayout(button_layout)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([350, 650])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Sẵn sàng")
        
        # Menu bar
        self.create_menu_bar()
        
        # Keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Thiết lập phím tắt"""
        # Ctrl+S: Save
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_snippet)
        
        # Ctrl+N: New
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.new_snippet)
        
        # Delete: Delete
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.delete_snippet)
        
        # Ctrl+F: Focus search
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_input.setFocus())
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("📁 File")
        
        import_action = QAction("📥 Import từ JSON", self)
        import_action.triggered.connect(self.import_snippets)
        import_action.setShortcut("Ctrl+I")
        file_menu.addAction(import_action)
        
        export_action = QAction("📤 Export ra JSON", self)
        export_action.triggered.connect(self.export_snippets)
        export_action.setShortcut("Ctrl+E")
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        backup_action = QAction("💾 Backup Database", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Thoát", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("👁️ View")
        
        stats_action = QAction("📊 Xem thống kê", self)
        stats_action.triggered.connect(self.show_stats)
        view_menu.addAction(stats_action)
        
        most_used_action = QAction("⭐ Snippets dùng nhiều nhất", self)
        most_used_action.triggered.connect(self.show_most_used)
        view_menu.addAction(most_used_action)
        
        recent_action = QAction("🕐 Snippets dùng gần đây", self)
        recent_action.triggered.connect(self.show_recent)
        view_menu.addAction(recent_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Trợ giúp")
        
        usage_action = QAction("📖 Hướng dẫn sử dụng", self)
        usage_action.triggered.connect(self.show_usage)
        help_menu.addAction(usage_action)
        
        about_action = QAction("ℹ️ Giới thiệu", self)
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
            
            # Hiển thị preview ngắn của content
            content_preview = content.replace('\n', ' ')[:50]
            if len(content) > 50:
                content_preview += "..."
            
            item_text = f"🔑 {keyword} ({usage}×) - {content_preview}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, keyword)
            
            # Tô màu theo mức độ sử dụng
            if usage > 20:
                item.setForeground(QColor("#4CAF50"))  # Xanh lá
                item.setFont(QFont("", -1, QFont.Bold))
            elif usage > 5:
                item.setForeground(QColor("#FF9800"))  # Cam
            
            self.snippet_list.addItem(item)
        
        self.total_label.setText(f"Tổng: {len(snippets)} snippets")
        self.statusBar().showMessage(f"Đã tải {len(snippets)} snippets")
    
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
            
            content_preview = content.replace('\n', ' ')[:50]
            if len(content) > 50:
                content_preview += "..."
            
            item_text = f"🔑 {keyword} ({usage}×) - {content_preview}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, keyword)
            
            # Highlight kết quả tìm kiếm
            if text.lower() in keyword.lower():
                item.setBackground(QColor("#FFF9C4"))
            
            self.snippet_list.addItem(item)
        
        self.statusBar().showMessage(f"Tìm thấy {len(results)} kết quả cho '{text}'")
    
    def on_item_selected(self, item):
        """Khi chọn một item trong list"""
        keyword = item.data(Qt.UserRole)
        # QUAN TRỌNG: Không tăng usage_count khi chỉ xem
        content = self.db.get_snippet(keyword, increment_usage=False)
        
        if content:
            self.keyword_input.setText(keyword)
            self.content_input.setPlainText(content)
            
            # Hiển thị stats
            snippets = self.db.get_all_snippets()
            for s in snippets:
                if s['keyword'] == keyword:
                    usage = s['usage_count']
                    last_used = s['last_used'] or "Chưa dùng"
                    self.stats_label.setText(f"📊 Đã dùng: {usage} lần | 🕐 Lần cuối: {last_used}")
                    self.stats_label.setStyleSheet("color: #2196F3; font-weight: bold;")
                    break
            
            self.statusBar().showMessage(f"Đang xem: {keyword}")
    
    def save_snippet(self):
        """Lưu snippet mới hoặc cập nhật"""
        keyword = self.keyword_input.text().strip()
        content = self.content_input.toPlainText().strip()
        
        # Validation
        if not keyword:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập keyword!")
            self.keyword_input.setFocus()
            return
        
        if not content:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập nội dung!")
            self.content_input.setFocus()
            return
        
        # Kiểm tra keyword hợp lệ (chỉ chứa ký tự cho phép)
        if not all(c.isalnum() or c in ['_', '.', '-'] for c in keyword):
            reply = QMessageBox.question(
                self, "Cảnh báo",
                f"Keyword '{keyword}' chứa ký tự đặc biệt.\n"
                "Nên chỉ dùng chữ, số, dấu gạch dưới (_), dấu chấm (.) hoặc gạch ngang (-).\n\n"
                "Bạn có muốn tiếp tục không?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Kiểm tra nếu keyword đã tồn tại
        existing_content = self.db.get_snippet(keyword, increment_usage=False)
        
        if existing_content:
            # Cập nhật
            reply = QMessageBox.question(
                self, "Xác nhận",
                f"Keyword '{keyword}' đã tồn tại.\n\n"
                f"Nội dung cũ:\n{existing_content[:100]}{'...' if len(existing_content) > 100 else ''}\n\n"
                "Bạn có muốn cập nhật không?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.db.update_snippet(keyword, content):
                    self.statusBar().showMessage(f"✅ Đã cập nhật: {keyword}", 3000)
                    self.load_snippets()
                    QMessageBox.information(self, "Thành công", f"Đã cập nhật snippet '{keyword}'!")
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể cập nhật!")
        else:
            # Thêm mới
            if self.db.add_snippet(keyword, content):
                self.statusBar().showMessage(f"✅ Đã thêm mới: {keyword}", 3000)
                self.load_snippets()
                QMessageBox.information(self, "Thành công", f"Đã thêm snippet '{keyword}'!")
                self.new_snippet()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể thêm mới!")
    
    def delete_snippet(self):
        """Xóa snippet"""
        keyword = self.keyword_input.text().strip()
        
        if not keyword:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn snippet để xóa!")
            return
        
        reply = QMessageBox.question(
            self, "⚠️ Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa snippet '{keyword}' không?\n\n"
            "Hành động này không thể hoàn tác!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.delete_snippet(keyword):
                self.statusBar().showMessage(f"✅ Đã xóa: {keyword}", 3000)
                self.new_snippet()
                self.load_snippets()
                QMessageBox.information(self, "Thành công", f"Đã xóa snippet '{keyword}'!")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể xóa!")
    
    def new_snippet(self):
        """Tạo snippet mới"""
        self.keyword_input.clear()
        self.content_input.clear()
        self.stats_label.setText("Chưa chọn snippet")
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")
        self.keyword_input.setFocus()
        self.statusBar().showMessage("Sẵn sàng tạo snippet mới")
    
    def export_snippets(self):
        """Export snippets ra file JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Snippets", "snippets_backup.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                import json
                data = self.db.export_to_dict()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(
                    self, "✅ Thành công", 
                    f"Đã export {len(data)} snippets vào:\n{file_path}"
                )
                self.statusBar().showMessage(f"Đã export {len(data)} snippets", 5000)
            except Exception as e:
                QMessageBox.critical(self, "❌ Lỗi", f"Không thể export:\n{e}")
    
    def import_snippets(self):
        """Import snippets từ file JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Snippets", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                success, errors = self.db.import_from_dict(data)
                
                msg = f"✅ Đã import thành công: {success} snippets"
                if errors > 0:
                    msg += f"\n⚠️ Bị lỗi/trùng: {errors} snippets"
                
                QMessageBox.information(self, "Hoàn tất", msg)
                self.load_snippets()
                self.statusBar().showMessage(f"Import: {success} OK, {errors} errors", 5000)
            except Exception as e:
                QMessageBox.critical(self, "❌ Lỗi", f"Không thể import:\n{e}")
    
    def backup_database(self):
        """Backup database"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"snippets_backup_{timestamp}.db"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Backup Database", default_name, "Database Files (*.db)"
        )
        
        if file_path:
            if self.db.backup_database(file_path):
                QMessageBox.information(
                    self, "✅ Thành công",
                    f"Đã backup database vào:\n{file_path}"
                )
            else:
                QMessageBox.critical(self, "❌ Lỗi", "Không thể backup database!")
    
    def show_stats(self):
        """Hiển thị thống kê"""
        stats = self.db.get_stats()
        
        msg = f"""📊 THỐNG KÊ SNIPPETS

        📝 Tổng số snippets: {stats['total_snippets']}
        🔥 Tổng lượt sử dụng: {stats['total_usage']}
        ⭐ Snippet phổ biến nhất: {stats['most_used_keyword'] or 'N/A'}
        └─ Số lần dùng: {stats['most_used_count']}
                """
        
        QMessageBox.information(self, "📊 Thống kê", msg)
    
    def show_most_used(self):
        """Hiển thị snippets dùng nhiều nhất"""
        snippets = self.db.get_most_used(10)
        
        if not snippets:
            QMessageBox.information(self, "Thông báo", "Chưa có snippet nào được sử dụng!")
            return
        
        msg = "⭐ TOP 10 SNIPPETS DÙNG NHIỀU NHẤT:\n\n"
        for i, snippet in enumerate(snippets, 1):
            keyword = snippet['keyword']
            usage = snippet['usage_count']
            content_preview = snippet['content'][:30].replace('\n', ' ')
            msg += f"{i}. {keyword} ({usage}×) - {content_preview}...\n"
        
        QMessageBox.information(self, "⭐ Most Used", msg)
    
    def show_recent(self):
        """Hiển thị snippets dùng gần đây"""
        snippets = self.db.get_recent_snippets(10)
        
        if not snippets:
            QMessageBox.information(self, "Thông báo", "Chưa có snippet nào được sử dụng!")
            return
        
        msg = "🕐 TOP 10 SNIPPETS DÙNG GẦN ĐÂY:\n\n"
        for i, snippet in enumerate(snippets, 1):
            keyword = snippet['keyword']
            last_used = snippet['last_used']
            content_preview = snippet['content'][:30].replace('\n', ' ')
            msg += f"{i}. {keyword} - {last_used}\n   {content_preview}...\n\n"
        
        QMessageBox.information(self, "🕐 Recent", msg)
    
    def show_usage(self):
        """Hiển thị hướng dẫn sử dụng"""
        msg = """📖 HƯỚNG DẪN SỬ DỤNG TEXT EXPANDER

        🔧 CÁCH SỬ DỤNG:
        1. Thêm snippet: Nhập keyword và content, nhấn Lưu (Ctrl+S)
        2. Gõ nhanh: Gõ keyword + Space/Tab/Enter để tự động thay thế
        3. Tắt/Bật: Nhấn Ctrl+Alt+X

        💡 MẸO:
        • Keyword nên ngắn gọn, dễ nhớ (vd: cc, tel, addr)
        • Chỉ dùng chữ, số, dấu gạch dưới (_), dấu chấm (.)
        • Keyword không phân biệt hoa thường
        • Ứng dụng hoạt động ngầm, không cần mở cửa sổ quản lý

        ⌨️ PHÍM TẮT:
        • Ctrl+S: Lưu snippet
        • Ctrl+N: Tạo mới
        • Ctrl+F: Tìm kiếm
        • Delete: Xóa snippet
        • Ctrl+Q: Thoát

        🔍 TÌM KIẾM:
        Tìm kiếm theo keyword hoặc nội dung, hỗ trợ tiếng Việt có dấu.
        """
        QMessageBox.information(self, "📖 Hướng dẫn", msg)
    
    def show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        QMessageBox.about(
            self,
            "ℹ️ Giới thiệu",
            """<h2>Text Expander</h2>
            <p><b>Ứng dụng mở rộng văn bản tự động</b></p>
            <p>Giúp bạn gõ nhanh các đoạn tin nhắn, địa chỉ email, số điện thoại và nội dung thường dùng.</p>
            
            <p><b>Tính năng:</b></p>
            <ul>
            <li>✅ Tự động thay thế keyword thành content</li>
            <li>✅ Hỗ trợ tiếng Việt có dấu</li>
            <li>✅ Hoạt động với Unikey</li>
            <li>✅ Tìm kiếm thông minh</li>
            <li>✅ Thống kê sử dụng</li>
            <li>✅ Import/Export JSON</li>
            </ul>
            
            <p><b>Phiên bản:</b> 2.0 (Improved)</p>
            <p><b>Hotkey:</b> Ctrl+Alt+X để bật/tắt</p>
            
            <p><i>Tương thích với Unikey và các bộ gõ tiếng Việt</i></p>
            """
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = SnippetManager()
    window.show()
    sys.exit(app.exec())