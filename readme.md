# Text Expander - Ứng dụng mở rộng văn bản tự động

## 📖 Giới thiệu

Text Expander là ứng dụng giúp bạn gõ nhanh các đoạn văn bản thường dùng bằng cách tự động thay thế từ khóa ngắn (keyword) thành nội dung đầy đủ (content).

**Ví dụ:**
- Gõ `cc` + Space → Tự động thay thế thành "Cảm ơn bạn đã liên hệ!"
- Gõ `addr` + Space → Thay thế thành địa chỉ đầy đủ của bạn
- Gõ `email` + Space → Thay thế thành địa chỉ email của bạn

## ✨ Tính năng

### ✅ Đã cải thiện trong phiên bản mới:

1. **Tương thích hoàn toàn với Unikey**
   - Xử lý debounce để tránh xung đột với bộ gõ tiếng Việt
   - Không bị lỗi khi gõ các ký tự có dấu

2. **Buffer management được cải thiện**
   - Buffer tự động xóa sau trigger key
   - Timeout tự động (5 giây không gõ sẽ xóa buffer)
   - Chỉ lưu các ký tự hợp lệ (chữ, số, _, ., -)

3. **Tìm kiếm thông minh**
   - Tìm kiếm không phân biệt hoa thường
   - Tìm kiếm bỏ dấu tiếng Việt
   - Tìm kiếm mờ (fuzzy search)
   - Sắp xếp theo độ liên quan

4. **Thay thế chính xác**
   - Xóa đúng số ký tự keyword
   - Delay phù hợp giữa các thao tác
   - Xử lý Unicode đúng cách

5. **Logging chi tiết**
   - Log tất cả hoạt động vào file `text_expander.log`
   - Dễ dàng debug và theo dõi

## 🚀 Cài đặt

### Yêu cầu:
```bash
pip install pynput PySide6 sqlite3
```

### Cấu trúc thư mục:
```
text-expander/
├── main.py                 # File chính (chạy ứng dụng)
├── keyboard_listener.py    # Module lắng nghe bàn phím (CẢI TIẾN)
├── database.py            # Module quản lý database (CẢI TIẾN)
├── manager_gui.py         # Giao diện quản lý snippets (CẢI TIẾN)
├── snippets.db            # Database SQLite (tự động tạo)
├── text_expander.log      # File log (tự động tạo)
└── resources/
    └── icon.ico           # Icon (tùy chọn)
```

## 📝 Cách sử dụng

### 1. Khởi động ứng dụng

```bash
python main.py
```

Ứng dụng sẽ chạy ngầm trên system tray (góc dưới bên phải màn hình).

### 2. Thêm snippet

**Cách 1: Qua giao diện**
1. Click phải vào icon trên system tray
2. Chọn "📝 Mở Quản lý"
3. Nhập keyword và content
4. Nhấn "💾 Lưu" (hoặc Ctrl+S)

**Cách 2: Qua code**
```python
from database import Database
db = Database()
db.add_snippet("cc", "Cảm ơn bạn đã liên hệ!")
db.add_snippet("email", "example@gmail.com")
db.add_snippet("addr", "123 Đường ABC, Quận 1, TP.HCM")
```

### 3. Sử dụng snippet

1. Mở bất kỳ ứng dụng nào (Word, Excel, browser, notepad, v.v.)
2. Gõ keyword (ví dụ: `cc`)
3. Nhấn **Space**, **Tab** hoặc **Enter**
4. Keyword sẽ tự động được thay thế bằng content

**Ví dụ:**
```
Bạn gõ: cc[Space]
Kết quả: Cảm ơn bạn đã liên hệ!
```

### 4. Bật/tắt ứng dụng

Nhấn **Ctrl + Alt + X** để bật/tắt chức năng tự động thay thế.

## 🎯 Gợi ý keyword

### Keyword tốt:
- `cc` → Cảm ơn
- `email` → Địa chỉ email
- `tel` → Số điện thoại
- `addr` → Địa chỉ
- `sig` → Chữ ký email
- `br` → Best regards

### Keyword nên tránh:
- ❌ Quá dài: `camoncuaban`
- ❌ Có dấu cách: `cam on`
- ❌ Có ký tự đặc biệt: `cảm-ơn`
- ❌ Chỉ có 1 ký tự: `c`

### Quy tắc keyword:
- ✅ Ngắn gọn (2-10 ký tự)
- ✅ Dễ nhớ
- ✅ Chỉ dùng: chữ, số, gạch dưới (_), dấu chấm (.), gạch ngang (-)
- ✅ Không trùng với từ thông dụng

## 🐛 Xử lý lỗi

### Vấn đề: Buffer cộng dồn

**Triệu chứng:** Keyword không được xóa hết, content bị thêm vào sau keyword

**Nguyên nhân:** Buffer không được xóa đúng cách

**Đã sửa:**
- Buffer tự động xóa sau mỗi trigger key
- Buffer timeout sau 5 giây không hoạt động
- Clear buffer khi gặp ký tự đặc biệt

### Vấn đề: Không thay thế content

**Triệu chứng:** Gõ keyword + Space nhưng không có gì xảy ra

**Nguyên nhân:** 
1. Keyword không tồn tại trong database
2. Keyword bị dấu tiếng Việt
3. Ứng dụng bị tắt

**Giải pháp:**
1. Kiểm tra keyword trong giao diện quản lý
2. Dùng keyword không dấu (vd: `camoc` thay vì `cảmơn`)
3. Kiểm tra log file: `text_expander.log`
4. Nhấn Ctrl+Alt+X để bật lại

