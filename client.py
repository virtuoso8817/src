import socket
import tkinter as tk
from tkinter import messagebox,simpledialog, filedialog
import threading
from encryption import encrypt_message, decrypt_message  # Import encryption functions
from datetime import datetime
import pygame
import os
import wave



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))

client_username = simpledialog.askstring("Username Setup", "Enter client username:")

if not client_username:
    client_username = "Client"

print(f"Client username set as: {client_username}")

# Add these global variables and functions to both client.py and server.py
is_paused = False


def open_audio_player(file_path):
    # Load audio to get duration (supports WAV/MP3 via pygame)
    try:
        sound = pygame.mixer.Sound(file_path)
        duration = sound.get_length()  # in seconds
        sound = None  # Free resources
    except Exception as e:
        messagebox.showerror("Error", f"Could not load audio: {e}")
        return

    # Convert duration to MM:SS format
    mins, secs = divmod(int(duration), 60)
    duration_str = f"{mins:02d}:{secs:02d}"

    # Player window setup
    player = tk.Toplevel()
    player.title("🎵 Audio Player")
    player.configure(bg="#2E2E2E")
    player.resizable(False, False)

    # Styling variables
    bg_color = "#2E2E2E"
    fg_color = "white"
    accent_color = "#4CAF50"
    progress_bg = "#404040"

    # Header with filename
    tk.Label(
        player,
        text=os.path.basename(file_path),
        bg=bg_color,
        fg=fg_color,
        font=("Arial", 10, "bold")
    ).pack(pady=10)

    # Time display frame
    time_frame = tk.Frame(player, bg=bg_color)
    time_frame.pack(pady=5)

    current_time = tk.Label(time_frame, text="00:00", bg=bg_color, fg=fg_color)
    current_time.pack(side=tk.LEFT)

    tk.Label(time_frame, text="/", bg=bg_color, fg=fg_color).pack(side=tk.LEFT)
    total_time = tk.Label(time_frame, text=duration_str, bg=bg_color, fg=fg_color)
    total_time.pack(side=tk.LEFT)

    # Progress bar (Canvas-based)
    progress_canvas = tk.Canvas(
        player,
        height=8,
        width=300,
        bg=progress_bg,
        highlightthickness=0
    )
    progress_canvas.pack(pady=5, padx=10)
    progress_line = progress_canvas.create_rectangle(0, 0, 0, 8, fill=accent_color, outline="")

    # Volume control
    volume_frame = tk.Frame(player, bg=bg_color)
    volume_frame.pack(pady=10)
    tk.Label(volume_frame, text="🔊", bg=bg_color, fg=fg_color).pack(side=tk.LEFT)
    volume_slider = tk.Scale(
        volume_frame,
        from_=0,
        to=100,
        orient=tk.HORIZONTAL,
        bg=bg_color,
        fg=fg_color,
        troughcolor=progress_bg,
        command=lambda v: pygame.mixer.music.set_volume(float(v)/100))
    volume_slider.set(100)
    volume_slider.pack(side=tk.LEFT)

    # Control buttons
    btn_frame = tk.Frame(player, bg=bg_color)
    btn_frame.pack(pady=10)

    # Play/Pause/Stop buttons with modern symbols
    play_btn = tk.Button(
        btn_frame,
        text="▶",
        font=("Arial", 14),
        bg=accent_color,
        fg=fg_color,
        borderwidth=0,
        command=lambda: play()
    )
    play_btn.pack(side=tk.LEFT, padx=5)

    pause_btn = tk.Button(
        btn_frame,
        text="⏸",
        font=("Arial", 14),
        bg=accent_color,
        fg=fg_color,
        borderwidth=0,
        command=lambda: pause_resume()
    )
    pause_btn.pack(side=tk.LEFT, padx=5)

    stop_btn = tk.Button(
        btn_frame,
        text="⏹",
        font=("Arial", 14),
        bg=accent_color,
        fg=fg_color,
        borderwidth=0,
        command=lambda: stop()
    )
    stop_btn.pack(side=tk.LEFT, padx=5)

    # Update progress bar
    def update_progress():
        if pygame.mixer.music.get_busy() and not is_paused:
            current_pos = pygame.mixer.music.get_pos()/1000  # Convert to seconds
            progress = (current_pos / duration) * 300  # 300 = canvas width
            progress_canvas.coords(progress_line, 0, 0, progress, 8)

            # Update time label
            mins, secs = divmod(int(current_pos), 60)
            current_time.config(text=f"{mins:02d}:{secs:02d}")
            player.after(200, update_progress)  # Update every 200ms
        elif is_paused:
            player.after(200, update_progress)  # Keep checking if unpaused

    def play():
        global is_paused
        try:
            if is_paused:
                pygame.mixer.music.unpause()
                is_paused = False
            else:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
            update_progress()
        except Exception as e:
            messagebox.showerror("Error", f"Playback error: {e}")

    def pause_resume():
        global is_paused
        if not is_paused:
            pygame.mixer.music.pause()
            is_paused = True
        else:
            pygame.mixer.music.unpause()
            is_paused = False

    def stop():
        global is_paused
        pygame.mixer.music.stop()
        is_paused = False
        progress_canvas.coords(progress_line, 0, 0, 0, 8)
        current_time.config(text="00:00")

    # Handle window close
    player.protocol("WM_DELETE_WINDOW", lambda: (stop(), player.destroy()))



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
                entry.delete(0, tk.END);
            except BrokenPipeError:
                messagebox.showerror("Error", "Connection lost! Please restart the client.")
                return

            # Try receiving server response
            # try:
            #     response = client_socket.recv(1024).decode()  # Receive response
            #     decrypt_response = decrypt_message(response)  # Decrypt response
            # except ConnectionResetError:
            #     messagebox.showerror("Error", "Server closed the connection unexpectedly!")
            #     return


            # chat_history.insert(tk.END, f"{get_timestamp()}Server: {decrypt_response}\n", "server_message")
            entry.delete(0, tk.END)  # Clear input field

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected Error: {e}")

    threading.Thread(target=send, daemon=True).start()


