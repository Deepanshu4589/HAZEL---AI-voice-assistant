import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
import tkinter as tk
from tkinter import scrolledtext
import threading
import cohere

# Replace with your Cohere API key
co = cohere.Client("Oyj03hkz48muxKqzsc1VOtsUuVSGuX49jpMZFdpk")

# Initialize TTS engine
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)

is_speaking = False  # flag for speaking

def speak(text):
    def _speak():
        global is_speaking
        is_speaking = True
        engine.say(text)
        engine.runAndWait()
        is_speaking = False
    threading.Thread(target=_speak).start()

def stop_speaking():
    global is_speaking
    if is_speaking:
        engine.stop()
        is_speaking = False

# GUI setup
root = tk.Tk()
root.title("Hazel - Virtual Assistant (Cohere)")
root.geometry("600x500")

response_text = scrolledtext.ScrolledText(root, width=60, height=15, wrap=tk.WORD, font=("Arial", 12))
response_text.pack(padx=20, pady=10)

chat_entry = tk.Entry(root, width=50, font=("Arial", 12))
send_chat_button = tk.Button(root, text="Send Chat", font=("Arial", 12))

is_chat_mode = tk.BooleanVar()
is_chat_mode.set(False)

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Hazel Listening....")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5)
            print("Recognizing....")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}\n")
            return query.lower()
        except Exception:
            print("Could not understand audio.")
            return "none"

def wish_me():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good morning Sir!")
    elif 12 <= hour < 18:
        speak("Good afternoon Sir!")
    else:
        speak("Good evening Sir!")
    speak("I am HAZEL, your virtual assistant using Cohere AI.")

def display_response(response):
    def _display():
        response_text.insert(tk.END, response + "\n")
        response_text.yview(tk.END)
        speak(response)
    threading.Thread(target=_display).start()

def chat_with_cohere(prompt):
    try:
        response = co.chat(
            model="command-r-plus",
            message=prompt,
            temperature=0.5,
        )
        return response.text.strip()
    except Exception as e:
        return f"Hazel: Error - {str(e)}"

def process_query(query):
    def _process():
        if "wikipedia" in query:
            display_response("Searching on Wikipedia...")
            search_query = query.replace("wikipedia", "")
            try:
                result = wikipedia.summary(search_query, sentences=2)
                display_response("Hazel: " + result)
            except wikipedia.exceptions.DisambiguationError:
                display_response("Please be more specific.")
            except wikipedia.exceptions.PageError:
                display_response("No information found.")

        elif "youtube" in query:
            webbrowser.open("https://youtube.com")

        elif "college website" in query:
            webbrowser.open("https://www.clginstitute.org/")

        elif "instagram" in query:
            webbrowser.open("https://instagram.com")

        elif "google" in query:
            webbrowser.open("https://google.com")

        elif "time" in query:
            now = datetime.datetime.now()
            response = f"The time is {now.strftime('%H')} hour and {now.strftime('%M')} minutes."
            display_response("Hazel: " + response)

        elif "set reminder" in query:
            rememberMsg = query.replace("set reminder", "")
            speak(f"Okay, I will remember that: {rememberMsg}")
            with open("reminder.txt", "w") as f:
                f.write(rememberMsg)

        elif "remember" in query or "remind" in query:
            try:
                with open("reminder.txt", "r") as f:
                    content = f.read()
                    display_response("Hazel: You asked me to remember - " + content)
            except FileNotFoundError:
                display_response("Hazel: No reminders found.")

        elif "exit" in query:
            display_response("Hazel: Goodbye!")
            root.destroy()

        else:
            reply = chat_with_cohere(query)
            display_response("Hazel: " + reply)

    threading.Thread(target=_process).start()

def take_voice_command():
    if is_chat_mode.get():
        return
    def _listen():
        query = take_command()
        if query != "none":
            response_text.insert(tk.END, "User: " + query + "\n")
            response_text.yview(tk.END)
            process_query(query)
    threading.Thread(target=_listen).start()

def send_chat():
    query = chat_entry.get()
    chat_entry.delete(0, tk.END)
    if query.strip():
        response_text.insert(tk.END, "User: " + query + "\n")
        response_text.yview(tk.END)
        process_query(query)

def toggle_chat_mode():
    if is_chat_mode.get():
        chat_entry.pack(pady=5)
        send_chat_button.pack(pady=5)
        voice_command_button.config(state=tk.DISABLED)
    else:
        chat_entry.pack_forget()
        send_chat_button.pack_forget()
        voice_command_button.config(state=tk.NORMAL)

# Buttons
voice_command_button = tk.Button(root, text="Take Voice Command", command=take_voice_command, font=("Arial", 12))
voice_command_button.pack(pady=10)

stop_speaking_button = tk.Button(root, text="Stop Speaking", command=stop_speaking, font=("Arial", 12), fg="red")
stop_speaking_button.pack(pady=5)

chat_mode_checkbox = tk.Checkbutton(root, text="Switch to Chat Mode", variable=is_chat_mode,
                                    command=toggle_chat_mode, font=("Arial", 12))
chat_mode_checkbox.pack(pady=5)

send_chat_button.config(command=send_chat)

exit_button = tk.Button(root, text="Exit", command=root.destroy, font=("Arial", 12))
exit_button.pack(pady=10)

wish_me()
root.mainloop()
