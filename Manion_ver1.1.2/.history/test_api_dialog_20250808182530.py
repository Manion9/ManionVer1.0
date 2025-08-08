#!/usr/bin/env python3
"""
API 설정 다이얼로그 테스트
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

def show_api_settings():
    """API 키 설정 창 테스트"""
    root = tk.Tk()
    root.withdraw()  # 메인 창 숨김
    
    settings_window = tk.Toplevel(root)
    settings_window.title("🔑 API 키 설정 (테스트)")
    settings_window.geometry("600x400")
    settings_window.resizable(False, False)
    
    # 창을 화면 중앙에 배치
    settings_window.transient(root)
    settings_window.grab_set()
    
    # 현재 상태 확인
    current_key = os.getenv("OPENAI_API_KEY", "")
    key_status = "✅ 설정됨" if current_key else "❌ 설정 안됨"
    
    # 안내 텍스트
    info_text = f"""
🔑 API 키 설정 상태: {key_status}

🎯 GPT Vision으로 이미지를 인식하려면 OpenAI API 키가 필요합니다.

📋 사용법:
1. 아래 입력창에 OpenAI API 키를 붙여넣으세요
2. "✅ 설정 완료" 버튼을 클릭하세요
3. 이미지를 업로드하고 GPT1(인식) 노드를 클릭하세요

⚠️ 주의: API 키는 프로그램 실행 중에만 저장됩니다.
"""
    
    info_label = tk.Label(settings_window, text=info_text, justify=tk.LEFT, anchor="nw")
    info_label.pack(fill=tk.BOTH, padx=20, pady=10)
    
    # API 키 입력
    key_frame = ttk.Frame(settings_window)
    key_frame.pack(fill=tk.X, padx=20, pady=5)
    
    ttk.Label(key_frame, text="OpenAI API 키 (전체 붙여넣기):").pack(anchor="w")
    key_entry = ttk.Entry(key_frame, width=80, font=("Consolas", 9))
    key_entry.pack(fill=tk.X, pady=5)
    
    # 현재 설정된 키가 있으면 전체 표시
    if current_key:
        key_entry.insert(0, current_key)
        
    # 안내 텍스트
    help_label = ttk.Label(key_frame, text="예: sk-proj-HjXZnJnXcZRGH7co0aHVVV8Tn5ea893E3pLWQ...", 
                          foreground="gray", font=("Arial", 8))
    help_label.pack(anchor="w", pady=(2, 0))
    
    # 함수 정의
    def save_key():
        key = key_entry.get().strip()
        if not key:
            messagebox.showwarning("경고", "API 키를 입력해주세요")
            return
            
        if not (key.startswith("sk-") or key.startswith("sk_")):
            messagebox.showerror("오류", "올바른 OpenAI API 키를 입력하세요\n(sk-proj- 또는 sk- 로 시작하는 전체 키)")
            return
        
        # 메모리에 API 키 저장
        os.environ["OPENAI_API_KEY"] = key
        
        # 성공 메시지
        messagebox.showinfo("설정 완료", 
            f"✅ API 키가 성공적으로 설정되었습니다!\n\n"
            f"📋 설정된 키: {key[:15]}...{key[-10:]}\n\n"
            f"🚀 이제 이미지를 업로드하고 GPT Vision 인식을 사용할 수 있습니다.")
        
        settings_window.destroy()
        root.quit()
    
    def test_key():
        key = key_entry.get().strip()
        if key and (key.startswith("sk-") or key.startswith("sk_")):
            os.environ["OPENAI_API_KEY"] = key
            messagebox.showinfo("테스트 완료", 
                f"API 키가 설정되었습니다!\n\n"
                f"이제 이미지를 업로드하고 GPT1(인식) 노드를 클릭해보세요.\n\n"
                f"키: {key[:15]}...{key[-10:]}")
        else:
            messagebox.showwarning("경고", "올바른 OpenAI API 키를 먼저 입력하세요")
    
    # 버튼 프레임 및 버튼들
    btn_frame = ttk.Frame(settings_window)
    btn_frame.pack(fill=tk.X, padx=20, pady=20)
    
    save_btn = ttk.Button(btn_frame, text="✅ 설정 완료", command=save_key)
    save_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    test_btn = ttk.Button(btn_frame, text="🧪 연결 테스트", command=test_key)
    test_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    cancel_btn = ttk.Button(btn_frame, text="❌ 취소", 
                           command=lambda: (settings_window.destroy(), root.quit()))
    cancel_btn.pack(side=tk.RIGHT)
    
    # 엔터 키로 설정 완료
    key_entry.bind('<Return>', lambda e: save_key())
    
    root.mainloop()

if __name__ == "__main__":
    show_api_settings()
