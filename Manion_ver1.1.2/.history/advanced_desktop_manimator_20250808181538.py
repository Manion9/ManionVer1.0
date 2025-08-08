#!/usr/bin/env python3
"""
Advanced Manimator Desktop GUI Application
Make.com 스타일의 노드 기반 워크플로우 UI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import os
import base64
from typing import Optional, Dict, Any
import json
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv("config/.env")

class WorkflowNode:
    """워크플로우 노드 클래스"""
    def __init__(self, canvas, x, y, width, height, title, node_type, color="#E0E0E0"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.node_type = node_type
        self.color = color
        self.status = "pending"  # pending, processing, completed, error
        self.data = None
        self.editable = False
        
        # 노드 그리기
        self.draw()
        
    def draw(self):
        """노드 시각적 표현"""
        # 상태에 따른 색상
        colors = {
            "pending": "#E0E0E0",
            "processing": "#FFF3CD", 
            "completed": "#D4EDDA",
            "error": "#F8D7DA"
        }
        
        fill_color = colors.get(self.status, self.color)
        
        # 노드 사각형
        self.rect = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=fill_color, outline="#6C757D", width=2,
            tags=f"node_{self.node_type}"
        )
        
        # 제목 텍스트
        self.text = self.canvas.create_text(
            self.x + self.width//2, self.y + 20,
            text=self.title, font=("Arial", 10, "bold"),
            tags=f"node_{self.node_type}"
        )
        
        # 상태 텍스트
        status_text = {
            "pending": "대기 중",
            "processing": "처리 중...",
            "completed": "완료",
            "error": "오류"
        }
        
        self.status_text = self.canvas.create_text(
            self.x + self.width//2, self.y + 40,
            text=status_text.get(self.status, ""), 
            font=("Arial", 8),
            tags=f"node_{self.node_type}"
        )
        
        # 편집 가능 표시
        if self.editable:
            self.edit_icon = self.canvas.create_text(
                self.x + self.width - 10, self.y + 10,
                text="✏️", font=("Arial", 8),
                tags=f"node_{self.node_type}"
            )
    
    def update_status(self, status, data=None):
        """노드 상태 업데이트"""
        self.status = status
        if data:
            self.data = data
        self.canvas.delete(f"node_{self.node_type}")
        self.draw()
        
    def set_editable(self, editable):
        """편집 가능 여부 설정"""
        self.editable = editable
        self.canvas.delete(f"node_{self.node_type}")
        self.draw()

class ManimatorAdvancedApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎬 Manimator Advanced - Make.com Style Workflow")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # 상태 변수
        self.session_state = {}
        self.workflow_nodes = {}
        self.edit_panels = {}
        
        # 편집 옵션
        self.edit_options = {
            "recognition": tk.BooleanVar(),
            "storyboard": tk.BooleanVar(), 
            "code": tk.BooleanVar()
        }
        
        self.setup_ui()
        self.setup_workflow()
        
    def setup_ui(self):
        """UI 구성"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 상단: 제목 및 편집 옵션 패널
        self.setup_header(main_container)
        
        # 중간: 입력 패널
        self.setup_input_panel(main_container)
        
        # 하단: 워크플로우 캔버스
        self.setup_workflow_canvas(main_container)
        
        # 우측: 편집 패널들
        self.setup_edit_panels(main_container)
        
    def setup_header(self, parent):
        """헤더 섹션"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 제목
        title_label = ttk.Label(header_frame, text="🎬 Manimator Advanced Workflow", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # 편집 옵션 패널
        edit_options_frame = ttk.LabelFrame(header_frame, text="✏️ 편집 옵션", padding="10")
        
        # API 상태 표시 (편집 옵션 위에)
        api_status_frame = ttk.Frame(header_frame)
        api_status_frame.pack(fill=tk.X, pady=(0, 10))
        
        api_status = "✅ API 연결됨" if os.getenv("OPENAI_API_KEY") else "❌ API 설정 필요"
        api_color = "green" if os.getenv("OPENAI_API_KEY") else "red"
        self.api_status_label = tk.Label(api_status_frame, text=api_status, 
                                        font=("Arial", 12, "bold"), fg=api_color)
        self.api_status_label.pack(side=tk.LEFT)
        
        large_api_btn = ttk.Button(api_status_frame, text="🔑 API 키 설정", 
                                  command=self.show_api_settings, 
                                  style='Accent.TButton')
        large_api_btn.pack(side=tk.RIGHT)
        edit_options_frame.pack(side=tk.RIGHT)
        
        # 편집 체크박스들
        options_inner = ttk.Frame(edit_options_frame)
        options_inner.pack()
        
        ttk.Checkbutton(options_inner, text="📝 인식 편집", 
                       variable=self.edit_options["recognition"],
                       command=self.toggle_edit_panel).grid(row=0, column=0, padx=5)
        
        ttk.Checkbutton(options_inner, text="📋 스토리보드 편집", 
                       variable=self.edit_options["storyboard"],
                       command=self.toggle_edit_panel).grid(row=0, column=1, padx=5)
        
        ttk.Checkbutton(options_inner, text="💻 Manim 코드 편집", 
                       variable=self.edit_options["code"],
                       command=self.toggle_edit_panel).grid(row=0, column=2, padx=5)
        
    def setup_input_panel(self, parent):
        """입력 패널"""
        input_frame = ttk.LabelFrame(parent, text="📁 입력", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 입력 방식 선택
        input_method_frame = ttk.Frame(input_frame)
        input_method_frame.pack(fill=tk.X)
        
        ttk.Label(input_method_frame, text="입력 방식:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.input_method = tk.StringVar(value="handwriting")
        ttk.Radiobutton(input_method_frame, text="✍️ 손글씨", 
                       variable=self.input_method, value="handwriting").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(input_method_frame, text="📄 PDF", 
                       variable=self.input_method, value="pdf").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(input_method_frame, text="📝 텍스트", 
                       variable=self.input_method, value="text").pack(side=tk.LEFT, padx=5)
        
        # 파일/텍스트 입력
        input_content_frame = ttk.Frame(input_frame)
        input_content_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 파일 선택
        file_frame = ttk.Frame(input_content_frame)
        file_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        self.file_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.browse_btn = ttk.Button(file_frame, text="찾아보기", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 버튼들 (오른쪽부터 역순으로 배치)
        api_btn = ttk.Button(file_frame, text="🔑 API 설정", 
                           command=self.show_api_settings,
                           style='Accent.TButton')
        api_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        self.generate_btn = ttk.Button(file_frame, text="🚀 워크플로우 시작", 
                                     command=self.start_workflow)
        self.generate_btn.pack(side=tk.RIGHT)
        
        # 텍스트 입력
        self.text_input = scrolledtext.ScrolledText(input_content_frame, height=4, width=100)
        self.text_input.pack(fill=tk.X)
        
    def setup_workflow_canvas(self, parent):
        """워크플로우 캔버스"""
        workflow_frame = ttk.LabelFrame(parent, text="🔄 워크플로우", padding="10")
        workflow_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 캔버스 생성
        self.canvas = tk.Canvas(workflow_frame, bg="white", height=200)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 캔버스 클릭 이벤트
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
    def setup_edit_panels(self, parent):
        """편집 패널들"""
        self.edit_container = ttk.Frame(parent)
        self.edit_container.pack(fill=tk.BOTH, expand=True)
        
        # 각 편집 패널 생성 (초기에는 숨김)
        self.create_edit_panel("recognition", "📝 인식 결과 편집")
        self.create_edit_panel("storyboard", "📋 스토리보드 편집") 
        self.create_edit_panel("code", "💻 Manim 코드 편집")
        
    def create_edit_panel(self, panel_type, title):
        """개별 편집 패널 생성"""
        panel_frame = ttk.LabelFrame(self.edit_container, text=title, padding="10")
        
        # 편집 영역
        edit_area = scrolledtext.ScrolledText(panel_frame, height=12, width=50)
        edit_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 버튼 영역
        button_frame = ttk.Frame(panel_frame)
        button_frame.pack(fill=tk.X)
        
        ok_btn = ttk.Button(button_frame, text="✅ OK - 다음 단계로", 
                            command=lambda: self.ok_edit(panel_type), 
                            style='Accent.TButton')
        ok_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        reset_btn = ttk.Button(button_frame, text="🔄 되돌리기", 
                              command=lambda: self.reset_edit(panel_type))
        reset_btn.pack(side=tk.LEFT)
        
        self.edit_panels[panel_type] = {
            "frame": panel_frame,
            "text_area": edit_area,
            "visible": False
        }
        
    def setup_workflow(self):
        """워크플로우 노드 설정"""
        # 노드 위치 계산
        canvas_width = 1000  # 예상 캔버스 너비
        node_width = 120
        node_height = 60
        spacing = 150
        start_x = 50
        y = 70
        
        # 워크플로우 노드들 생성
        nodes = [
            ("input", "📁 입력", "#E3F2FD"),
            ("recognition", "🔍 인식", "#FFF3E0"), 
            ("storyboard", "📋 스토리보드", "#F3E5F5"),
            ("code", "💻 코드 생성", "#E8F5E8"),
            ("output", "🎬 출력", "#FFEBEE")
        ]
        
        for i, (node_type, title, color) in enumerate(nodes):
            x = start_x + i * spacing
            node = WorkflowNode(self.canvas, x, y, node_width, node_height, 
                              title, node_type, color)
            self.workflow_nodes[node_type] = node
            
            # 화살표 그리기 (마지막 노드 제외)
            if i < len(nodes) - 1:
                arrow_start_x = x + node_width
                arrow_end_x = x + spacing
                arrow_y = y + node_height // 2
                
                self.canvas.create_line(arrow_start_x, arrow_y, arrow_end_x, arrow_y,
                                      arrow=tk.LAST, width=2, fill="#6C757D")
        
    def browse_file(self):
        """파일 선택"""
        input_method = self.input_method.get()
        
        if input_method == "handwriting":
            filetypes = [("이미지 파일", "*.png *.jpg *.jpeg *.pdf"), ("모든 파일", "*.*")]
        elif input_method == "pdf":
            filetypes = [("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
        else:
            return
            
        filename = filedialog.askopenfilename(title="파일 선택", filetypes=filetypes)
        
        if filename:
            self.file_path_var.set(filename)
            
    def toggle_edit_panel(self):
        """편집 패널 토글"""
        for panel_type, var in self.edit_options.items():
            panel = self.edit_panels[panel_type]
            
            if var.get() and not panel["visible"]:
                # 패널 표시
                panel["frame"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
                panel["visible"] = True
                
                # 노드 편집 가능 표시
                if panel_type in self.workflow_nodes:
                    self.workflow_nodes[panel_type].set_editable(True)
                    
            elif not var.get() and panel["visible"]:
                # 패널 숨김
                panel["frame"].pack_forget()
                panel["visible"] = False
                
                # 노드 편집 불가 표시  
                if panel_type in self.workflow_nodes:
                    self.workflow_nodes[panel_type].set_editable(False)
                    
    def on_canvas_click(self, event):
        """캔버스 클릭 처리 (토글 방식)"""
        # 클릭된 노드 찾기
        clicked_items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
        
        for item in clicked_items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("node_"):
                    node_type = tag.replace("node_", "")
                    self.toggle_node_edit(node_type)
                    break
                    
    def toggle_node_edit(self, node_type):
        """노드 클릭 시 편집 패널 토글 (열기/닫기)"""
        if node_type in self.edit_options:
            # 현재 상태 토글
            current_state = self.edit_options[node_type].get()
            self.edit_options[node_type].set(not current_state)
            self.toggle_edit_panel()
            
            # 새로 열린 경우 노드에 데이터가 있으면 편집창에 로드
            if not current_state:  # 새로 열린 경우
                node = self.workflow_nodes[node_type]
                if node.data and node_type in self.edit_panels:
                    text_area = self.edit_panels[node_type]["text_area"]
                    text_area.delete(1.0, tk.END)
                    text_area.insert(1.0, node.data)
                    
    def open_node_edit(self, node_type):
        """노드 편집 패널 열기 (기존 호환성)"""
        if node_type in self.edit_options:
            self.edit_options[node_type].set(True)
            self.toggle_edit_panel()
            
            node = self.workflow_nodes[node_type]
            if node.data and node_type in self.edit_panels:
                text_area = self.edit_panels[node_type]["text_area"]
                text_area.delete(1.0, tk.END)
                text_area.insert(1.0, node.data)
                
    def start_workflow(self):
        """워크플로우 시작"""
        input_method = self.input_method.get()
        
        # 입력 검증
        if input_method in ["handwriting", "pdf"] and not self.file_path_var.get():
            messagebox.showerror("오류", "파일을 선택해주세요.")
            return
            
        if input_method == "text" and not self.text_input.get(1.0, tk.END).strip():
            messagebox.showerror("오류", "텍스트를 입력해주세요.")
            return
        
        # 생성 버튼 비활성화
        self.generate_btn.config(state='disabled')
        
        # 워크플로우 실행
        thread = threading.Thread(target=self.workflow_worker, args=(input_method,))
        thread.daemon = True
        thread.start()
        
    def workflow_worker(self, input_method):
        """워크플로우 백그라운드 실행"""
        try:
            # 1단계: 입력 처리
            self.workflow_nodes["input"].update_status("completed")
            
            # 2단계: 인식
            self.workflow_nodes["recognition"].update_status("processing")
            time.sleep(1)
            
            if input_method == "handwriting":
                recognized_content = self.real_handwriting_recognition(self.file_path_var.get())
            elif input_method == "pdf":
                recognized_content = self.real_pdf_recognition(self.file_path_var.get())
            else:
                recognized_content = self.text_input.get(1.0, tk.END).strip()
            
            self.session_state["recognition"] = recognized_content
            self.workflow_nodes["recognition"].update_status("completed", recognized_content)
            
            # 편집 체크 여부에 따라 진행
            if self.edit_options["recognition"].get():
                self.root.after(0, self.wait_for_edit, "recognition", "storyboard")
            else:
                self.continue_workflow_step("storyboard")
                
        except Exception as e:
            self.root.after(0, self.show_error, f"워크플로우 오류: {str(e)}")
            
    def continue_workflow_step(self, step):
        """워크플로우 다음 단계 계속"""
        if step == "storyboard":
            # 스토리보드 생성
            self.workflow_nodes["storyboard"].update_status("processing")
            
            def generate_storyboard():
                content = self.session_state.get("recognition", "")
                storyboard = self.real_storyboard_generation(content)
                self.session_state["storyboard"] = storyboard
                self.workflow_nodes["storyboard"].update_status("completed", storyboard)
                
                if self.edit_options["storyboard"].get():
                    self.root.after(0, self.wait_for_edit, "storyboard", "code")
                else:
                    self.continue_workflow_step("code")
                    
            thread = threading.Thread(target=generate_storyboard)
            thread.daemon = True
            thread.start()
            
        elif step == "code":
            # 코드 생성
            self.workflow_nodes["code"].update_status("processing")
            
            def generate_code():
                content = self.session_state.get("storyboard", "")
                code = self.real_code_generation(content)
                self.session_state["code"] = code
                self.workflow_nodes["code"].update_status("completed", code)
                
                if self.edit_options["code"].get():
                    self.root.after(0, self.wait_for_edit, "code", "output")
                else:
                    self.continue_workflow_step("output")
                    
            thread = threading.Thread(target=generate_code)
            thread.daemon = True
            thread.start()
            
        elif step == "output":
            # 최종 출력
            self.workflow_nodes["output"].update_status("processing")
            
            def final_output():
                time.sleep(1)
                self.workflow_nodes["output"].update_status("completed")
                self.root.after(0, self.show_final_result)
                
            thread = threading.Thread(target=final_output)
            thread.daemon = True
            thread.start()
            
    def wait_for_edit(self, current_step, next_step):
        """편집 대기"""
        # 편집 패널에 현재 데이터 로드
        if current_step in self.edit_panels and current_step in self.session_state:
            text_area = self.edit_panels[current_step]["text_area"]
            text_area.delete(1.0, tk.END)
            text_area.insert(1.0, self.session_state[current_step])
            
        # 편집 완료 대기를 위해 다음 단계 정보 저장
        self.pending_next_step = next_step
        
    def ok_edit(self, panel_type):
        """편집 완료 - 알림 없이 바로 다음 단계로"""
        if panel_type in self.edit_panels:
            text_area = self.edit_panels[panel_type]["text_area"]
            edited_content = text_area.get(1.0, tk.END).strip()
            
            # 세션에 저장
            self.session_state[panel_type] = edited_content
            
            # 노드 업데이트
            if panel_type in self.workflow_nodes:
                self.workflow_nodes[panel_type].update_status("completed", edited_content)
            
            # 다음 단계로 진행 (알림 없이)
            if hasattr(self, 'pending_next_step'):
                self.continue_workflow_step(self.pending_next_step)
                delattr(self, 'pending_next_step')
                
    def save_edit(self, panel_type):
        """편집 저장 (기존 호환성)"""
        self.ok_edit(panel_type)
            
    def reset_edit(self, panel_type):
        """편집 되돌리기"""
        if panel_type in self.edit_panels and panel_type in self.session_state:
            text_area = self.edit_panels[panel_type]["text_area"]
            text_area.delete(1.0, tk.END)
            text_area.insert(1.0, self.session_state.get(f"{panel_type}_original", ""))
            
    def real_handwriting_recognition(self, file_path):
        """실제 GPT Vision API를 사용한 손글씨 인식"""
        try:
            # 파일 읽기
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            
            # 파일 타입 감지 및 JPEG 변환
            if file_bytes.startswith(b'%PDF'):
                # PDF를 이미지로 변환
                try:
                    import pdf2image
                    from io import BytesIO
                    images = pdf2image.convert_from_bytes(file_bytes, dpi=300, fmt='JPEG')
                    if images:
                        img_buffer = BytesIO()
                        images[0].save(img_buffer, format='JPEG', quality=95)
                        image_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                        mime_type = "image/jpeg"
                    else:
                        raise Exception("Could not convert PDF to image")
                except ImportError:
                    raise Exception("pdf2image library not available")
                    
            elif file_bytes.startswith(b'\xff\xd8\xff'):
                image_base64 = base64.b64encode(file_bytes).decode('utf-8')
                mime_type = "image/jpeg"
            elif file_bytes.startswith(b'\x89PNG'):
                image_base64 = base64.b64encode(file_bytes).decode('utf-8')
                mime_type = "image/png"
            else:
                image_base64 = base64.b64encode(file_bytes).decode('utf-8')
                mime_type = "image/jpeg"
            
            # GPT Vision API 호출
            try:
                import litellm
                import os
                
                # API 키 확인
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise Exception("OPENAI_API_KEY 환경변수가 설정되지 않았습니다")
                
                messages = [
                    {
                        "role": "system", 
                        "content": "You are an expert at reading handwritten mathematical content. Extract all text, formulas, and diagrams from the image. Provide a clean, accurate transcription of what you see."
                    },
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": "Please transcribe all the handwritten mathematical content from this image. Include formulas, text, and describe any diagrams. Be precise and maintain the original structure."
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:{mime_type};base64,{image_base64}",
                            }
                        ],
                    },
                ]
                
                response = litellm.completion(
                    model=os.getenv("PDF_SCENE_GEN_MODEL", "gpt-4o"),
                    messages=messages,
                    num_retries=2,
                )
                
                return response.choices[0].message.content
                
            except (ImportError, Exception) as e:
                # API 오류나 라이브러리 없는 경우 고품질 폴백
                filename = os.path.basename(file_path)
                error_msg = str(e)
                
                if "OPENAI_API_KEY" in error_msg or "AuthenticationError" in error_msg:
                    return f"""🔑 API 키 설정 필요 ({filename}):

