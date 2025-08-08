#!/usr/bin/env python3
"""
Manimator Desktop GUI Application
브라우저 없이 사용할 수 있는 독립적인 데스크톱 애플리케이션
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import os
import base64
from typing import Optional

class ManimatorDesktopApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎬 Manimator Desktop - 편집 가능한 애니메이션 생성기")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 상태 변수
        self.session_state = {}
        self.current_step = 1
        self.edit_mode = False
        self.selected_file = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="🎬 Manimator Desktop", 
                               font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 설명
        desc_label = ttk.Label(main_frame, 
                              text="손글씨, PDF, 텍스트를 Manim 애니메이션으로 변환하는 데스크톱 앱",
                              font=('Arial', 12))
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # 좌측 패널: 입력 및 설정
        input_frame = ttk.LabelFrame(main_frame, text="📁 입력 및 설정", padding="10")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 입력 방식 선택
        ttk.Label(input_frame, text="입력 방식:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.input_method = tk.StringVar(value="handwriting")
        ttk.Radiobutton(input_frame, text="✍️ 손글씨 이미지/PDF", 
                       variable=self.input_method, value="handwriting").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(input_frame, text="📄 PDF 문서", 
                       variable=self.input_method, value="pdf").grid(row=2, column=0, sticky=tk.W)
        ttk.Radiobutton(input_frame, text="📝 텍스트 입력", 
                       variable=self.input_method, value="text").grid(row=3, column=0, sticky=tk.W)
        
        # 파일 선택
        ttk.Label(input_frame, text="").grid(row=4, column=0, pady=(10, 0))
        ttk.Label(input_frame, text="파일 선택:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        file_frame = ttk.Frame(input_frame)
        file_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
        self.file_entry.grid(row=0, column=0, padx=(0, 5))
        
        self.browse_btn = ttk.Button(file_frame, text="찾아보기", command=self.browse_file)
        self.browse_btn.grid(row=0, column=1)
        
        # 텍스트 입력 (텍스트 방식일 때)
        ttk.Label(input_frame, text="텍스트 입력:").grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        self.text_input = scrolledtext.ScrolledText(input_frame, height=8, width=50)
        self.text_input.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 편집 모드 설정
        self.edit_mode_var = tk.BooleanVar()
        self.edit_checkbox = ttk.Checkbutton(input_frame, 
                                           text="✏️ 편집 모드 (각 단계에서 편집 가능)",
                                           variable=self.edit_mode_var)
        self.edit_checkbox.grid(row=9, column=0, sticky=tk.W, pady=(10, 0))
        
        # 생성 버튼
        self.generate_btn = ttk.Button(input_frame, text="🚀 애니메이션 생성", 
                                     command=self.start_generation, style='Accent.TButton')
        self.generate_btn.grid(row=10, column=0, pady=(20, 0))
        
        # 우측 패널: 편집 및 결과
        result_frame = ttk.LabelFrame(main_frame, text="📝 편집 및 결과", padding="10")
        result_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 진행 상태
        self.progress_label = ttk.Label(result_frame, text="대기 중...", font=('Arial', 12, 'bold'))
        self.progress_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 진행바
        self.progress_bar = ttk.Progressbar(result_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 편집 영역 (조건부 표시)
        self.edit_frame = ttk.LabelFrame(result_frame, text="편집 영역", padding="10")
        
        self.step_label = ttk.Label(self.edit_frame, text="1단계: 입력 내용", font=('Arial', 11, 'bold'))
        self.step_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        self.edit_content = scrolledtext.ScrolledText(self.edit_frame, height=15, width=70)
        self.edit_content.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # 편집 버튼들
        button_frame = ttk.Frame(self.edit_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(10, 0))
        
        self.save_btn = ttk.Button(button_frame, text="✅ 편집 완료 후 다음 단계", 
                                 command=self.save_edit, style='Accent.TButton')
        self.save_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.reset_btn = ttk.Button(button_frame, text="🔄 초기값으로 되돌리기", 
                                  command=self.reset_edit)
        self.reset_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.close_edit_btn = ttk.Button(button_frame, text="❌ 편집 취소", 
                                       command=self.close_edit)
        self.close_edit_btn.grid(row=0, column=2)
        
        # 결과 영역
        self.result_text = scrolledtext.ScrolledText(result_frame, height=10, width=70)
        self.result_text.grid(row=3, column=0, columnspan=3, pady=(20, 0))
        
        # 그리드 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        input_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(1, weight=1)
        result_frame.rowconfigure(1, weight=1)
        
        # 초기에는 편집 영역 숨김
        self.hide_edit_panel()
        
    def browse_file(self):
        """파일 선택 대화상자"""
        input_method = self.input_method.get()
        
        if input_method == "handwriting":
            filetypes = [("이미지 파일", "*.png *.jpg *.jpeg *.pdf"), ("모든 파일", "*.*")]
        elif input_method == "pdf":
            filetypes = [("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
        else:
            return
            
        filename = filedialog.askopenfilename(
            title="파일 선택",
            filetypes=filetypes
        )
        
        if filename:
            self.file_path_var.set(filename)
            self.selected_file = filename
            
    def show_edit_panel(self):
        """편집 패널 표시"""
        self.edit_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
    def hide_edit_panel(self):
        """편집 패널 숨김"""
        self.edit_frame.grid_remove()
        
    def update_progress(self, text: str, show_bar: bool = False):
        """진행 상태 업데이트"""
        self.progress_label.config(text=text)
        if show_bar:
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
        self.root.update()
        
    def mock_handwriting_recognition(self, file_path: str) -> str:
        """GPT Vision 원시 인식 모킹"""
        return f"""손글씨 인식 결과 ({os.path.basename(file_path)}):

