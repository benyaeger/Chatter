import tkinter as tk
from tkinter import messagebox


class ChatterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatter - Login")
        self.build_login_ui()

    def build_login_ui(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create login UI
        self.root.geometry("300x200")

        tk.Label(self.root, text="First Name:").pack(pady=5)
        self.first_name_entry = tk.Entry(self.root)
        self.first_name_entry.pack(pady=5)

        tk.Label(self.root, text="Last Name:").pack(pady=5)
        self.last_name_entry = tk.Entry(self.root)
        self.last_name_entry.pack(pady=5)

        login_button = tk.Button(self.root, text="Log In", command=self.handle_login)
        login_button.pack(pady=20)

    def handle_login(self):
        # Extract user input
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()

        # Placeholder for authentication logic
        if first_name and last_name:  # Simple check; replace with real authentication
            self.open_main_window(first_name, last_name)
        else:
            messagebox.showerror("Login Error", "Please enter your first and last name.")

    def open_main_window(self, first_name, last_name):
        # Destroy the login window components and set up the main chat UI
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("600x400")
        self.root.title(f"Chatter - {first_name} {last_name}")

        # Create the chat list frame on the left
        self.chat_list_frame = tk.Frame(self.root, width=200, bg="lightgrey")
        self.chat_list_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Create the chat frame on the right
        self.chat_frame = tk.Frame(self.root, bg="white")
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Example chat boxes (this should be dynamic in a real app)
        tk.Button(self.chat_list_frame, text="Chat 1", bg="lightgrey").pack(pady=10)
        tk.Button(self.chat_list_frame, text="Chat 2", bg="lightgrey").pack(pady=10)
        tk.Button(self.chat_list_frame, text="Chat 3", bg="lightgrey").pack(pady=10)

        # Messages display area
        self.message_area = tk.Frame(self.chat_frame, bg="#d3f8d3")  # Pastel green background
        self.message_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Placeholder for "No Messages" label
        self.no_message_label = tk.Label(self.message_area, text="No Messages In This Chat Yet", bg="#d3f8d3")
        self.no_message_label.pack(expand=True)  # Center the message

        # Input field and send button container
        self.message_input_frame = tk.Frame(self.chat_frame, bg="white")
        self.message_input_frame.pack(fill=tk.X, padx=10, pady=5)

        # Input field for typing messages
        self.message_entry = tk.Entry(self.message_input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Send button
        send_button = tk.Button(self.message_input_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT)

    def send_message(self):
        # Placeholder for message sending logic
        message = self.message_entry.get()
        if message.strip():
            self.no_message_label.pack_forget()  # Remove the "No Messages" label

            # Display the new message
            message_label = tk.Label(self.message_area, text=f"You: {message}", bg="#d3f8d3", anchor="w", justify="left")
            message_label.pack(fill=tk.X, padx=5, pady=2)

            self.message_entry.delete(0, tk.END)  # Clear input field
        else:
            messagebox.showwarning("Input Error", "Cannot send an empty message.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatterApp(root)
    root.mainloop()
