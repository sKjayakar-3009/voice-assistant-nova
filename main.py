import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import pyttsx3 as p
import speech_recognition as sr
import subprocess
import pyautogui
import selenium_w
from selenium_w import infow
from datetime import datetime
from googletrans import Translator
from tkinter import messagebox
from tkinter import Label, Toplevel,Entry,Button,OptionMenu,StringVar
import time
import threading
import random
import logging
import pyttsx3
import webbrowser
from tkinter import scrolledtext
import math
import cv2


# Define paths for system applications
CONTROL_PANEL_COMMAND = 'C:\\Windows\\System32\\control.exe'
CALCULATOR_COMMAND = 'C:\\Windows\\System32\\calc.exe'
THIS_PC_COMMAND = 'C:\\Windows\\System32\\explorer.exe'
COMMAND_PROMPT = 'C:\\Windows\\System32\\cmd.exe'

# Initialize text-to-speech engine globally
engine = p.init()
users_db = {"1234": "1234"}

def recognize_speech(recognizer=None):
    if recognizer is None:
        recognizer = sr.Recognizer()  # Or however you initialize your recognizer

    # Your voice recognition code goes here, using the provided recognizer
    # For example:
    print("Listening for speech...")
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except:
        return None

def typing_effect(text_widget, text, tag, delay=0.05):
    text_widget.delete('1.0', tk.END)
    for char in text:
        text_widget.insert(tk.END, char, tag)
        text_widget.update()
        time.sleep(delay)

def create_input_window(platform_name, callback):
    window = tk.Tk()
    window.title(f"Search on {platform_name}")
    window.configure(bg="#e3f2fd")  # Light blue background

    logo_label = tk.Label(window, text=platform_name, font=("Arial", 12, "bold"), bg="#e3f2fd", fg="#0d47a1")
    logo_label.pack(pady=10)

    entry = tk.Entry(window, width=50, font=("Arial", 10))
    entry.pack(pady=10)

    def submit_action():
        input_text = entry.get()
        if input_text:
            callback(input_text)
            window.destroy()
        else:
            messagebox.showwarning("Input Error", "Please enter a search topic.")

    submit_button = tk.Button(window, text="Submit", command=submit_action, bg="#1e88e5", fg="white",
                              font=("Arial", 10, "bold"))
    submit_button.pack(side="left", padx=10)

    recognizer = sr.Recognizer()

    def mic_action():
        spoken_text = recognize_speech(recognizer)
        entry.delete(0, tk.END)
        entry.insert(0, spoken_text)

    mic_button = tk.Button(window, text="🎤", command=mic_action, bg="#1e88e5", fg="white", font=("Arial", 10, "bold"))
    mic_button.pack(side="right", padx=10)

    window.mainloop()


def perform_calculation(expression):
    try:
        # Handle special calculations
        if 'log' in expression:
            result = eval(expression.replace('log', 'math.log'))
        elif '^' in expression:
            base, exp = expression.split('^')
            result = math.pow(float(base), float(exp))
        else:
            result = eval(expression)  # Perform the calculation
        return f"The result is: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


def on_microphone_click(text_box, recognizer):
    def recognize_speech():
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                text_box.delete(0, tk.END)  # Clear the text box
                text_box.insert(0, text)  # Insert recognized text into the text box
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Could not understand audio")
        except sr.RequestError:
            messagebox.showerror("Error", "Could not request results from Google Speech Recognition service")

    recognize_speech()


def on_submit_click(text_box):
    expression = text_box.get()
    # Perform calculation
    result = perform_calculation(expression)

    # Show result in Calculator app
    open_calculator_and_input(expression)

    # Update UI
    messagebox.showinfo("Result", result)


def open_calculator_and_input(expression):
    # Open Calculator
    subprocess.Popen('calc.exe', shell=True)

    # Wait for the Calculator to open
    time.sleep(2)

    # Simulate typing the expression into the Calculator
    pyautogui.typewrite(expression)
    pyautogui.press('enter')


