# Quick Start Guide - Text Expander

## 🚀 Bắt đầu trong 5 phút

### 1. Cài đặt dependencies

```bash
pip install pynput PySide6
```

### 2. Chạy test để kiểm tra

```bash
python test_expander.py
```

Nếu tất cả tests PASSED ✅, tiếp tục bước 3.

### 3. Khởi động ứng dụng

```bash
python main.py
```

Ứng dụng sẽ chạy ngầm trên system tray (góc dưới bên phải).

### 4. Thêm snippet đầu tiên

**Cách 1: Qua GUI**
1. Click phải vào icon trên system tray
2. Chọn "📝 Mở Quản lý"
3. Nhập:
   - Keyword: `test`
   - Content: `This is a test!`
4. Nhấn "💾 Lưu"

**Cách 2: Qua Python**
```python
from database import Database
db = Database()
db.add_snippet("test", "This is a test!")
db.add_snippet("email", "your.email@gmail.com")
db.add_snippet("tel", "0123-456-789")
```

### 5. Test ngay!

1. Mở Notepad hoặc bất kỳ text editor nào
2. Gõ: `test` + **Space**
3. Xem magic xảy ra! ✨

Keyword `test` sẽ tự động được thay thế bằng `This is a test!`

---

## 📝 Gợi ý snippets hữu ích

Copy & paste đoạn code này để tạo snippets phổ biến:

```python
from database import Database
db = Database()

# Email & Contact
db.add_snippet("email", "your.email@gmail.com")
db.add_snippet("tel", "0123-456-789")
db.add_snippet("addr", "123 Đường ABC, Quận 1, TP.HCM")

# Greetings
db.add_snippet("hi", "Xin chào,\n\nTôi là [Tên].")
db.add_snippet("thanks", "Cảm ơn bạn!\n\nTrân trọng,")
db.add_snippet("bye", "Chúc bạn một ngày tốt lành!")

# Common responses
db.add_snippet("ok", "Được rồi, tôi sẽ xử lý ngay.")
db.add_snippet("sorry", "Xin lỗi vì sự bất tiện này.")
db.add_snippet("asap", "Tôi sẽ xử lý càng sớm càng tốt.")

# Shortcuts
db.add_snippet("br", "Best regards,")
db.add_snippet("cc", "Cảm ơn bạn!")
db.add_snippet("fyi", "For your information")

print("✅ Đã thêm 12 snippets!")
```

---

## ⌨️ Phím tắt quan trọng

| Phím | Chức năng |
|------|-----------|
| **Ctrl+Alt+X** | Bật/tắt ứng dụng |
| **Ctrl+S** | Lưu snippet (trong GUI) |
| **Ctrl+N** | Tạo snippet mới (trong GUI) |
| **Ctrl+F** | Tìm kiếm (trong GUI) |

---

## 🎯 Tips & Tricks

### ✅ DO (Nên làm):
- Dùng keyword ngắn: `cc`, `tel`, `addr`
- Keyword không dấu: `camoc` thay vì `cảmơn`
- Dùng chữ thường: `email` thay vì `EMAIL`
- Test trước khi dùng nhiều

### ❌ DON'T (Không nên):
- Keyword quá dài: `xincamoncuaban`
- Keyword có dấu cách: `xin cam on`
- Keyword trùng từ thông dụng: `the`, `a`, `is`
- Keyword 1 ký tự: `a`, `b`, `c`

---

## 🐛 Troubleshooting nhanh

### Vấn đề: Không thay thế
```bash
# Kiểm tra log
tail -f text_expander.log

# Xem snippet có tồn tại không
python -c "from database import Database; db = Database(); print(db.get_all_snippets())"
```

### Vấn đề: Ứng dụng crash
```bash
# Xem log lỗi
cat text_expander.log | grep ERROR

# Restart
python main.py
```

### Vấn đề: Conflict với Unikey
- Dùng keyword không dấu
- Ví dụ: `camoc` thay vì `cảmơn`

---

## 📖 Đọc thêm

- [README.md](README.md) - Hướng dẫn đầy đủ
- [CHANGELOG.md](CHANGELOG.md) - Các cải tiến
- [test_expander.py](test_expander.py) - Test suite

---

## 💡 Ví dụ workflow

```
# Morning routine
You: hi[Space]
Output: Xin chào,

        Tôi là [Tên].

# Quick reply
You: thanks[Space]
Output: Cảm ơn bạn!

        Trân trọng,

# Share contact
You: email[Space] or tel[Space]
Output: your.email@gmail.com or 0123-456-789
```

---

## ✨ Thành công!

Bạn đã sẵn sàng! 

**Next steps:**
1. Thêm snippets cá nhân của bạn
2. Sử dụng hàng ngày
3. Xem log để debug nếu cần: `text_expander.log`

**Need help?** 
- Check README.md
- Review logs
- Run tests: `python test_expander.py`

Happy typing! 🎉