# def receive_messages():
#     while True:
#         try:
#             response = client_socket.recv(1024).decode()
#             if not response:
#                 break
#             decrypted_response = decrypt_message(response)  # Decrypt incoming message
#             pygame.mixer.music.play()  # Play notification sound
#             chat_history.insert(tk.END, f"{get_timestamp()}Server: {decrypted_response}\n", "server_message")
#         except:
#             break

def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            if data.startswith(b"FILE::"):
                try:
                    header_end = data.index(b'\n')
                except ValueError:
                    header_end = len(data)
                header = data[:header_end].decode().strip()
                parts = header.split("::")
                if len(parts) < 4:
                    continue
                file_type, file_name, file_size = parts[1], parts[2], int(parts[3])
                file_data = data[header_end+1:]

                os.makedirs("received_files", exist_ok=True)
                file_path = os.path.join("received_files", file_name)

                with open(file_path, 'wb') as f:
                    f.write(file_data)
                    received = len(file_data)
                    while received < file_size:
                        chunk = client_socket.recv(min(1024, file_size - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                if file_type == "Audio":
                    chat_history.insert(tk.END, f"{get_timestamp()}Received {file_type}: {file_name}\n", "info")
                    chat_history.insert(tk.END, f"Click to play: {file_name}\n", "audio_hyperlink")
                    chat_history.tag_config("audio_hyperlink", foreground="purple", underline=1)
                    chat_history.tag_bind("audio_hyperlink", "<Button-1>",
                                          lambda e, fp=file_path: open_audio_player(fp))

                chat_history.insert(tk.END, f"{get_timestamp()}Received {file_type}: {file_name}\n", "info")
                chat_history.insert(tk.END, f"Click to open: {file_name}\n", "hyperlink")
                chat_history.tag_config("hyperlink", foreground="blue", underline=1)
                chat_history.tag_bind("hyperlink", "<Button-1>", lambda e, fp=file_path: os.startfile(fp))
                pygame.mixer.music.play()
            else:
                try:
                    response = data.decode()
                    decrypted_response = decrypt_message(response)
                    chat_history.insert(tk.END, f"{get_timestamp()}Server: {decrypted_response}\n", "server_message")
                except Exception as e:
                    print(f"Decryption error: {e}")
        except ConnectionResetError:
            break
        except Exception as e:
            print(f"Error: {e}")
            break




threading.Thread(target=receive_messages, daemon=True).start()

# Tkinter UI
root = tk.Tk()
root.title(" Chat Client")
root.geometry("400x600")
root.configure(bg="#f0f0f0")

# Styling
font_style = ("Arial", 12)



def attach_audio():
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=(("WAV files", "*.wav"), ("MP3 files", "*.mp3"), ("All files", "*.*")))
    if not file_path:
        return
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_type = "Audio"

        # Send file header
        header = f"FILE::{file_type}::{file_name}::{file_size}\n".encode()
        client_socket.sendall(header)

        # Send file in chunks
        with open(file_path, "rb") as file:
            while chunk := file.read(1024):
                client_socket.sendall(chunk)

        chat_history.insert(tk.END, f"Sent {file_type}: {file_name}\n", "info")
    except Exception as e:
        chat_history.insert(tk.END, f"Error sending {file_type}: {e}\n", "error")




def attach_image():
    file_path = tk.filedialog.askopenfilename(title="Select Image File",
                                              filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"),
                                                         ("All files", "*.*")))
    if not file_path:
        return

    try:
        file_name = file_path.split("/")[-1]
        file_size = os.path.getsize(file_path)
        file_type = "Image"

        # Send file header
        header = f"FILE::{file_type}::{file_name}::{file_size}".encode()
        client_socket.sendall(header + b"\n")

        # Send the file in chunks
        with open(file_path, "rb") as file:
            while chunk := file.read(1024):
                client_socket.sendall(chunk)

        chat_history.insert(tk.END, f"Sent {file_type}: {file_name}\n", "info")
    except Exception as e:
        chat_history.insert(tk.END, f"Error sending {file_type}: {e}\n", "error")