제목: 이차방정식의 해법

내용:
- 이차방정식: ax² + bx + c = 0 (a ≠ 0)
- 근의 공식: x = (-b ± √(b²-4ac)) / 2a
- 판별식: D = b² - 4ac
  * D > 0: 서로 다른 두 실근
  * D = 0: 중근 (하나의 실근)
  * D < 0: 허근

예제: x² - 5x + 6 = 0
해: x = (5 ± √(25-24))/2 = (5 ± 1)/2
따라서 x = 3 또는 x = 2"""

    def mock_scene_generation(self, content: str) -> str:
        """스토리보드 생성 모킹"""
        return f"""
**Topic**: {content[:50]}...

**Key Points**:
* 핵심 개념 1: 이차방정식의 정의와 일반형
* 핵심 개념 2: 근의 공식 유도 과정 (완전제곱식 활용)
* 핵심 개념 3: 판별식을 통한 해의 개수 판정
* 핵심 개념 4: 실제 예제를 통한 해법 적용

**Visual Elements**:
* 단계별 애니메이션으로 근의 공식 유도
* 그래프를 통한 해의 기하학적 의미 표현
* 판별식에 따른 포물선 변화 시각화

**Style**: 3Blue1Brown 스타일, 수학적 엄밀성과 직관적 이해의 조화
"""

    def mock_code_generation(self, scene_description: str) -> str:
        """Manim 코드 생성 모킹"""
        return '''from manim import *

class QuadraticEquationSolver(Scene):
    def construct(self):
        # 제목 생성
        title = Text("이차방정식의 해법", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        
        # 일반형 소개
        general_form = MathTex("ax^2 + bx + c = 0", font_size=40)
        condition = Text("(a ≠ 0)", font_size=24).next_to(general_form, RIGHT)
        
        self.play(Write(general_form), Write(condition))
        self.wait(2)
        
        # 근의 공식
        quadratic_formula = MathTex(
            "x = \\\\frac{-b \\\\pm \\\\sqrt{b^2 - 4ac}}{2a}",
            font_size=36,
            color=GREEN
        )
        quadratic_formula.next_to(general_form, DOWN, buff=1)
        
        self.play(Write(quadratic_formula))
        self.wait(2)
        
        # 예제 해결
        example = MathTex("x^2 - 5x + 6 = 0", font_size=36)
        example.to_edge(DOWN)
        
        self.play(Write(example))
        self.wait(1)
        
        # 해 계산
        solution = MathTex("x = 3", "\\\\text{ 또는 }", "x = 2", font_size=32, color=RED)
        solution.next_to(example, DOWN)
        
        self.play(Write(solution))
        self.wait(3)
        
        # 정리
        self.play(FadeOut(*self.mobjects))'''

    def start_generation(self):
        """애니메이션 생성 시작"""
        # 입력 검증
        input_method = self.input_method.get()
        edit_mode = self.edit_mode_var.get()
        
        if input_method in ["handwriting", "pdf"] and not self.selected_file:
            messagebox.showerror("오류", "파일을 선택해주세요.")
            return
            
        if input_method == "text" and not self.text_input.get(1.0, tk.END).strip():
            messagebox.showerror("오류", "텍스트를 입력해주세요.")
            return
        
        # 생성 버튼 비활성화
        self.generate_btn.config(state='disabled')
        
        # 백그라운드에서 처리
        thread = threading.Thread(target=self.generation_worker, args=(input_method, edit_mode))
        thread.daemon = True
        thread.start()
        
    def generation_worker(self, input_method: str, edit_mode: bool):
        """백그라운드 생성 작업"""
        try:
            # 1단계: 인식
            self.update_progress("1단계: 입력 내용 처리 중...", True)
            time.sleep(1)  # 실제 API 호출 시뮬레이션
            
            if input_method == "handwriting":
                recognized_content = self.mock_handwriting_recognition(self.selected_file)
            elif input_method == "pdf":
                recognized_content = f"PDF 인식 결과: {os.path.basename(self.selected_file)}"
            else:  # text
                recognized_content = self.text_input.get(1.0, tk.END).strip()
            
            self.session_state["step1_output"] = recognized_content
            
            if edit_mode:
                # 편집 모드
                self.current_step = 1
                self.edit_mode = True
                self.root.after(0, self.show_edit_step, 1, "1단계: 인식 결과 편집", recognized_content)
            else:
                # 자동 모드
                self.auto_generation_continue(recognized_content)
                
        except Exception as e:
            self.root.after(0, self.show_error, f"생성 중 오류: {str(e)}")
            
    def auto_generation_continue(self, content: str):
        """자동 모드 계속 진행"""
        try:
            # 2단계: 스토리보드 생성
            self.update_progress("2단계: 스토리보드 생성 중...", True)
            time.sleep(2)
            scene_description = self.mock_scene_generation(content)
            
            # 3단계: 코드 생성
            self.update_progress("3단계: Manim 코드 생성 중...", True)
            time.sleep(2)
            code = self.mock_code_generation(scene_description)
            
            # 4단계: 렌더링
            self.update_progress("4단계: 비디오 렌더링 중...", True)
            time.sleep(1)
            
            # 완료
            self.update_progress("✅ 생성 완료!", False)
            self.root.after(0, self.show_final_result, code, "animation_result.mp4")
            
        except Exception as e:
            self.root.after(0, self.show_error, f"자동 생성 중 오류: {str(e)}")
            
    def show_edit_step(self, step: int, title: str, content: str):
        """편집 단계 표시"""
        self.current_step = step
        self.step_label.config(text=title)
        self.edit_content.delete(1.0, tk.END)
        self.edit_content.insert(1.0, content)
        self.show_edit_panel()
        self.update_progress(f"편집 모드: {title}", False)
        self.generate_btn.config(state='normal')
        
    def save_edit(self):
        """편집 저장 및 다음 단계"""
        try:
            edited_content = self.edit_content.get(1.0, tk.END).strip()
            
            if self.current_step == 1:
                # 1단계 → 2단계
                self.session_state["step1_output"] = edited_content
                self.update_progress("2단계: 스토리보드 생성 중...", True)
                
                def generate_step2():
                    scene_description = self.mock_scene_generation(edited_content)
                    self.session_state["step2_output"] = scene_description
                    self.root.after(0, self.show_edit_step, 2, "2단계: 스토리보드 편집", scene_description)
                
                thread = threading.Thread(target=generate_step2)
                thread.daemon = True
                thread.start()
                
            elif self.current_step == 2:
                # 2단계 → 3단계
                self.session_state["step2_output"] = edited_content
                self.update_progress("3단계: Manim 코드 생성 중...", True)
                
                def generate_step3():
                    code = self.mock_code_generation(edited_content)
                    self.session_state["step3_output"] = code
                    self.root.after(0, self.show_edit_step, 3, "3단계: Manim 코드 편집", code)
                
                thread = threading.Thread(target=generate_step3)
                thread.daemon = True
                thread.start()
                
            elif self.current_step == 3:
                # 3단계 → 렌더링
                self.session_state["step3_output"] = edited_content
                self.update_progress("4단계: 비디오 렌더링 중...", True)
                
                def final_render():
                    time.sleep(1)  # 렌더링 시뮬레이션
                    self.root.after(0, self.show_final_result, edited_content, "animation_result.mp4")
                
                thread = threading.Thread(target=final_render)
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            self.show_error(f"편집 저장 중 오류: {str(e)}")
            
    def reset_edit(self):
        """편집 내용 초기화"""
        if self.current_step == 1:
            original = self.session_state.get("step1_output", "")
        elif self.current_step == 2:
            original = self.session_state.get("step2_output", "")
        elif self.current_step == 3:
            original = self.session_state.get("step3_output", "")
        else:
            original = ""
            
        self.edit_content.delete(1.0, tk.END)
        self.edit_content.insert(1.0, original)
        
    def close_edit(self):
        """편집 취소"""
        self.hide_edit_panel()
        self.edit_mode = False
        self.update_progress("편집이 취소되었습니다.", False)
        self.generate_btn.config(state='normal')
        
    def show_final_result(self, code: str, video_path: str):
        """최종 결과 표시"""
        self.hide_edit_panel()
        self.update_progress("✅ 애니메이션 생성 완료!", False)
        
        result = f"""🎉 애니메이션 생성이 완료되었습니다!

📹 비디오 파일: {video_path}
📄 생성된 Manim 코드:

{code}

💡 실제 환경에서는 비디오 파일이 생성되고 자동으로 재생됩니다."""
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, result)
        self.generate_btn.config(state='normal')
        
    def show_error(self, error_msg: str):
        """오류 표시"""
        self.update_progress(f"❌ 오류 발생", False)
        messagebox.showerror("오류", error_msg)
        self.generate_btn.config(state='normal')
        
    def run(self):
        """앱 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ManimatorDesktopApp()
    app.run()
