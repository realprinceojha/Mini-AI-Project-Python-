import sys
import openai
import pyttsx3
import speech_recognition as sr
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtGui import QColor, QPalette, QTextCursor
from PyQt5.QtCore import Qt
from datetime import datetime

# ==========================
# OpenAI API Key
# ==========================
openai.api_key = "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"  # yaha apna key daal

# ==========================
# Voice Engine Setup
# ==========================
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0 = male, 1 = female
engine.setProperty('rate', 150)

def speak(text):
    if text:
        engine.say(text)
        engine.runAndWait()

def stop_speaking():
    engine.stop()  # <-- AI voice ko turant rokne ke liye

# ==========================
# Voice Recognizer
# ==========================
recognizer = sr.Recognizer()
mic = sr.Microphone()

# ==========================
# Main GUI
# ==========================
class MiniAI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini AI - Advanced Assistant")
        self.setGeometry(200, 100, 700, 600)
        self.setStyleSheet("background-color: #121212; color: #ffffff; font-size: 14px;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Title & Subtitle
        self.title_label = QLabel("Mini AI")
        self.title_label.setStyleSheet("color: #00ffff; font-size: 22px; font-weight: bold;")
        layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        self.subtitle_label = QLabel("Ask anything! Type or use voice 🎤")
        self.subtitle_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        layout.addWidget(self.subtitle_label, alignment=Qt.AlignCenter)

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        # monospaced font + bold for thick output
        self.chat_box.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-size: 14px; font-family: 'Courier New'; font-weight:bold;")
        layout.addWidget(self.chat_box)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your question here...")
        self.input_field.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-size: 14px; padding:5px;")
        self.input_field.returnPressed.connect(self.send_text)  # <-- Enter key triggers send
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("background-color: #00bfff; color: #000000; font-weight:bold; padding:5px;")
        self.send_btn.clicked.connect(self.send_text)
        input_layout.addWidget(self.send_btn)

        self.voice_btn = QPushButton("Voice")
        self.voice_btn.setStyleSheet("background-color: #ff8c00; color: #000000; font-weight:bold; padding:5px;")
        self.voice_btn.clicked.connect(self.voice_input)
        input_layout.addWidget(self.voice_btn)

        # Stop Voice Button
        self.stop_voice_btn = QPushButton("Stop Voice")
        self.stop_voice_btn.setStyleSheet("background-color: #ff0000; color: #ffffff; font-weight:bold; padding:5px;")
        self.stop_voice_btn.clicked.connect(stop_speaking)
        input_layout.addWidget(self.stop_voice_btn)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def send_text(self):
        user_input = self.input_field.text()
        if not user_input.strip():
            return
        self.display_message("You", user_input)
        self.input_field.clear()
        self.ai_response(user_input, voice=False)

    def voice_input(self):
        self.display_message("You", "[Voice Input...]")
        QApplication.processEvents()
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio, language='en-IN')
            self.display_message("You", user_input)
            self.ai_response(user_input, voice=True)
        except:
            self.display_message("AI", "Sorry, I could not recognize your voice.")
            speak("Sorry, I could not recognize your voice.")

    def ai_response(self, user_input, voice=False):
        response_text = ""

        # ==========================
        # Time & Date
        # ==========================
        if "time" in user_input.lower():
            now = datetime.now()
            response_text = f"Current time is {now.strftime('%H:%M:%S')}"
        elif "date" in user_input.lower():
            now = datetime.now()
            response_text = f"Today's date is {now.strftime('%d-%m-%Y')}"
        else:
            # OpenAI Response
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": user_input}]
                )
                response_text = response.choices[0].message.content
            except Exception as e:
                print("Error:", e)
                response_text = "Sorry, I could not process your request."

        self.display_message("AI", response_text)
        if voice:
            speak(response_text)

    def display_message(self, sender, message):
        color = "#00ff00" if sender == "You" else "#ff00ff"
        # monospace + bold for thick text
        self.chat_box.append(f'<span style="color:{color}; font-weight:bold; font-family: "Courier New";">{sender}:</span> {message}')
        self.chat_box.moveCursor(QTextCursor.End)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiniAI()
    window.show()
    sys.exit(app.exec_())