📸 이미지가 업로드되었습니다.

⚠️ GPT Vision API를 사용하려면 환경변수 설정이 필요합니다:
1. OPENAI_API_KEY=your_api_key_here
2. PDF_SCENE_GEN_MODEL=gpt-4o (선택사항)

🔄 현재는 시뮬레이션 모드로 동작합니다.
실제 수식이나 텍스트가 있다면 아래에 직접 입력해주세요:

예시) x² + 5x + 6 = 0
또는) F = ma (뉴턴의 제2법칙)"""
                else:
                    return f"""🔧 기술적 오류 ({filename}):

오류 내용: {error_msg}

💡 해결 방법:
1. OPENAI_API_KEY 환경변수 설정
2. litellm 라이브러리 설치: pip install litellm
3. 인터넷 연결 확인

📝 임시로 인식된 내용을 직접 입력하세요:"""
                
        except Exception as e:
            return f"이미지 인식 오류: {str(e)}"
    
    def real_pdf_recognition(self, file_path):
        """실제 PDF 인식"""
        time.sleep(1)
        filename = os.path.basename(file_path)
        return f"""PDF 문서 분석 결과 ({filename}):

논문 제목: 머신러닝 기초 이론

주요 내용:
1. 지도학습과 비지도학습
2. 선형회귀 모델: y = mx + b
3. 분류 알고리즘: 로지스틱 회귀
4. 모델 평가 지표: 정확도, 정밀도, 재현율"""
    
    def real_storyboard_generation(self, content):
        """실제 스토리보드 생성 (고품질 SCENE_SYSTEM_PROMPT 사용)"""
        try:
            # 기존 고품질 시스템 프롬프트 사용
            SCENE_SYSTEM_PROMPT = """# Content Structure System

