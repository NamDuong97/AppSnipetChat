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
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Khởi tạo database nếu chưa tồn tại"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Bảng snippets
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE NOT NULL COLLATE NOCASE,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 0,
            last_used TIMESTAMP
        )
        ''')
        
        # Tạo index cho tìm kiếm nhanh
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON snippets(keyword COLLATE NOCASE)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage ON snippets(usage_count DESC)')
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized: {self.db_path}")
    
    def add_snippet(self, keyword: str, content: str) -> bool:
        """Thêm snippet mới"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Trim keyword
            keyword = keyword.strip()
            
            cursor.execute(
                "INSERT INTO snippets (keyword, content) VALUES (?, ?)",
                (keyword, content)
            )
            conn.commit()
            conn.close()
            print(f"✅ Added snippet: '{keyword}'")
            return True
        except sqlite3.IntegrityError:
            print(f"❌ Keyword '{keyword}' already exists")
            return False
        except Exception as e:
            print(f"❌ Error adding snippet: {e}")
            return False
    
    def get_snippet(self, keyword: str, increment_usage: bool = True) -> Optional[str]:
        """
        Lấy content theo keyword
        
        Args:
            keyword: Keyword cần tìm
            increment_usage: Có tăng usage count không (mặc định True)
        
        Returns:
            Content của snippet hoặc None nếu không tìm thấy
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Trim keyword
            keyword = keyword.strip()
            
            # Tìm kiếm không phân biệt hoa thường
            cursor.execute(
                "SELECT content FROM snippets WHERE keyword = ? COLLATE NOCASE",
                (keyword,)
            )
            result = cursor.fetchone()
            
            if result:
                content = result['content']
                
                # Tăng usage count nếu cần
                if increment_usage:
                    cursor.execute('''
                        UPDATE snippets 
                        SET usage_count = usage_count + 1,
                            last_used = CURRENT_TIMESTAMP
                        WHERE keyword = ? COLLATE NOCASE
                    ''', (keyword,))
                    conn.commit()
                
                return content
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error getting snippet: {e}")
            return None
        finally:
            conn.close()
    
    def update_snippet(self, keyword: str, content: str) -> bool:
        """Cập nhật snippet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            keyword = keyword.strip()
            
            cursor.execute(
                "UPDATE snippets SET content = ? WHERE keyword = ? COLLATE NOCASE",
                (content, keyword)
            )
            updated = cursor.rowcount > 0
            conn.commit()
            
            if updated:
                print(f"✅ Updated snippet: '{keyword}'")
            else:
                print(f"❌ Snippet not found: '{keyword}'")
            
            return updated
        except Exception as e:
            print(f"❌ Error updating snippet: {e}")
            return False
        finally:
            conn.close()
    
    def delete_snippet(self, keyword: str) -> bool:
        """Xóa snippet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            keyword = keyword.strip()
            
            cursor.execute("DELETE FROM snippets WHERE keyword = ? COLLATE NOCASE", (keyword,))
            deleted = cursor.rowcount > 0
            conn.commit()
            
            if deleted:
                print(f"✅ Deleted snippet: '{keyword}'")
            else:
                print(f"❌ Snippet not found: '{keyword}'")
            
            return deleted
        except Exception as e:
            print(f"❌ Error deleting snippet: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_snippets(self) -> List[Tuple]:
        """Lấy tất cả snippets (cho hiển thị)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT keyword, content, usage_count, 
                       datetime(last_used, 'localtime') as last_used
                FROM snippets 
                ORDER BY usage_count DESC, keyword COLLATE NOCASE
            ''')
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"❌ Error getting all snippets: {e}")
            return []
        finally:
            conn.close()
    
    def search_snippets(self, search_text: str) -> List[Tuple]:
        """
        Tìm kiếm snippets (trong keyword và content)
        
        Returns list sorted by relevance:
        1. Exact keyword match
        2. Keyword starts with search_text
        3. Keyword contains search_text
        4. Content contains search_text
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            search_text = search_text.strip()
            search_pattern = f"%{search_text}%"
            
            cursor.execute('''
                SELECT keyword, content, usage_count,
                       CASE 
                           WHEN keyword = ? COLLATE NOCASE THEN 1
                           WHEN keyword LIKE ? COLLATE NOCASE THEN 2
                           WHEN keyword LIKE ? COLLATE NOCASE THEN 3
                           ELSE 4
                       END as relevance
                FROM snippets 
                WHERE keyword LIKE ? COLLATE NOCASE OR content LIKE ?
                ORDER BY relevance, usage_count DESC, keyword COLLATE NOCASE
            ''', (search_text, f"{search_text}%", search_pattern, search_pattern, search_pattern))
            
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"❌ Error searching snippets: {e}")
            return []
        finally:
            conn.close()
    
    def get_most_used(self, limit=10) -> List[Tuple]:
        """Lấy snippets dùng nhiều nhất"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT keyword, content, usage_count
                FROM snippets 
                WHERE usage_count > 0
                ORDER BY usage_count DESC, keyword COLLATE NOCASE
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"❌ Error getting most used snippets: {e}")
            return []
        finally:
            conn.close()
    
    def get_recent_snippets(self, limit=10) -> List[Tuple]:
        """Lấy snippets được dùng gần đây nhất"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT keyword, content, usage_count,
                       datetime(last_used, 'localtime') as last_used
                FROM snippets 
                WHERE last_used IS NOT NULL
                ORDER BY last_used DESC
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"❌ Error getting recent snippets: {e}")
            return []
        finally:
            conn.close()
    
    def get_stats(self) -> dict:
        """Lấy thống kê về database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Tổng số snippets
            cursor.execute("SELECT COUNT(*) as total FROM snippets")
            total = cursor.fetchone()['total']
            
            # Tổng lượt sử dụng
            cursor.execute("SELECT SUM(usage_count) as total_usage FROM snippets")
            total_usage = cursor.fetchone()['total_usage'] or 0
            
            # Snippet được dùng nhiều nhất
            cursor.execute('''
                SELECT keyword, usage_count 
                FROM snippets 
                ORDER BY usage_count DESC 
                LIMIT 1
            ''')
            most_used = cursor.fetchone()
            
            return {
                'total_snippets': total,
                'total_usage': total_usage,
                'most_used_keyword': most_used['keyword'] if most_used else None,
                'most_used_count': most_used['usage_count'] if most_used else 0
            }
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {
                'total_snippets': 0,
                'total_usage': 0,
                'most_used_keyword': None,
                'most_used_count': 0
            }
        finally:
            conn.close()
    
    def backup_database(self, backup_path: str) -> bool:
        """Sao lưu database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Error backing up database: {e}")
            return False
    
    def import_from_dict(self, snippets_dict: dict) -> tuple:
        """
        Import snippets từ dictionary
        
        Args:
            snippets_dict: {keyword: content, ...}
        
        Returns:
            (success_count, error_count)
        """
        success = 0
        errors = 0
        
        for keyword, content in snippets_dict.items():
            if self.add_snippet(keyword, content):
                success += 1
            else:
                errors += 1
        
        return (success, errors)
    
    def export_to_dict(self) -> dict:
        """Export tất cả snippets ra dictionary"""
        snippets = self.get_all_snippets()
        result = {}
        
        for snippet in snippets:
            result[snippet['keyword']] = snippet['content']
        
        return result