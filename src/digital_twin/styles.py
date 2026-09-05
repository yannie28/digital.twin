custom_css = """
:root {
    --bg-color: #FFF5F8;
    --primary: #FFB6C1;
    --secondary: #FFDDE7;
    --accent: #FF8FAB;
    --text: #5A4A4D;
}

body {
    background-color: var(--bg-color) !important;
    font-family: 'Poppins', sans-serif;
}

.gradio-container {
    background: var(--bg-color) !important;
}

.chatbot {
    border: 2px solid var(--secondary) !important;
    border-radius: 20px !important;
    background: white !important;
}

.message.user {
    background: #FFC1D6 !important;
    color: var(--text) !important;
    border-radius: 18px 18px 4px 18px !important;
}

.message.bot {
    background: #FFE4EC !important;
    color: var(--text) !important;
    border-radius: 18px 18px 18px 4px !important;
}

textarea {
    border-radius: 15px !important;
    border: 2px solid var(--secondary) !important;
}

button {
    background: linear-gradient(135deg, #FFB6C1, #FF8FAB) !important;
    border: none !important;
    color: white !important;
    border-radius: 15px !important;
    font-weight: bold !important;
}

h1 {
    color: #D63384;
    text-align: center;
}
"""

