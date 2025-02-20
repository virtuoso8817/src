import socket
import tkinter as tk
from tkinter import messagebox,simpledialog
import threading
from encryption import encrypt_message, decrypt_message  # Import encryption functions
from datetime import datetime
import pygame
import wave



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))

client_username = simpledialog.askstring("Username Setup", "Enter client username:")

if not client_username:
    client_username = "Client"

print(f"Client username set as: {client_username}")




def get_timestamp():
    return datetime.now().strftime("[%H:%M:%S] ")

# Initialize pygame mixer
pygame.mixer.init()

# Load the notification sound
notification_sound = "notification1.mp3"  # Replace with a valid sound file
pygame.mixer.music.load(notification_sound)
def send_message():
    def send():
        try:
            message = entry.get()
            if not message:
                messagebox.showwarning("Warning", "Message cannot be empty!")
                return

            # Immediately display sent message in chat historys
            chat_history.insert(tk.END, f"{get_timestamp()}{client_username}: {message}\n", "user_message")

            # Try sending message
            try:
                encrypted_message = encrypt_message(message)  # Encrypt user input
                client_socket.send(encrypted_message.encode())  # Send user input to server
            except BrokenPipeError:
                messagebox.showerror("Error", "Connection lost! Please restart the client.")
                return

            # Try receiving server response
            try:
                response = client_socket.recv(1024).decode()  # Receive response
                decrypt_response = decrypt_message(response)  # Decrypt response
            except ConnectionResetError:
                messagebox.showerror("Error", "Server closed the connection unexpectedly!")
                return


            chat_history.insert(tk.END, f"{get_timestamp()}Server: {decrypt_response}\n", "server_message")
            entry.delete(0, tk.END)  # Clear input field

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected Error: {e}")

    threading.Thread(target=send, daemon=True).start()


def receive_messages():
    while True:
        try:
            response = client_socket.recv(1024).decode()
            if not response:
                break
            decrypted_response = decrypt_message(response)  # Decrypt incoming message
            pygame.mixer.music.play()  # Play notification sound
            chat_history.insert(tk.END, f"{get_timestamp()}Server: {decrypted_response}\n", "server_message")
        except:
            break





threading.Thread(target=receive_messages, daemon=True).start()

# Tkinter UI
root = tk.Tk()
root.title(" Chat Client")
root.geometry("400x600")
root.configure(bg="#f0f0f0")

# Styling
font_style = ("Arial", 12)


def save_chat_history():
    try:
        with open("chat_history.txt", "w", encoding="utf-8") as file:
            file.write(chat_history.get(1.0, tk.END))
        messagebox.showinfo("Info", "Chat history saved to chat_history.txt")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save chat history: {e}")

save_button = tk.Button(root, text="Save Chat", font=font_style, bg="#FF5733", fg="white", command=save_chat_history)
save_button.pack(pady=5)


# Header Label
header = tk.Label(root, text="Client Chat", font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", pady=10)
header.pack(fill=tk.X)

# Chat History (Text Box)
chat_frame = tk.Frame(root, padx=10, pady=5, bg="#f0f0f0")
chat_frame.pack(fill=tk.BOTH, expand=True)

chat_history = tk.Text(chat_frame, height=15, width=50, font=font_style, wrap=tk.WORD)
chat_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(chat_frame, command=chat_history.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chat_history.config(yscrollcommand=scrollbar.set)

# Text Entry Box
entry_frame = tk.Frame(root, bg="#f0f0f0", padx=10, pady=5)
entry_frame.pack(fill=tk.X)

entry = tk.Entry(entry_frame, font=font_style, width=30)
entry.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)

send_button = tk.Button(entry_frame, text="Send", font=font_style, bg="#4CAF50", fg="white", command=send_message)
send_button.pack(side=tk.RIGHT, padx=5)


def toggle_theme():
    current_bg = chat_history.cget("bg")
    if current_bg == "white":
        chat_history.config(bg="black", fg="white")
    else:
        chat_history.config(bg="white", fg="black")

theme_button = tk.Button(root, text="Toggle Theme",font=font_style, bg="#FF5733", fg="white", command=toggle_theme)
theme_button.pack()

def clear_chat():
    chat_history.delete(1.0, tk.END)

clear_button = tk.Button(root, text="Clear Chat",font=font_style, bg="#FF5733", fg="white", command=clear_chat)
clear_button.pack()



def on_typing(event):
    typing_label.config(text="You are typing...")
    root.after(2000, lambda: typing_label.config(text=""))

entry.bind("<KeyPress>", on_typing)
typing_label = tk.Label(root, text="")
typing_label.pack()

def insert_emoji(emoji):
    """Insert the selected emoji into the entry box."""
    entry.insert(tk.END, emoji)

# Frame for emoji buttons
emoji_frame = tk.Frame(root)
emoji_frame.pack()

# List of emojis to display
emojis = ["😀", "😂", "👍", "❤️", "🎉", "🥳", "😎", "😢", "🔥", "💯"]

# Create emoji buttons
for emoji in emojis:
    button = tk.Button(emoji_frame, text=emoji, font=("Arial", 14), command=lambda e=emoji: insert_emoji(e))
    button.pack(side=tk.LEFT, padx=2, pady=2)

# Text Color Formatting
chat_history.tag_config("user_message", foreground="blue")
chat_history.tag_config("server_message", foreground="green")

root.mainloop()






