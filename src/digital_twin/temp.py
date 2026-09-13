import gradio as gr

custom_css = """
.gradio-container {
    max-width: 900px !important; /* Adjust max width (e.g., 700px, 60vw) */
    margin: 0 auto !important;   /* Centers the app horizontally */
}

/* --- 1. SHARED RESPONSIVE STRUCTURE --- */
.centered-container {
    max-width: 700px;
    margin: 0 auto;
    text-align: center;
    padding-top: 40px;
    font-family: ui-sans-serif, system-ui, sans-serif;
}
.avatar-img {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    margin: 0 auto 20px auto;
    object-fit: cover;
    display: block;
}
.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 10px;
}
.main-title em {
    font-style: italic;
    color: #2563eb !important;
}
.subtitle {
    font-size: 1.1rem;
    margin-bottom: 30px;
}
/* Pill suggestion buttons styling */
.pill-button {
    border-radius: 9999px !important;
    padding: 6px 16px !important;
    font-size: 0.9rem !important;
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s;
}
/* Fixed permanent bottom panel wrapper */
.input-wrapper {
    position: fixed;
    bottom: 0px;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 760px;
    padding: 20px 10px 30px 10px;
    z-index: 100;
    border: none !important;
}

/* --- REMOVE GRADIO BLOCK BACKGROUND LAYERS --- */
.input-wrapper > div,
.input-wrapper div[class*="form"],
.input-wrapper .form,
.input-wrapper [class*="block"] {
    border: none !important;
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
}

/* Fixed Textbox style matching the Amber/Gold design line */
.input-wrapper textarea {
    border: 1px solid #cbd5e1 !important;        /* Soft blue-gray border */
    border-radius: 12px !important;              /* Rounded corners matching image */
    padding: 16px 20px !important;              /* Generous inner spacing */
    font-size: 1rem !important;
    color: #64748b !important;                   /* Subtle slate text color */
    background-color: #ffffff !important;        /* Solid white background */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important; /* Soft bottom drop shadow */
    outline: none !important;
}

/* Optional: Subtle blue glow on focus */
.input-wrapper textarea:focus {
    border-color: #94a3b8 !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
}

/* --- FIX: STRIP GLOBAL GRADIO THEME THEME VARIABLES TO FORCE TRANSPARENCY --- */
.chat-display {
    --block-background-fill: transparent !important;
    --panel-background-fill: transparent !important;
    --background-fill-secondary: transparent !important;
    border: none !important;
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
    margin-bottom: 140px;
}

.chat-display, 
.chat-display > div,
.chat-display [class*="panel"],
.chat-display [class*="wrapper"],
.chat-display [class*="group"],
.chat-display [class*="message-wrap"] {
    border: none !important;
    border-color: transparent !important;
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
}

.chat-display div[class*="message"] div[class*="user"],
.chat-display [data-testid="user-message"] {
    background-color: #f9fafb !important; /* Rich blue user bubble */
    padding: 6px 8px !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 12px !important;
}
.chat-display div[class*="message"] div[class*="bot"],
.chat-display div[class*="message"] div[class*="assistant"],
.chat-display [data-testid="bot-message"] {
    border-radius: 12px !important;
    padding: 12px 16px !important;
    border: none !important;
}

/* Hide default "Chatbot" header label */
.chat-display [class*="header"] {
    display: none !important;
}

/* --- 3. DARK THEME AUTOMATION RULES --- */
@media (prefers-color-scheme: dark) {
    :root {
        --body-text-color: #f9fafb !important;
        --background-fill-primary: #040814 !important; /* Pitch dark canvas */
    }
}
.dark, body.dark {
    --body-text-color: #f9fafb !important;
    --background-fill-primary: #040814 !important;
}
.dark .main-title { color: #f9fafb !important; }
.dark .subtitle { color: #9ca3af !important; }
.dark .pill-button {
    border: 1px solid #1f2937 !important;
    background-color: #111827 !important;
    color: #e5e7eb !important;
}
.dark .pill-button:hover { background-color: #1f2937 !important; }

.dark .input-wrapper {
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
}
.dark .input-wrapper textarea {
    background-color: #0c1020 !important;
    color: #f9fafb !important;
}
.dark .input-wrapper textarea::placeholder {
    color: #4b5563 !important;
}

/* Isolate background color rules specifically onto message text bubbles */
.dark .chat-display div[class*="message"] div[class*="user"],
.dark .chat-display [data-testid="user-message"] {
    background-color: #132342 !important; /* Rich blue user bubble */
    color: #f9fafb !important;
}
"""

with gr.Blocks() as demo:
    
    with gr.Column(elem_classes="centered-container") as welcome_screen:
        gr.HTML('<img src="https://unsplash.com" class="avatar-img" alt="Digital Twin Avatar">')
        gr.HTML("<h1 class='main-title'>I'm Ed Donner's <em>digital twin.</em><br>Ask me anything &ndash; the real Ed Donner might just chime in.</h1>")
        gr.HTML("<p class='subtitle'>I know Ed Donner's background, courses, and curriculum.<br>I can also put you in touch directly.</p>")
        
        with gr.Row():
            btn1 = gr.Button("Which order should I take your courses", elem_classes="pill-button")
            btn2 = gr.Button("What job can I get after taking your courses?", elem_classes="pill-button")
            btn3 = gr.Button("I'd like to get in touch", elem_classes="pill-button")

    chatbot = gr.Chatbot(elem_classes="chat-display", visible=False)

    with gr.Row(elem_classes="input-wrapper"):
        user_input = gr.Textbox(
            show_label=False,
            placeholder='Ask me anything...',
            lines=1,
            max_lines=3,
            scale=4
        )

    def respond(message, history):
        if not message.strip():
            return "", history, gr.update(), gr.update()
        
        bot_reply = (
            "Hi there, nice to meet you.\n\n"
            "I'm Ed Donner's AI digital twin, here to help with questions about my "
            "courses, AI engineering, agents, or anything else professional you'd "
            "like to discuss. I'm also always grateful if you follow me on LinkedIn "
            "and subscribe to my YouTube channel."
        )
        
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": bot_reply})
        
        return "", history, gr.update(visible=False), gr.update(visible=True)

    user_input.submit(
        respond, 
        inputs=[user_input, chatbot], 
        outputs=[user_input, chatbot, welcome_screen, chatbot]
    )
    
    btn1.click(lambda: "Which order should I take your courses", None, user_input)
    btn2.click(lambda: "What job can I get after taking your courses?", None, user_input)
    btn3.click(lambda: "I'd like to get in touch", None, user_input)

if __name__ == "__main__":
    demo.launch(css=custom_css)
