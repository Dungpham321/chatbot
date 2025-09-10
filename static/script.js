document.getElementById("chat-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const form = new FormData(this);
    const chatBox = document.getElementById("chat-box");
    const question = form.get("question");

    // Hiển thị tin nhắn người dùng
    const userMsg = document.createElement("div");
    userMsg.className = "message user-message";
    userMsg.innerHTML = `<strong>Bạn:</strong> ${question}`;
    chatBox.appendChild(userMsg);

    // Tạo khối "Bot đang trả lời..."
    const botTyping = document.createElement("div");
    botTyping.className = "message bot-message typing";
    botTyping.innerHTML = `<strong>Bot:</strong> <em>Đang trả lời...</em>`;
    chatBox.appendChild(botTyping);
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("/chat", {
        method: "POST",
        body: form
    })
    .then(res => res.json())
    .then(data => {
        // Xóa đoạn "Đang trả lời..."
        botTyping.remove();

        // Hiển thị câu trả lời thật
        const botMsg = document.createElement("div");
        botMsg.className = "message bot-message";
        botMsg.innerHTML = `<strong>Bot:</strong><div class="markdown">${marked.parse(data.answer)}</div>`;
        chatBox.appendChild(botMsg);

        this.reset();
        chatBox.scrollTop = chatBox.scrollHeight;
    });
});
document.getElementById("file-upload").addEventListener("change", function () {
    const fileNameSpan = document.getElementById("file-name");
    const file = this.files[0];
    if (file) {
        fileNameSpan.textContent = file.name;
    } else {
        fileNameSpan.textContent = "";
    }
});