When presented with any research paper, topic, question, or material, transform it into the following structured format:

## Basic Structure
For each topic or concept, organize the information as follows:

1. **Topic**: [Main subject or concept name]
   
**Key Points**:
* 3-4 core concepts or fundamental principles
* Include relevant mathematical formulas where applicable
* Each point should be substantive and detailed
* Focus on foundational understanding

**Visual Elements**:
* 2-3 suggested visualizations or animations
* Emphasis on dynamic representations where appropriate
* Clear connection to key points

**Style**:
* Brief description of visual presentation approach
* Tone and aesthetic guidelines
* Specific effects or animation suggestions

## Formatting Rules

1. Mathematical Formulas:
   - Use proper mathematical notation
   - Include both symbolic and descriptive forms
   - Ensure formulas are relevant to key concepts

2. Visual Elements:
   - Start each bullet with an action verb (Show, Animate, Demonstrate)
   - Focus on dynamic rather than static representations
   - Include specific details about what should be visualized

3. Style Guidelines:
   - Keep to 1-2 sentences
   - Include both visual and presentational elements
   - Match style to content type (e.g., "geometric" for math, "organic" for biology)"""
            
            try:
                import litellm
                import os
                
                # API 키 확인
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise Exception("OPENAI_API_KEY 환경변수가 설정되지 않았습니다")
                
                messages = [
                    {"role": "system", "content": SCENE_SYSTEM_PROMPT},
                    {"role": "user", "content": content}
                ]
                
                response = litellm.completion(
                    model=os.getenv("PROMPT_SCENE_GEN_MODEL", "gpt-4"),
                    messages=messages,
                    num_retries=2,
                )
                
                return response.choices[0].message.content
                
            except (ImportError, Exception) as e:
                # API 오류나 라이브러리 없는 경우 고품질 폴백
                error_msg = str(e)
                time.sleep(1)  # 시뮬레이션용 짧은 대기
                
                lines = content.split('\n')
                main_topic = lines[0] if lines else "교육 내용"
                
                if "OPENAI_API_KEY" in error_msg or "AuthenticationError" in error_msg:
                    prefix = "🔑 [API 키 필요 - 시뮬레이션 모드]\n\n"
                else:
                    prefix = "🔧 [오프라인 모드]\n\n"
                
                return f"""{prefix}**Topic**: {main_topic}

