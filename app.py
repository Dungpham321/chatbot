from flask import Flask, render_template, request, jsonify,Response, session
import os, requests
import json
from docx import Document
import PyPDF2
from dotenv import load_dotenv
load_dotenv()
from datetime import timedelta
import redis


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv('SECRET_KEY')
app.permanent_session_lifetime = timedelta(hours=1)

r = redis.Redis(
    host=os.getenv('HOST_RE'),  # endpoint từ Redis Cloud
    port=10164,                                         # port từ Redis Cloud
    password=os.getenv('PASSWORD_RE'),                          # mật khẩu từ Redis Cloud
    ssl=False,                                           # Redis Cloud yêu cầu SSL
    decode_responses=True                              # để nhận dữ liệu dạng chuỗi
)


# Hàm gọi Deepseek
def ask_deepseek(context, question):
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("REFERER"),
        "X-Title": os.getenv("TITLE")
    }
    payload = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [{"role": "user", "content": f"Dựa trên văn bản sau, hãy trả lời bằng tiếng Việt:\n{context}\nCâu hỏi: {question}"}]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    question = request.form.get("question")
    context_key = "chat:context"
    context = ""
    file = request.files.get("file")
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        ext = os.path.splitext(file.filename)[1].lower()
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                context += "\n\n" + f.read()
        elif ext == ".docx":
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            context += "\n\n" + text
        elif ext == ".pdf":
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            context += "\n\n" + text
        else:
            context += "\n\n[Không hỗ trợ định dạng file này]"
        r.setex(context_key,1800, context)
    else:
        # Nếu không có file → dùng context cũ trong session
        context = r.get(context_key) or ""
    answer = ask_deepseek(context, question)
    response_data = json.dumps({"answer": answer}, ensure_ascii=False)
    return Response(response_data, content_type="application/json; charset=utf-8")


if __name__ == "__main__":
    app.run(debug=True)