def create_calculator_window(update_ui_callback, recognizer):
    window = tk.Tk()
    window.title("Calculator")

    label = tk.Label(window, text="Enter calculation:")
    label.pack(pady=10)

    text_box = tk.Entry(window, width=50)
    text_box.pack(pady=5)

    mic_button = tk.Button(window, text="🎙️", command=lambda: on_microphone_click(text_box, recognizer))
    mic_button.pack(side=tk.LEFT, padx=5)

    submit_button = tk.Button(window, text="Submit", command=lambda: on_submit_click(text_box))
    submit_button.pack(side=tk.LEFT, padx=5)

    window.mainloop()

def create_round_image(image_path, size):
    try:
        image = Image.open(image_path).convert("RGBA")
        image = image.resize((size, size), Image.LANCZOS)
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        result = Image.new('RGBA', (size, size))
        result.paste(image, (0, 0), mask)
        return ImageTk.PhotoImage(result)
    except Exception as e:
        logging.error(f"Error creating round image: {e}")
        return None

def tell_time_and_date():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")
    return f"The current time is {current_time} and today's date is {current_date}."

def wait_for_ready(r,update_ui_callback):
        update_ui_callback("Nova: Ready detected. You can proceed.")

def generate_meeting_link():
    base_url = "https://meet.jit.si/" # Replace with your Daily.co subdomain
    unique_room_name = f"Room{random.randint(1000, 9999)}"
    return f"{base_url}{unique_room_name}"


def start_captioning(root):
    # Create a new Toplevel window for captions
    caption_window = Toplevel(root)
    caption_window.title("Live Captions")
    caption_window.geometry("600x100")

    # Keep the caption window always on top
    caption_window.attributes("-topmost", True)

    # Label to show live captions
    caption_label = Label(caption_window, text="Captions will appear here...", font=("Playfair Display", 12), wraplength=300)
    caption_label.pack(pady=20)

    # Function to capture and display speech as text
    recognizer = sr.Recognizer()
    def update_caption():
        if not caption_window.winfo_exists():  # Check if the window still exists
            return  # Exit if the window is closed

        with sr.Microphone() as source:
            caption_label.config(text="Listening...")  # Update if the window is active
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                caption_label.config(text=f"Caption: {text}")
            except sr.UnknownValueError:
                if caption_label.winfo_exists():  # Check if label still exists
                    caption_label.config(text="Could not understand audio")
            except sr.RequestError:
                if caption_label.winfo_exists():  # Check if label still exists
                    caption_label.config(text="Error with the speech recognition service")

            # Schedule the next caption update if window is still open
        if caption_window.winfo_exists():
            caption_window.after(2000, update_caption)  # Adjust interval as needed

            # Start capturing and updating captions
        update_caption()