**Debug:**
```bash
# Xem log
cat text_expander.log | tail -50

# Tìm lỗi
grep "ERROR" text_expander.log
grep "NOT FOUND" text_expander.log
```

### Vấn đề: Xung đột với Unikey

**Triệu chứng:** Phải gõ 's' 2 lần mới ra chữ 's'

**Đã sửa:**
- Thêm debounce time 50ms
- Chỉ accept ký tự hợp lệ
- Bỏ qua ký tự đặc biệt từ Unikey

**Gợi ý:**
- Dùng keyword không dấu để tránh xung đột
- Ví dụ: `camoc` thay vì `cảmơn`

### Vấn đề: Ứng dụng không hoạt động

**Kiểm tra:**

1. **Ứng dụng có đang chạy không?**
   ```bash
   # Xem process
   ps aux | grep python
   ```

2. **Log có lỗi không?**
   ```bash
   tail -f text_expander.log
   ```

3. **Database có OK không?**
   ```python
   from database import Database
   db = Database()
   print(db.get_all_snippets())
   ```

4. **Thử restart:**
   - Thoát ứng dụng (click phải icon → Thoát)
   - Chạy lại: `python main.py`

## 📊 Thống kê & Quản lý

### Xem thống kê:
```python
from database import Database
db = Database()
stats = db.get_stats()
print(stats)
```

### Top snippets dùng nhiều nhất:
```python
most_used = db.get_most_used(10)
for snippet in most_used:
    print(f"{snippet['keyword']}: {snippet['usage_count']} lần")
```

### Backup database:
```python
db.backup_database("backup_20250101.db")
```

### Export/Import JSON:

**Export:**
```python
import json
data = db.export_to_dict()
with open('snippets.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

**Import:**
```python
import json
with open('snippets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
success, errors = db.import_from_dict(data)
print(f"Import: {success} OK, {errors} errors")
```

## ⌨️ Phím tắt

### Trong ứng dụng:
- **Ctrl + Alt + X**: Bật/tắt chức năng thay thế

### Trong giao diện quản lý:
- **Ctrl + S**: Lưu snippet
- **Ctrl + N**: Tạo snippet mới
- **Ctrl + F**: Tìm kiếm
- **Delete**: Xóa snippet
- **Ctrl + I**: Import từ JSON
- **Ctrl + E**: Export ra JSON
- **Ctrl + Q**: Thoát

## 🔧 Cấu hình nâng cao

### Thay đổi trigger keys:

Mở `keyboard_listener.py`, tìm dòng:
```python
self.trigger_keys = {Key.space, Key.tab, Key.enter}
```

Có thể thêm/bớt các phím trigger theo ý muốn.

### Thay đổi debounce time:

```python
self.char_debounce = 0.05  # 50ms - giảm nếu muốn responsive hơn
```

### Thay đổi buffer timeout:

```python
self.buffer_timeout = 5.0  # 5 giây - tăng nếu gõ chậm
```

## 📦 Build file .exe

Để build thành file .exe (không cần Python):

```bash
# Cài PyInstaller
pip install pyinstaller

# Build
pyinstaller main.spec

# File .exe sẽ ở trong thư mục dist/
```

## 🔍 Troubleshooting chi tiết

### Log analysis:

**Xem buffer:**
```bash
grep "Buffer:" text_expander.log
```

**Xem trigger events:**
```bash
grep "TRIGGER:" text_expander.log
```

**Xem kết quả tìm kiếm:**
```bash
grep "FOUND\|NOT FOUND" text_expander.log
```

**Xem replacement:**
```bash
grep "Replacing" text_expander.log
```

### Kiểm tra database:

```bash
sqlite3 snippets.db
sqlite> SELECT * FROM snippets;
sqlite> SELECT keyword, usage_count FROM snippets ORDER BY usage_count DESC LIMIT 10;
sqlite> .quit
```

## 🎓 Ví dụ snippets hữu ích

```python
from database import Database
db = Database()

# Email templates
db.add_snippet("hi", "Xin chào,\n\nTôi là [Tên của bạn].")
db.add_snippet("thanks", "Cảm ơn bạn đã liên hệ!\n\nTrân trọng,")
db.add_snippet("sig", "Trân trọng,\n[Tên]\n[Email]\n[SĐT]")

# Thông tin cá nhân
db.add_snippet("email", "your.email@gmail.com")
db.add_snippet("tel", "0123-456-789")
db.add_snippet("addr", "123 Đường ABC, Quận 1, TP.HCM")

# Code snippets
db.add_snippet("pyfunc", "def function_name():\n    pass")
db.add_snippet("pyclass", "class ClassName:\n    def __init__(self):\n        pass")

# Văn bản thường dùng
db.add_snippet("sorry", "Xin lỗi vì sự bất tiện này.")
db.add_snippet("confirm", "Đã nhận được yêu cầu của bạn. Chúng tôi sẽ xử lý trong 24h.")
db.add_snippet("followup", "Tôi muốn follow-up về vấn đề này.")

# Emojis
db.add_snippet("ok", "👍")
db.add_snippet("heart", "❤️")
db.add_snippet("fire", "🔥")
```

## 📞 Hỗ trợ

Nếu gặp vấn đề:

1. Kiểm tra log: `text_expander.log`
2. Kiểm tra database: `snippets.db`
3. Thử restart ứng dụng
4. Thử chạy với log level DEBUG

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa.

## 🙏 Credits

- **pynput**: Keyboard listening
- **PySide6**: GUI framework
- **SQLite**: Database

---

**Version:** 2.0 (Improved - Compatible with Unikey)
**Last Updated:** 2024