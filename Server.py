import socket
import threading
import logging
import json
import tkinter as tk
from tkinter import messagebox

# Configure logging
logging.basicConfig(filename='message_log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

addresses_file = 'ServerAddress.json'

try:
    with open(addresses_file, 'r') as file:
        addresses = json.load(file)
except FileNotFoundError:
    addresses = {
        
    }

def save_addresses():
    with open(addresses_file, 'w') as file:
        json.dump(addresses, file)

def show_popup(receiver_name, sender_name, message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    try:
        messagebox.showinfo(f"Message Received by {sender_name}", f"From {sender_name}: {message}")
        root.destroy()
    except Exception as e:
        logging.error(f"Error showing message popup: {e}")

def start_server(ip, name, port=9999):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server_socket.bind((ip, port))
        logging.debug(f"Server started on {ip}:{port}")
    except Exception as e:
        logging.error(f"Error binding to port {port} on {ip}: {e}")
        return

    server_socket.listen(5)
    logging.debug("Server is listening for connections...")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            logging.debug(f"Got a connection from {addr}")
            
            message = client_socket.recv(1024).decode('utf-8')
            logging.debug(f"Message received from {addr}: {message}")

            log_message = f"Message received from {addr}: {message}"
            logging.info(log_message)

            if message:
                sender_name, actual_message = message.split(':', 1)
                show_popup(name, sender_name, actual_message.strip())
            
            client_socket.close()
        except Exception as e:
            logging.error(f"Error accepting or handling connection: {e}")

def setup_gui():
    root = tk.Tk()
    root.title("Add Computer and IP Address")

    tk.Label(root, text="Computer Name:").grid(row=0, column=0, padx=10, pady=10)
    tk.Label(root, text="IP Address:").grid(row=1, column=0, padx=10, pady=10)

    name_entry = tk.Entry(root, width=30)
    name_entry.grid(row=0, column=1, padx=10, pady=10)
    ip_entry = tk.Entry(root, width=30)
    ip_entry.grid(row=1, column=1, padx=10, pady=10)

    def add_computer():
        name = name_entry.get().strip()
        ip_address = ip_entry.get().strip()

        if name and ip_address:
            addresses[name] = ip_address
            save_addresses()
            messagebox.showinfo("Success", f"Computer {name} with IP {ip_address} added successfully!")
            name_entry.delete(0, tk.END)
            ip_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Computer name and IP address cannot be empty")

    add_button = tk.Button(root, text="Add Computer", command=add_computer)
    add_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    root.mainloop()

def run_server():
    for name, ip_address in addresses.items():
        server_thread = threading.Thread(target=start_server, args=(ip_address, name))
        server_thread.daemon = True
        server_thread.start()

if __name__ == "__main__":
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Setup and run the GUI
    setup_gui()

    # Keep the main thread alive
    while True:
        pass
