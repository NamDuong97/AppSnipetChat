import sqlite3
import os
from typing import Optional, List, Tuple

class Database:
    def __init__(self, db_path="snippets.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Tạo kết nối đến database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Để truy cập theo tên cột
        return conn
    
    def init_database(self):
        """Khởi tạo database nếu chưa tồn tại"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Bảng snippets
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 0,
            last_used TIMESTAMP
        )
        ''')
        
        # Tạo index cho tìm kiếm nhanh
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON snippets(keyword)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage ON snippets(usage_count)')
        
        conn.commit()
        conn.close()
        print(f"Database initialized: {self.db_path}")
    
    def add_snippet(self, keyword: str, content: str) -> bool:
        """Thêm snippet mới"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO snippets (keyword, content) VALUES (?, ?)",
                (keyword, content)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            print(f"Keyword '{keyword}' đã tồn tại")
            return False
    
    def get_snippet(self, keyword: str) -> Optional[str]:
        """Lấy content theo keyword và tăng usage count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Lấy content
        cursor.execute(
            "SELECT content FROM snippets WHERE keyword = ?",
            (keyword,)
        )
        result = cursor.fetchone()
        
        if result:
            # Tăng usage count và cập nhật last_used
            cursor.execute('''
                UPDATE snippets 
                SET usage_count = usage_count + 1,
                    last_used = CURRENT_TIMESTAMP
                WHERE keyword = ?
            ''', (keyword,))
            conn.commit()
            content = result['content']
        else:
            content = None
        
        conn.close()
        return content
    
    def update_snippet(self, keyword: str, content: str) -> bool:
        """Cập nhật snippet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE snippets SET content = ? WHERE keyword = ?",
            (content, keyword)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def delete_snippet(self, keyword: str) -> bool:
        """Xóa snippet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM snippets WHERE keyword = ?", (keyword,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def get_all_snippets(self) -> List[Tuple]:
        """Lấy tất cả snippets (cho hiển thị)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT keyword, content, usage_count, 
                   datetime(last_used, 'localtime') as last_used
            FROM snippets 
            ORDER BY usage_count DESC, keyword
        ''')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_snippets(self, search_text: str) -> List[Tuple]:
        """Tìm kiếm snippets (trong keyword và content)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f"%{search_text}%"
        cursor.execute('''
            SELECT keyword, content, usage_count
            FROM snippets 
            WHERE keyword LIKE ? OR content LIKE ?
            ORDER BY usage_count DESC
        ''', (search_pattern, search_pattern))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_most_used(self, limit=10):
        """Lấy snippets dùng nhiều nhất"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT keyword, content, usage_count
            FROM snippets 
            ORDER BY usage_count DESC 
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def backup_database(self, backup_path: str):
        """Sao lưu database"""
        import shutil
        shutil.copy2(self.db_path, backup_path)
        print(f"Database backed up to: {backup_path}")