def handle_task(r, update_ui_callback, stop_main_mic, input_text=None, user_input=None):
    while True:  # Continuously wait for input until an exit command is given
        query = user_input if user_input else recognize_speech()
        print(f"Final query: {query}")

        if not query:
            update_ui_callback("Nova: I'm sorry, I couldn't understand that. Could you please type your query or try speaking again?")
            continue  # Ask again if no valid input

        # Display the user query
        update_ui_callback(f"User: {query}")
        query_lower = query.lower()  # Convert to lowercase for easier keyword matching

        global mic_active
        mic_active = False
        def add_ready_button():
            ready_button = tk.Button(
                root, text="Ready", command=lambda: handle_next_task(ready_button),
                bg="#00796b", fg="white", font=("Arial", 10, "bold"),
                borderwidth=0, highlightthickness=0
            )
            ready_button.config(width=12, height=1, relief="flat", cursor="hand2")
            ready_button.place(relx=0.5, rely=0.9, anchor="center")

            # Function to handle ready button click

        def start_listening(update_ui_callback):
            global mic_active
            if not mic_active:
                mic_active = True  # Enable mic when ready button is clicked
                update_ui_callback("Nova: Listening for your next task...")

                # Capture spoken text only when mic is active
                spoken_text = recognize_speech()  # Begin speech recognition
                handle_task(r, update_ui_callback, stop_main_mic, input_text=spoken_text)

        def handle_next_task(ready_button):
            ready_button.destroy()  # Remove the button after it's clicked
            start_listening(update_ui_callback)  # Re-trigger main loop for next input

        # Task-specific commands based on keywords
        if "calculator" in query_lower:
            update_ui_callback("Nova: Opening Calculator.")
            subprocess.Popen("calc.exe", shell=True)
            add_ready_button()
        elif "control panel" in query_lower:
            update_ui_callback("Nova: Opening Control Panel.")
            subprocess.Popen("control", shell=True)
            add_ready_button()
        elif "game" in query_lower or "games" in query_lower:
            update_ui_callback("Nova: Opening the game website for you.")
            assist = infow()
            assist.play_online_game()
            add_ready_button()
        elif "voice to text" in query_lower or "speech to text" in query_lower:
            update_ui_callback("Nova: Opening voice-to-text converter.")
            open_voice_to_text_window(r, update_ui_callback)
            add_ready_button()
        elif "file explorer" in query_lower:
            update_ui_callback("Nova: Opening File Explorer.")
            subprocess.Popen("explorer", shell=True)
            add_ready_button()
        elif "weather" in query_lower:
            update_ui_callback("Nova: Opening weather information window.")
            open_weather_window(update_ui_callback)
            add_ready_button()
        elif "news" in query_lower or "headline" in query_lower:
            update_ui_callback("Nova: Fetching today's news headlines.")
            try:
                assist = infow()
                headlines = assist.get_news_headlines()
                update_ui_callback(f"Nova: {headlines if headlines else 'No news headlines found.'}")
            except Exception as e:
                update_ui_callback(f"Nova: An error occurred while fetching the news.")
        elif "list" in query_lower and ("tasks" in query_lower or "task" in query_lower):
            tasks_list = (
                "Nova:\n1. BROWSER Search.\n2. Video Call.\n3. YouTube.\n4. News.\n"
                "5. Control Panel Access.\n6. File Explorer.\n7. Voice-to-Text Converter.\n"
                "8. Calculator.\n9. Online Games.\n10. Weather Report.\n11.Set Reminders. \n12.Translator"
            )
            update_ui_callback(tasks_list)
            add_ready_button()
        elif "youtube" in query_lower:
            video_prompt = "What video would you like to play?"
            update_ui_callback(f"Nova: {video_prompt}")

            def youtube_callback(topic):
                update_ui_callback(f"User: {topic}")
                play_prompt = f"Playing a video about {topic} on YouTube."
                update_ui_callback(f"Nova: {play_prompt}")

                assist = infow()
                if assist.play_youtube_video(topic):
                    update_ui_callback("Nova: Video playing completed.")
                    return handle_task(r, update_ui_callback)

            create_input_window("YouTube", youtube_callback)

        elif "translate" in query_lower or "translator" in query_lower:
            stop_main_mic()
            update_ui_callback("Nova: Opening translation window.")
            open_translation_window(update_ui_callback)
            add_ready_button()

        elif "set reminder" in query_lower or "set alarm" in query_lower:
            stop_main_mic()
            update_ui_callback("Nova: Opening reminder setup window.")
            open_reminder_window(update_ui_callback)
            add_ready_button()
        elif "video call" in query_lower:
            stop_main_mic()
            video_call_link = generate_meeting_link()
            update_ui_callback(f"Nova: Starting a video call. Here is your link: {video_call_link}")
            webbrowser.open(video_call_link)
            start_captioning(root)
            add_ready_button()
        elif any(word in query_lower.split() for word in ["what", "when", "where", "why", "how", "who"]):
            # Google Search for informational questions
            update_ui_callback(f"Nova: Searching Google for '{query}'.")
            assist = infow()
            search_results = assist.search_google(query)
            update_ui_callback(f"Nova: {search_results}")
            add_ready_button()
        elif any(word in query_lower for word in ["time", "date"]):
            current_time_and_date = tell_time_and_date()
            update_ui_callback(f"Nova: {current_time_and_date}")
            add_ready_button()
        elif any(word in query_lower for word in ["exit", "stop", "quit", "no", "goodbye", "thank you"]):
            goodbye_prompt = "Okay, thank you! Goodbye!"
            update_ui_callback(f"Nova: {goodbye_prompt}")
            break  # Exit the loop and end the program
        else:
            # Unrecognized command fallback
            update_ui_callback("Nova: Sorry, I didn't catch that. Can you please repeat?")

        # Prompt for further assistance and wait for new input
        follow_up_prompt = "Is there anything else I can help you with?"
        update_ui_callback(f"Nova: {follow_up_prompt}")

        # Wait for next input; reset user_input to avoid reuse
        user_input = None

