#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Type Test - Tự động gõ text vào vị trí con trỏ
"""

import time
from pynput.keyboard import Controller, Key

def auto_type(text, countdown=5):
    """
    Tự động gõ text vào vị trí con trỏ đang focus
    
    Args:
        text: Text cần gõ
        countdown: Số giây countdown (default 5)
    """
    print("=" * 60)
    print("AUTO TYPE TEST")
    print("=" * 60)
    print(f"\nSẽ gõ: '{text}'")
    print(f"\nCountdown {countdown} giây...")
    print("👉 Click vào ô input bất kỳ (Notepad, browser, etc.)")
    print()
    
    # Countdown
    for i in range(countdown, 0, -1):
        print(f"   {i}...", flush=True)
        time.sleep(1)
    
    print("\n🎬 BẮT ĐẦU GÕ!\n")
    
    controller = Controller()
    
    try:
        # Gõ từng ký tự
        for i, char in enumerate(text):
            try:
                if char == '\n':
                    controller.press(Key.enter)
                    controller.release(Key.enter)
                    print(f"   [{i+1}/{len(text)}] Enter")
                else:
                    controller.press(char)
                    controller.release(char)
                    print(f"   [{i+1}/{len(text)}] '{char}'")
                
                time.sleep(0.01)  # Delay nhỏ giữa các ký tự
                
            except Exception as e:
                print(f"\n❌ LỖI khi gõ ký tự '{char}': {e}")
                return False
        
        print("\n✅ HOÀN TẤT!")
        print(f"Đã gõ {len(text)} ký tự")
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI NGHIÊM TRỌNG: {e}")
        return False

def test_backspace(count=5, countdown=5):
    """
    Test phím Backspace
    
    Args:
        count: Số lần nhấn Backspace
        countdown: Số giây countdown
    """
    print("=" * 60)
    print("BACKSPACE TEST")
    print("=" * 60)
    print(f"\nSẽ nhấn Backspace {count} lần")
    print(f"\nCountdown {countdown} giây...")
    print("👉 Gõ một vài chữ trong Notepad, sau đó để con trỏ ở cuối")
    print()
    
    # Countdown
    for i in range(countdown, 0, -1):
        print(f"   {i}...", flush=True)
        time.sleep(1)
    
    print("\n🎬 BẮT ĐẦU XÓA!\n")
    
    controller = Controller()
    
    try:
        for i in range(count):
            controller.press(Key.backspace)
            controller.release(Key.backspace)
            print(f"   [{i+1}/{count}] Backspace")
            time.sleep(0.1)
        
        print("\n✅ HOÀN TẤT!")
        print(f"Đã nhấn Backspace {count} lần")
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        return False

def test_replace(old_text, new_text, countdown=5):
    """
    Test xóa và thay thế text (giống app thật)
    
    Args:
        old_text: Text cũ (để biết xóa bao nhiêu ký tự)
        new_text: Text mới sẽ gõ vào
        countdown: Số giây countdown
    """
    print("=" * 60)
    print("REPLACE TEST (Giống App Thật)")
    print("=" * 60)
    print(f"\n1. Gõ text: '{old_text}'")
    print(f"2. Xóa {len(old_text)} ký tự")
    print(f"3. Gõ text mới: '{new_text}'")
    print(f"\nCountdown {countdown} giây...")
    print("👉 Click vào ô input")
    print()
    
    # Countdown
    for i in range(countdown, 0, -1):
        print(f"   {i}...", flush=True)
        time.sleep(1)
    
    print("\n🎬 BẮT ĐẦU!\n")
    
    controller = Controller()
    
    try:
        # Step 1: Gõ old_text
        print(f"📝 Step 1: Gõ '{old_text}'...")
        for char in old_text:
            controller.press(char)
            controller.release(char)
            time.sleep(0.01)
        print(f"✅ Step 1: Đã gõ '{old_text}'")
        
        time.sleep(0.5)
        
        # Step 2: Xóa old_text bằng Backspace
        print(f"\n⌫ Step 2: Xóa {len(old_text)} ký tự...")
        for i in range(len(old_text)):
            controller.press(Key.backspace)
            controller.release(Key.backspace)
            time.sleep(0.01)
        print(f"✅ Step 2: Đã xóa {len(old_text)} ký tự")
        
        time.sleep(0.5)
        
        # Step 3: Gõ new_text
        print(f"\n⌨️ Step 3: Gõ '{new_text}'...")
        for char in new_text:
            controller.press(char)
            controller.release(char)
            time.sleep(0.01)
        print(f"✅ Step 3: Đã gõ '{new_text}'")
        
        print("\n✅ ✅ ✅ HOÀN TẤT! ✅ ✅ ✅")
        print(f"'{old_text}' → '{new_text}'")
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== MAIN ====================

if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 60)
    print("AUTO TYPE TEST SUITE")
    print("=" * 60)
    print("\nChọn test:")
    print("  1. Auto Type - Tự động gõ text")
    print("  2. Backspace Test - Test xóa")
    print("  3. Replace Test - Test thay thế (giống app thật)")
    print("  4. Quick Test t1 → content")
    print()
    
    choice = input("Chọn (1-4): ").strip()
    
    if choice == "1":
        print("\n--- AUTO TYPE TEST ---")
        custom_text = input("Nhập text muốn gõ (Enter = 'Hello World'): ").strip()
        if not custom_text:
            custom_text = "Hello World"
        
        result = auto_type(custom_text)
        
        if result:
            print("\n✅ Test PASSED - Controller hoạt động tốt!")
        else:
            print("\n❌ Test FAILED - Controller có vấn đề!")
            print("\nGiải pháp:")
            print("  - Chạy với quyền administrator/sudo")
            print("  - Check antivirus/security software")
    
    elif choice == "2":
        print("\n--- BACKSPACE TEST ---")
        count = input("Số lần Backspace (Enter = 5): ").strip()
        count = int(count) if count else 5
        
        result = test_backspace(count)
        
        if result:
            print("\n✅ Test PASSED - Backspace hoạt động tốt!")
        else:
            print("\n❌ Test FAILED - Backspace có vấn đề!")
    
    elif choice == "3":
        print("\n--- REPLACE TEST ---")
        old_text = input("Text cũ (Enter = 't1'): ").strip()
        if not old_text:
            old_text = "t1"
        
        new_text = input("Text mới (Enter = 'This is t1 content'): ").strip()
        if not new_text:
            new_text = "This is t1 content - TEST WORKS!"
        
        result = test_replace(old_text, new_text)
        
        if result:
            print("\n✅ Test PASSED - Replace hoạt động tốt!")
            print("\n🎉 App sẽ hoạt động bình thường!")
        else:
            print("\n❌ Test FAILED - Replace có vấn đề!")
            print("\n⚠️ App sẽ KHÔNG thể thay thế text!")
    
    elif choice == "4":
        print("\n--- QUICK TEST: t1 → content ---")
        print("Test chính xác như app sẽ làm:\n")
        result = test_replace("t1", "This is t1 content - TEST WORKS!")
        
        if result:
            print("\n✅ ✅ ✅ PERFECT! App sẽ hoạt động! ✅ ✅ ✅")
        else:
            print("\n❌ ❌ ❌ FAILED! App sẽ KHÔNG hoạt động! ❌ ❌ ❌")
            print("\nCần:")
            print("  1. Chạy với quyền administrator/sudo")
            print("  2. Hoặc check antivirus/security software")
    
    else:
        print("\n❌ Lựa chọn không hợp lệ!")
        sys.exit(1)
    
    print("\n" + "=" * 60)