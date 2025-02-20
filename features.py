import os
import socket
import tkinter as tk
from tkinter import filedialog
from encryption import encrypt_message, decrypt_message

BUFFER_SIZE = 4096


def send_file(sock, chat_history, file_type):
    """Send audio, image, or PDF file."""
    file_path = filedialog.askopenfilename(
        title=f"Select {file_type} File",
        filetypes=[("Supported Files", "*.png;*.jpg;*.jpeg;*.mp3;*.wav;*.pdf")]
    )
    if not file_path:
        return

    try:
        # Get file size and name
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # Send file header: FILE::TYPE::name::size
        header = f"FILE::{file_type}::{file_name}::{file_size}".encode()
        sock.sendall(header + b"\n")

        # Send the file in chunks
        with open(file_path, "rb") as file:
            while chunk := file.read(BUFFER_SIZE):
                sock.sendall(chunk)

        chat_history.insert(tk.END, f"Sent {file_type}: {file_name}\n", "info")
    except Exception as e:
        chat_history.insert(tk.END, f"Error sending {file_type}: {e}\n", "error")


def receive_file(sock, chat_history):
    """Receive file (audio, image, PDF) and show as clickable link."""
    try:
        # Read the file header (ends with newline)
        header = sock.recv(BUFFER_SIZE).decode().strip()
        if not header.startswith("FILE::"):
            return  # Not a file transfer

        _, file_type, file_name, file_size = header.split("::")
        file_size = int(file_size)

        received_bytes = 0
        file_path = f"received_{file_name}"

        with open(file_path, "wb") as file:
            while received_bytes < file_size:
                chunk = sock.recv(BUFFER_SIZE)
                if not chunk:
                    break
                file.write(chunk)
                received_bytes += len(chunk)

        # Show clickable link
        chat_history.insert(tk.END, f"Received {file_type}: ")
        chat_history.insert(tk.END, f"{file_name}\n", ("file_link", file_path))
        chat_history.tag_config("file_link", foreground="blue", underline=True)
        chat_history.tag_bind("file_link", "<Button-1>", lambda e, path=file_path: os.startfile(path))
    except Exception as e:
        chat_history.insert(tk.END, f"Error receiving file: {e}\n", "error")


def send_message(sock, message, username):
    """Send an encrypted text message."""
    encrypted_msg = encrypt_message(f"{username}: {message}")
    sock.sendall(encrypted_msg.encode())


def receive_message(sock, chat_history):
    """Receive and decrypt a text message."""
    try:
        encrypted_msg = sock.recv(BUFFER_SIZE).decode()
        if encrypted_msg:
            decrypted_msg = decrypt_message(encrypted_msg)
            chat_history.insert(tk.END, decrypted_msg + "\n", "message")
    except Exception as e:
        chat_history.insert(tk.END, f"Error receiving message: {e}\n", "error")