def open_voice_to_text_window(r, update_ui_callback):
    def start_recording():
        update_ui_callback("Nova: Listening...")
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                text = r.recognize_google(audio)
                text_box.insert(tk.END, text + "\n")
                update_ui_callback(f"Nova: Recognized text - {text}")
        except sr.UnknownValueError:
            update_ui_callback("Nova: Sorry, I could not understand the audio.")
        except sr.RequestError:
            update_ui_callback("Nova: Sorry, there was an error with the speech recognition service.")

    def close_window():
        window.destroy()

    window = tk.Tk()
    window.title("Voice to Text")

    text_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=30)
    text_box.pack(padx=10, pady=10)

    speak_button = tk.Button(window, text="Speak", command=start_recording, bg='green', fg='white')
    speak_button.pack(padx=5, pady=5)

    close_button = tk.Button(window, text="Close", command=close_window, bg='red', fg='white')
    close_button.pack(padx=5, pady=5)

    window.mainloop()


def open_translation_window(update_ui_callback):
    def translate_text():
        text_to_translate = text_entry.get()
        target_lang = lang_var.get()

        if text_to_translate and target_lang:
            translation = perform_translation(text_to_translate, target_lang)
            update_ui_callback(f"Nova: Translation - {translation}")
            result_label.config(text=f"Translated Text: {translation}")
        else:
            update_ui_callback("Nova: Please enter text and select a language.")

    def use_mic():
        text_entry.delete(0, tk.END)
        text_entry.insert(0, recognize_speech())  # Assume recognize_speech() fetches voice input

    # Translation input window
    translation_window = Toplevel()
    translation_window.title("Translate Text")
    translation_window.geometry("350x300")
    translation_window.configure(bg="#d1e7dd")  # Soft green background

    Label(translation_window, text="Enter text to translate:", bg="#d1e7dd", font=("Arial", 10)).pack(pady=5)
    text_entry = Entry(translation_window, width=30, font=("Arial", 10))
    text_entry.pack(pady=5)

    # Mic button for voice input
    mic_image = Image.open("pythonProject1\photos\mic.png")  # Ensure correct path to microphone icon
    mic_image = mic_image.resize((24, 24), Image.LANCZOS)
    mic_icon = ImageTk.PhotoImage(mic_image)

    mic_button = Button(translation_window, image=mic_icon, command=use_mic, bg="#0d6efd", borderwidth=0,
                        activebackground="#0b5ed7")
    mic_button.image = mic_icon
    mic_button.pack(pady=5)

    # Dropdown for language selection
    Label(translation_window, text="Select language:", bg="#d1e7dd", font=("Arial", 10)).pack(pady=5)
    lang_var = StringVar()
    lang_var.set("தமிழ்")  # Default language தமிழ்
    lang_options = ["Spanish", "French","தமிழ்","Chinese", "Japanese"]  # Add language codes as needed
    lang_menu = OptionMenu(translation_window, lang_var, *lang_options)
    lang_menu.pack(pady=5)

    # Translate button
    Button(translation_window, text="Translate", command=translate_text, bg="#0d6efd", fg="white",
           font=("Arial", 10, "bold"), activebackground="#0b5ed7", activeforeground="white").pack(pady=15)

    # Label to show translation result
    result_label = Label(translation_window, text="Translated Text:", bg="#d1e7dd", font=("Arial", 10, "italic"))
    result_label.pack(pady=10)


def perform_translation(text, dest_lang):
    translator = Translator()
    try:
        result = translator.translate(text, dest=dest_lang)
        return result.text
    except Exception as e:
        return f"Error in translation: {e}"


