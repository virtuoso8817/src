import socket
import threading
import tkinter as tk
from tkinter import messagebox,simpledialog
from encryption import encrypt_message, decrypt_message
from datetime import datetime
import pygame
import os



HOST = "127.0.0.1"  # Localhost
PORT = 12345        # Port number

# Create a socket (IPv4, TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))  # Bind to the address
server_socket.listen(5)           # Listen for connections

print(f"Server is listening on {HOST}:{PORT}...")

client_socket, client_address = server_socket.accept()
print(f"Connected to {client_address}")



# Prompt for username inside the main Tkinter window
server_username = simpledialog.askstring("Username Setup", "Enter server username:")

if not server_username:
    server_username = "Server"  # Default username if none provided

print(f"Server username set as: {server_username}")




# Initialize pygame mixer
pygame.mixer.init()

# Load the notification sound


notification_sound = "notification1.mp3"  # Replace with a valid sound file
pygame.mixer.music.load(notification_sound)
"""
try:
    notification_sound = pygame.mixer.Sound(notification_sound)
except pygame.error as e:
    print(f"Error loading sound: {e}") """

'''
def play_notification():
    """Play the notification sound in a separate thread."""

    def play():
        try:
            notification_sound.play()
        except pygame.error as e:
            print(f"Sound playback error: {e}")

    threading.Thread(target=play, daemon=True).start()
'''


# Tkinter UI Setup
root = tk.Tk()
root.title("Server Chat")
root.geometry("400x600")
root.configure(bg="#f0f0f0")

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
header = tk.Label(root, text="Server Chat", font=("Arial", 16, "bold"), bg="#FF5733", fg="white", pady=10)
header.pack(fill=tk.X)

# Chat History
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

def get_timestamp():
    return datetime.now().strftime("[%H:%M:%S] ")
# Function to send messages from server
def send_message():
    def send():
        try:
            message = entry.get()
            if not message:
                messagebox.showwarning("Warning", "Message cannot be empty!")
                return

            encrypted_message = encrypt_message(message)
            client_socket.send(encrypted_message.encode())  # Send message to client

            # Display message in chat history
            chat_history.insert(tk.END, f"{get_timestamp()}{server_username}: {message}\n", "server_message")
            entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Error sending message: {e}")

    threading.Thread(target=send, daemon=True).start()

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


















send_button = tk.Button(entry_frame, text="Send", font=font_style, bg="#FF5733", fg="white", command=send_message)
send_button.pack(side=tk.RIGHT, padx=5)

# Function to receive messages from the client
def receive_messages():
    while True:
        try:
            response = client_socket.recv(1024).decode()
            if not response:
                break

            decrypted_response = decrypt_message(response)
            # Play notification sound
            pygame.mixer.music.play()
            chat_history.insert(tk.END, f"{get_timestamp()}Client: {decrypted_response}\n", "client_message")

        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()
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
chat_history.tag_config("server_message", foreground="red")   # Server messages in red
chat_history.tag_config("client_message", foreground="green")  # Client messages in green

root.mainloop()


