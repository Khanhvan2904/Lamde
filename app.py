import streamlit as st
import google.generativeai as genai
from docx import Document
import io, random, re

# --- CẤU HÌNH AI ---
genai.configure(api_key="MÃ_API_CỦA_BẠN")
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_questions_via_ai(file):
    """Sử dụng AI để nhận diện danh sách câu hỏi chính xác nhất"""
    doc = Document(file)
    full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    
    prompt = f"""
    Phân tích văn bản sau và chia nó thành danh sách các câu hỏi riêng biệt.
    Mỗi câu hỏi phải bao gồm cả nội dung câu hỏi và các phương án trả lời đi kèm.
    Chỉ trả về danh sách, mỗi câu hỏi cách nhau bởi ký tự '###'.
    Nội dung: {full_text[:30000]}
    """
    response = model.generate_content(prompt)
    # Chia nhỏ kết quả dựa trên ký tự ngăn cách của AI
    questions = response.text.split('###')
    return [q.strip() for q in questions if len(q.strip()) > 10]

def create_final_docx(selected_qs):
    doc = Document()
    for i, q_text in enumerate(selected_qs):
        # Đánh lại số câu tự động
        clean_text = re.sub(r'^Câu\s*\d+[:\.]?', f'Câu {i+1}:', q_text, flags=re.IGNORECASE)
        doc.add_paragraph(clean_text)
        doc.add_paragraph("-" * 20)
    
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- GIAO DIỆN ---
st.title("🎯 Trình Tạo Đề Thi Thông Minh")

with st.sidebar:
    n_multi = st.number_input("Số câu Dạng 1", value=10)
    n_tf = st.number_input("Số câu Dạng 2", value=4)
    n_short = st.number_input("Số câu Dạng 3", value=6)

col1, col2, col3 = st.columns(3)
f1 = col1.file_uploader("Ngân hàng Dạng 1", type=['docx'])
f2 = col2.file_uploader("Ngân hàng Dạng 2", type=['docx'])
f3 = col3.file_uploader("Ngân hàng Dạng 3", type=['docx'])

if st.button("🚀 Tạo Đề Ngẫu Nhiên"):
    if f1 and f2 and f3:
        with st.spinner("AI đang phân tích ngân hàng câu hỏi..."):
            bank1 = extract_questions_via_ai(f1)
            bank2 = extract_questions_via_ai(f2)
            bank3 = extract_questions_via_ai(f3)
            
            # Hiển thị số lượng AI tìm được để kiểm tra
            st.write(f"Tìm thấy: Dạng 1 ({len(bank1)} câu), Dạng 2 ({len(bank2)} câu), Dạng 3 ({len(bank3)} câu)")
            
            if len(bank1) >= n_multi and len(bank2) >= n_tf and len(bank3) >= n_short:
                final_selection = random.sample(bank1, n_multi) + \
                                  random.sample(bank2, n_tf) + \
                                  random.sample(bank3, n_short)
                
                final_doc = create_final_docx(final_selection)
                st.download_button("📥 Tải Đề Thi (.docx)", final_doc, "De_Thi_Random.docx")
            else:
                st.error("Số lượng câu hỏi AI nhận diện được vẫn ít hơn yêu cầu. Hãy kiểm tra lại file gốc.")