def open_reminder_window(update_ui_callback):
    def set_reminder():
        reminder_text = reminder_name_entry.get()
        reminder_date = reminder_date_entry.get()
        reminder_time = reminder_time_entry.get()

        if reminder_text and reminder_date and reminder_time:
            reminder_datetime_str = f"{reminder_date} {reminder_time}"
            set_reminder_task(reminder_text, reminder_datetime_str, update_ui_callback)
            reminder_window.destroy()
        else:
            update_ui_callback("Nova: Please fill out all fields.")

    # Create reminder input window
    reminder_window = Toplevel()
    reminder_window.title("Set Reminder")
    reminder_window.geometry("350x250")
    reminder_window.configure(bg="#ffebcd")  # Light background color

    Label(reminder_window, text="Reminder Name:", bg="#ffebcd", font=("Arial", 10)).pack(pady=5)
    reminder_name_entry = Entry(reminder_window, width=30, font=("Arial", 10))
    reminder_name_entry.pack(pady=5)

    Label(reminder_window, text="Date (YYYY-MM-DD):", bg="#ffebcd", font=("Arial", 10)).pack(pady=5)
    reminder_date_entry = Entry(reminder_window, width=30, font=("Arial", 10))
    reminder_date_entry.pack(pady=5)

    Label(reminder_window, text="Time (HH:MM):", bg="#ffebcd", font=("Arial", 10)).pack(pady=5)
    reminder_time_entry = Entry(reminder_window, width=30, font=("Arial", 10))
    reminder_time_entry.pack(pady=5)

    Button(reminder_window, text="Set Reminder", command=set_reminder, bg="#ff6347", fg="white",
           font=("Arial", 10, "bold"), activebackground="#cd5c5c").pack(pady=20)


def set_reminder_task(reminder_text, reminder_datetime_str, update_ui_callback):
    def reminder_task():
        delay = (reminder_datetime - datetime.now()).total_seconds()
        if delay > 0:
            threading.Timer(delay, show_reminder, [reminder_text, update_ui_callback]).start()
            update_ui_callback(f"Nova: Reminder set for {reminder_datetime_str}")
        else:
            update_ui_callback("Nova: Reminder time is in the past. Enter a future time.")

    reminder_datetime = datetime.strptime(reminder_datetime_str, "%Y-%m-%d %H:%M")
    reminder_task()


def show_reminder(reminder_text, update_ui_callback):
    update_ui_callback(f"Nova: Reminder - {reminder_text}")
    messagebox.showinfo("Reminder", reminder_text)  # Display popup alert

def open_weather_window(update_ui_callback):
    def get_weather():
        location = location_var.get()
        if location:
            weather_info = selenium_w.infow.fetch_weather(city=location)
            update_ui_callback(f"Nova: {weather_info}")
            weather_window.destroy()
        else:
            update_ui_callback("Nova: Please select a location.")

    weather_window = Toplevel()
    weather_window.title("Weather Information")
    weather_window.geometry("320x250")
    weather_window.configure(bg="#e0f7fa")  # Light blue background

    Label(weather_window, text="Select location for weather:", bg="#e0f7fa", fg="#00796b",
          font=("Arial", 12, "bold")).pack(pady=(15, 5))

    # Dropdown for cities in Tamil Nadu
    location_var = StringVar()
    location_var.set("Chennai")  # Default city
    cities = ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Tiruppur", "Vellore",
              "Thoothukudi", "Erode"]
    city_menu = OptionMenu(weather_window, location_var, *cities)
    city_menu.config(bg="#00796b", fg="white", font=("Arial", 10, "bold"), activebackground="#004d40")
    city_menu.pack(pady=10)

    Button(weather_window, text="Get Weather", command=get_weather, bg="#00796b", fg="white",
           font=("Arial", 10, "bold"), activebackground="#004d40", activeforeground="white", padx=10, pady=5).pack(pady=15)


def main(update_ui_callback,stop_main_mic,user_input):
    global r
    r = sr.Recognizer()

    intro_prompt = "I am Nova, your voice assistant. What can I do for you?"
    update_ui_callback(f"Nova: {intro_prompt}")
    update_ui_callback("Nova: Listening...")
    while True:
        exit_program = handle_task(r, update_ui_callback,stop_main_mic,user_input)
        if exit_program:
            break