def save_chat_history():
    try:
        with open("chat_history.txt", "w", encoding="utf-8") as file:
            file.write(chat_history.get(1.0, tk.END))
        messagebox.showinfo("Info", "Chat history saved to chat_history.txt")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save chat history: {e}")

save_button = tk.Button(root, text="Save Chat", font=font_style, bg="#4CAF50", fg="white", command=save_chat_history)
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
send_button.pack(side=tk.RIGHT, pady = 5)

attach_button = tk.Button(entry_frame, text="Attach", font=font_style, bg="#4CAF50", fg="white", command=attach_image)
attach_button.pack(side=tk.RIGHT, padx=5)

attach_audio_button = tk.Button(
    entry_frame, text="Attach Audio", font=font_style,
    bg="#4CAF50", fg="white", command=attach_audio
)
attach_audio_button.pack(side=tk.RIGHT, padx=5)



def toggle_theme():
    current_bg = chat_history.cget("bg")
    if current_bg == "white":
        chat_history.config(bg="black", fg="white")
    else:
        chat_history.config(bg="white", fg="black")

theme_button = tk.Button(root, text="Toggle Theme",font=font_style, bg="#4CAF50", fg="white", command=toggle_theme)
theme_button.pack()

def clear_chat():
    chat_history.delete(1.0, tk.END)

clear_button = tk.Button(root, text="Clear Chat",font=font_style, bg="#4CAF50", fg="white", command=clear_chat)
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






