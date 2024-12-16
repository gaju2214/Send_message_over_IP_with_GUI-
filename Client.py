import socket
import tkinter as tk
from tkinter import messagebox
import json
import logging

# Configure logging
logging.basicConfig(filename='message_log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

addresses_file = 'ClientAddress.json'

try:
    with open(addresses_file, 'r') as file:
        addresses = json.load(file)
except FileNotFoundError:
    addresses = {
    }

def save_addresses():
    with open(addresses_file, 'w') as file:
        json.dump(addresses, file)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('10.254.254.254', 1))  # Dummy IP address for connection
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        logging.error(f"Error getting local IP address: {e}")
        return None

def get_sender_name(local_ip):
    for name, ip in addresses.items():
        if ip == local_ip:
            return name
    return "Unknown Sender"

def send_message(sender_name, ip_address, message):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 9999
        client_socket.connect((ip_address, port))

        full_message = f"{sender_name}: {message}"
        client_socket.send(full_message.encode('utf-8'))
        logging.debug(f"Sent message: {full_message} to {ip_address}")

        client_socket.close()

        log_message = f"Message sent to {ip_address}: {full_message}"
        logging.info(log_message)

        messagebox.showinfo("Success", f"Message sent successfully to {ip_address}!")
    except Exception as e:
        error_message = f"Error sending message to {ip_address}: {e}"
        logging.error(error_message)
        messagebox.showerror("Error", error_message)

def setup_gui():
    root = tk.Tk()
    root.title("Message Sender")

    local_ip = get_local_ip()
    sender_name = get_sender_name(local_ip)

    tk.Label(root, text=f"Sender Name: {sender_name}").grid(row=0, column=0, padx=10, pady=10)

    message_entries = {}
    buttons = []

    def refresh_gui():
        for widget in root.winfo_children():
            widget.destroy()

        tk.Label(root, text=f"Sender Name: {sender_name}").grid(row=0, column=0, padx=10, pady=10)

        row = 1
        for name, ip_address in addresses.items():
            def on_name_click(name, ip, entry):
                def handler():
                    message = entry.get().strip()
                    if message:
                        send_message(sender_name, ip, message)
                    else:
                        messagebox.showerror("Error", "Message cannot be empty")
                return handler

            def on_remove_click(name):
                def handler():
                    del addresses[name]
                    save_addresses()
                    refresh_gui()
                return handler
            
            message_entry = tk.Entry(root, width=30)
            message_entry.grid(row=row, column=0, padx=10, pady=10)
            
            button = tk.Button(root, text=f" {name}", command=on_name_click(name, ip_address, message_entry))
            button.grid(row=row, column=1, padx=10, pady=10)
            
            remove_button = tk.Button(root, text="Remove", command=on_remove_click(name))
            remove_button.grid(row=row, column=2, padx=10, pady=10)

            message_entries[name] = message_entry
            buttons.append((button, remove_button))
            row += 1

        tk.Label(root, text="Add Computer Name:").grid(row=row, column=0, padx=10, pady=10)
        tk.Label(root, text="Add IP Address:").grid(row=row, column=1, padx=10, pady=10)

        new_name_entry = tk.Entry(root, width=15)
        new_name_entry.grid(row=row+1, column=0, padx=10, pady=10)
        new_ip_entry = tk.Entry(root, width=15)
        new_ip_entry.grid(row=row+1, column=1, padx=10, pady=10)

        def add_computer():
            name = new_name_entry.get().strip()
            ip_address = new_ip_entry.get().strip()

            if name and ip_address:
                addresses[name] = ip_address
                save_addresses()

                refresh_gui()
                new_name_entry.delete(0, tk.END)
                new_ip_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Name and IP address cannot be empty")

        add_button = tk.Button(root, text="Add Computer", command=add_computer)
        add_button.grid(row=row+1, column=2, padx=10, pady=10)

    refresh_gui()
    root.mainloop()

if __name__ == "__main__":
    setup_gui()