class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.r = sr.Recognizer()
        self.is_mic_on = True
        self.root.title("Voice Assistant")
        self.video_path = "D:/projects/voice assistant/pythonProject1/photos/back.mp4"
        self.mic_active = False
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

        # Hide the main window and show login window first
        self.root.withdraw()
        self.show_login_window()
        self.create_profile_card()

    def show_login_window(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        self.login_window.geometry("800x600")
        self.login_window.configure(bg="#04D8B2")
        self.center_window(self.login_window, 800, 600)

        tk.Label(self.login_window, text="Username:", font=("Helvetica", 14), bg="#f0f0f5").pack(pady=25)
        self.username_entry = tk.Entry(self.login_window, font=("Helvetica", 14))
        self.username_entry.pack(pady=10)

        tk.Label(self.login_window, text="Enter Password:", font=("Helvetica", 14), bg="#f0f0f5").pack(pady=25)
        self.password_entry = tk.Entry(self.login_window, show='*', font=("Helvetica", 14))
        self.password_entry.pack(pady=10)

        button_frame = tk.Frame(self.login_window, bg="#f0f0f5")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Sign In", command=self.sign_in, font=("Helvetica", 14), bg="#2196F3",
                  fg="white").pack(side="left", padx=10)
        tk.Button(button_frame, text="Sign Up", command=self.sign_up, font=("Helvetica", 14), bg="#FF5722",
                  fg="white").pack(side="right", padx=10)

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

    def start_voice_input(self):
        if self.is_mic_on:
            self.update_ui("Nova: Listening for your command...")
            threading.Thread(target=self.listen_for_command).start()

    def listen_for_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            try:
                command = r.recognize_google(audio)
                self.update_ui(f"User: {command}")
                self.process_input(command)
            except sr.UnknownValueError:
                self.update_ui("Nova: Could not understand audio.")
            except sr.RequestError:
                self.update_ui("Nova: Could not request results; check your network connection.")

    def stop_main_mic(self):
        self.is_mic_on = False

    def sign_in(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in users_db and users_db[username] == password:
            self.login_window.destroy()
            self.root.deiconify()
            self.setup_main_window()
        else:
            messagebox.showerror("Login Error", "Invalid username or password.")

    def sign_up(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in users_db:
            messagebox.showerror("Sign Up Error", "Username already exists.")
        else:
            users_db[username] = password
            messagebox.showinfo("Sign Up Success", "Account created successfully. You can now sign in.")

    def setup_main_window(self):
        self.canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.canvas.pack(fill=tk.BOTH, expand=True)
        video_thread = threading.Thread(target=self.play_video_background, daemon=True)
        video_thread.start()
        self.start_assistant()
        self.setup_gui()

    def create_profile_card(self):
        profile_frame = tk.Frame(self.root, bg="#f0f0f0", highlightbackground="#000", highlightthickness=1)
        profile_frame.place(x=20, y=20, width=250, height=100)

        try:
            img = Image.open("D:/projects/voice assistant/pythonProject1/photos/user.png")
            img = img.resize((60, 60), Image.LANCZOS)
            profile_image = ImageTk.PhotoImage(img)
            img_label = tk.Label(profile_frame, image=profile_image, bg="#f0f0f0")
            img_label.image = profile_image
            img_label.place(x=10, y=20)
        except Exception as e:
            print(f"Error loading profile image: {e}")

        username_label = tk.Label(profile_frame, text="Username", font=("Arial", 12, "bold"), bg="#f0f0f0")
        username_label.place(x=80, y=35)

        menu_button = tk.Button(profile_frame, text="⋮", font=("Arial", 12), bg="#f0f0f0", borderwidth=0,
                                command=self.show_menu)
        menu_button.place(x=220, y=10)

    def show_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg="#ffffff", font=("Arial", 10))
        menu.add_command(label="Logout", command=self.logout)
        menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def logout(self):
        confirm = tk.messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if confirm:
            self.root.destroy()
            self.show_login_window()

    def play_video_background(self):
        cap = cv2.VideoCapture(self.video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            frame = cv2.resize(frame, (self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            self.canvas.image = img_tk
            self.root.update_idletasks()
            self.root.update()
        cap.release()

    def submit_input(self):
        user_input = self.user_input_box.get()
        if user_input:
            self.update_ui(f"User: {user_input}")
            self.user_input_box.delete(0, tk.END)
            self.process_input(user_input)

    def process_input(self, user_input):
        if user_input:
            self.update_ui(f"User: {user_input}")
            exit_program = handle_task(self.r, self.update_ui, self.stop_main_mic, user_input)
            if exit_program:
                self.root.quit()

    def setup_gui(self):
        self.ellie_image_path = "D:/projects/voice assistant/pythonProject1/photos/nova.jfif"
        self.user_image_path = "D:/projects/voice assistant/pythonProject1/photos/user.png"

        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)

        self.ellie_image = self.load_image(self.ellie_image_path, (50, 50))
        self.user_image = self.load_image(self.user_image_path, (50, 50))

        self.profile_card = tk.Frame(self.root, bg="lightblue", width=200, height=750)
        self.profile_card.place(relx=0.05, rely=0.5, anchor=tk.W)

        self.profile_frame_inner = tk.Frame(self.profile_card, bg="white", relief="groove", bd=2)
        self.profile_frame_inner.pack(fill="both", expand=True, padx=10, pady=10)

        self.profile_image = self.load_image(self.user_image_path, (80, 80))
        self.profile_image_label = tk.Label(self.profile_frame_inner, image=self.profile_image, bg="white")
        self.profile_image_label.pack(pady=10)

        self.username_label = tk.Label(self.profile_frame_inner, text="Username", font=("Arial", 14), bg="white", fg="black")
        self.username_label.pack(pady=5)

        self.options_button = tk.Button(self.profile_frame_inner, text="⋮", font=("Arial", 16), bg="white", fg="black",
                                        relief="flat", command=self.show_options)
        self.options_button.pack(pady=5)

        self.logout_button = tk.Button(self.profile_frame_inner, text="Logout", font=("Arial", 12), bg="red",
                                       fg="white", command=self.logout, relief="flat")
        self.logout_button.pack(pady=5)
        self.logout_button.pack_forget()

        self.text_box = tk.Text(self.root, wrap=tk.WORD, bg="white", fg="gold", font=("Helvetica", 12))
        self.text_box.place(relx=0.3, rely=0.5, anchor=tk.W, width=800, height=750)

        self.text_box.tag_configure("Nova", foreground="blue")
        self.text_box.tag_configure("user", foreground="green")

        self.text_box.insert(tk.END, "Welcome to the Voice Assistant\n", "Nova")
        self.text_box.configure(state=tk.DISABLED)

        ready_button = tk.Button(self.root, text="Ready", command=self.start_voice_input,
                                 bg="#40E0D0", fg="black", font=("Arial", 10, "bold"),
                                 borderwidth=0, highlightthickness=0, relief="flat", cursor="hand2")
        ready_button.config(width=12, height=1, relief="flat")
        ready_button.place(relx=0.5, rely=0.9, anchor="center")

    def show_options(self):
        if self.logout_button.winfo_viewable():
            self.logout_button.pack_forget()
        else:
            self.logout_button.pack(pady=5)

    def load_image(self, path, size):
        try:
            image = Image.open(path).convert("RGBA")
            image = image.resize(size, Image.LANCZOS)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            result = Image.new('RGBA', size)
            result.paste(image, (0, 0), mask)
            return ImageTk.PhotoImage(result)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    def update_ui(self, message):
        if hasattr(self, 'text_box'):
            self.text_box.configure(state=tk.NORMAL)
            if message.startswith("Nova:"):
                self.text_box.image_create(tk.END, image=self.ellie_image)
                self.text_box.insert(tk.END, f" {message}\n", "Nova")
            elif message.startswith("User:"):
                self.text_box.image_create(tk.END, image=self.user_image)
                self.text_box.insert(tk.END, f" {message}\n", "user")
            else:
                self.text_box.insert(tk.END, f"{message}\n", "Nova")
            self.text_box.configure(state=tk.DISABLED)
            self.text_box.see(tk.END)

    def start_assistant(self):
        import threading
        threading.Thread(target=self.main).start()

    def main(self):
        global r
        r = sr.Recognizer()
        intro_prompt = "Hello, I am Nova, your voice assistant. What can I do for you?"
        self.update_ui(f"Nova: {intro_prompt}")
        while True:
            exit_program = handle_task(r, self.update_ui, self.stop_main_mic)
            if exit_program:
                break

# Start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()