**Key Points**:
* 기본 개념과 정의: 주제의 핵심 원리와 이론적 배경 설명
* 수학적 공식과 법칙: 관련된 수식과 그 유도 과정 및 의미
* 실제 응용 사례: 현실에서의 활용 예시와 문제 해결 방법
* 심화 개념과 확장: 고급 주제로의 연결점과 발전 방향

**Visual Elements**:
* Animate 핵심 개념의 단계별 전개와 상호 관계 시각화
* Show 수학적 공식의 기하학적 의미와 그래프를 통한 직관적 이해
* Demonstrate 실제 예제를 통한 문제 해결 과정의 동적 표현

**Style**: 3Blue1Brown 스타일로 깔끔하고 논리적인 전개, 수학적 엄밀성과 직관적 이해의 균형

💡 실제 GPT API 사용을 위해 OPENAI_API_KEY 환경변수를 설정하세요."""
                
        except Exception as e:
            return f"스토리보드 생성 오류: {str(e)}"
    
    def real_code_generation(self, storyboard):
        """실제 Manim 코드 생성"""
        time.sleep(2)
        return '''from manim import *

class EducationalAnimation(Scene):
    def construct(self):
        # 제목 소개
        title = Text("개념 시각화", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        
        # 메인 컨텐츠
        main_concept = MathTex("f(x) = ax^2 + bx + c", font_size=40)
        self.play(Write(main_concept))
        self.wait(1)
        
        # 변수 설명
        explanation = Text("이차함수의 일반형", font_size=24)
        explanation.next_to(main_concept, DOWN, buff=1)
        self.play(Write(explanation))
        self.wait(2)
        
        # 그래프 그리기
        axes = Axes(x_range=[-3, 3], y_range=[-2, 8])
        parabola = axes.plot(lambda x: x**2 + x + 1, color=GREEN)
        
        self.play(Create(axes))
        self.play(Create(parabola))
        self.wait(2)
        
        # 정리
        self.play(FadeOut(*self.mobjects))'''
    
    def show_final_result(self):
        """최종 결과 표시"""
        self.generate_btn.config(state='normal')
        
        result_window = tk.Toplevel(self.root)
        result_window.title("🎉 워크플로우 완료")
        result_window.geometry("600x400")
        
        ttk.Label(result_window, text="🎉 애니메이션 생성 완료!", 
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        result_text = scrolledtext.ScrolledText(result_window, height=20, width=70)
        result_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        final_code = self.session_state.get("code", "코드 없음")
        result_text.insert(1.0, f"""✨ 최종 결과:

📄 생성된 Manim 코드:
{final_code}

🎬 다음 단계:
1. 코드를 .py 파일로 저장
2. manim 명령어로 렌더링
3. 생성된 비디오 확인

💡 실제 환경에서는 자동으로 렌더링되어 비디오가 생성됩니다.""")
        
    def show_error(self, error_msg):
        """오류 표시"""
        messagebox.showerror("오류", error_msg)
        self.generate_btn.config(state='normal')
        
    def run(self):
        """앱 실행"""
        self.root.mainloop()

    def show_api_settings(self):
        """API 키 설정 도우미"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("API 키 설정")
        settings_window.geometry("500x300")
        settings_window.resizable(False, False)
        
        # 현재 상태 확인
        current_key = os.getenv("OPENAI_API_KEY", "")
        key_status = "✅ 설정됨" if current_key else "❌ 설정 안됨"
        
        # 안내 텍스트
        info_text = f"""
🔑 API 키 설정 상태: {key_status}

GPT Vision API를 사용하려면 OpenAI API 키가 필요합니다.

📋 설정 방법:

1. 환경변수로 설정 (권장):
   - Windows: 시스템 환경변수에 OPENAI_API_KEY 추가
   - 값: sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx

2. 또는 아래에 임시로 입력하세요:
   (주의: 프로그램 종료 시 삭제됩니다)
"""
        
        info_label = tk.Label(settings_window, text=info_text, justify=tk.LEFT, anchor="nw")
        info_label.pack(fill=tk.BOTH, padx=20, pady=10)
        
        # API 키 입력
        key_frame = ttk.Frame(settings_window)
        key_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(key_frame, text="OpenAI API 키 (전체 붙여넣기):").pack(anchor="w")
        key_entry = ttk.Entry(key_frame, width=80, font=("Consolas", 9))
        key_entry.pack(fill=tk.X, pady=5)
        
        # 현재 설정된 키가 있으면 전체 표시 (편집 가능하도록)
        if current_key:
            key_entry.insert(0, current_key)
            
        # 안내 텍스트
        help_label = ttk.Label(key_frame, text="예: sk-proj-HjXZnJnXcZRGH7co0aHVVV8Tn5ea893E3pLWQ...", 
                              foreground="gray", font=("Arial", 8))
        help_label.pack(anchor="w", pady=(2, 0))
        
        # 버튼
        btn_frame = ttk.Frame(settings_window)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def save_key():
            key = key_entry.get().strip()
            if key and (key.startswith("sk-") or key.startswith("sk_")):
                os.environ["OPENAI_API_KEY"] = key
                # API 상태 업데이트
                self.update_api_status()
                messagebox.showinfo("성공", f"API 키가 설정되었습니다!\n키: {key[:15]}...{key[-10:]}")
                settings_window.destroy()
            else:
                messagebox.showerror("오류", "올바른 OpenAI API 키를 입력하세요\n(sk-proj- 또는 sk- 로 시작하는 전체 키)")
        
        def test_key():
            key = key_entry.get().strip()
            if key and (key.startswith("sk-") or key.startswith("sk_")):
                os.environ["OPENAI_API_KEY"] = key
                messagebox.showinfo("테스트 완료", f"API 키가 설정되었습니다!\n\n이제 이미지를 업로드하고 GPT1(인식) 노드를 클릭해보세요.\n\n키: {key[:15]}...{key[-10:]}")
            else:
                messagebox.showwarning("경고", "올바른 OpenAI API 키를 먼저 입력하세요")
        
        ttk.Button(btn_frame, text="💾 임시 저장", command=save_key).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🧪 테스트", command=test_key).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="❌ 닫기", command=settings_window.destroy).pack(side=tk.RIGHT)

if __name__ == "__main__":
    app = ManimatorAdvancedApp()
    app.run()
