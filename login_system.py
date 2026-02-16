import sqlite3
import bcrypt
import tkinter as tk
from tkinter import messagebox
import re
import threading
import time

# Color scheme
DARK_BG = "#0f1419"
CARD_BG = "#1a1f2e"
ACCENT_GREEN = "#00d084"
ACCENT_BLUE = "#0077B6"  # Peacock blue
ACCENT_RED = "#ff3366"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#a0a0b0"
BORDER_COLOR = "#2a3040"

# -------- PASSWORD STRENGTH CHECKER --------
def check_password_strength(password):
    """Returns (strength_level, strength_text, color) where 0=weak, 1=fair, 2=good, 3=strong"""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[a-z]", password) and re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        score += 1
    
    if score <= 1:
        return 0, "Weak", "#ff4444"
    elif score <= 2:
        return 1, "Fair", "#ffaa00"
    elif score <= 3:
        return 2, "Good", "#ffdd00"
    else:
        return 3, "Strong", ACCENT_GREEN

# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password BLOB,
    failed_attempts INTEGER,
    locked INTEGER
)
""")

conn.commit()

# ---------------- SECURITY FUNCTIONS ----------------
def gui_register():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Error", "All fields are required")
        return

    if len(password) < 6:
        messagebox.showwarning(
            "Weak Password",
            "Password should be at least 6 characters"
        )
        return

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, 0, 0)",
            (username, hashed_pw)
        )
        conn.commit()
        messagebox.showinfo("Success", "Registration successful")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    except:
        messagebox.showerror("Error", "Username already exists")


def gui_login():
    username = username_entry.get()
    password = password_entry.get()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user:
        messagebox.showerror("Error", "User not found")
        return

    stored_pw, attempts, locked = user[1], user[2], user[3]

    if locked:
        messagebox.showwarning(
            "Account Locked",
            "Account locked due to multiple failed login attempts"
        )
        return

    if bcrypt.checkpw(password.encode(), stored_pw):
        cursor.execute(
            "UPDATE users SET failed_attempts=0 WHERE username=?",
            (username,)
        )
        conn.commit()
        messagebox.showinfo("Success", "Login successful")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    else:
        attempts += 1

        if attempts >= 3:
            cursor.execute(
                "UPDATE users SET locked=1 WHERE username=?",
                (username,)
            )
            conn.commit()
            messagebox.showwarning(
                "Account Locked",
                "Account locked due to brute-force attack"
            )
        else:
            cursor.execute(
                "UPDATE users SET failed_attempts=? WHERE username=?",
                (attempts, username)
            )
            conn.commit()
            messagebox.showerror(
                "Error",
                f"Wrong password (Attempt {attempts})"
            )

# ---------------- GUI LAYOUT ----------------
root = tk.Tk()
root.title("Secure Login System")
root.geometry("1100x700")
root.configure(bg="#01182F")

# Center card frame (enlarged)
card = tk.Frame(
    root,
    bg="#0b2748",
    width=520,
    height=460
)
card.place(relx=0.5, rely=0.5, anchor="center")

# Title (larger)
tk.Label(
    card,
    text="Secure Login",
    font=("Oswald", 22, "bold"),
    fg="#b63000",
    bg="#0e2a3a"

).pack(pady=(30, 8))

# Subtitle (larger)
tk.Label(
    card,
    text="Brute-Force Attack Protection Enabled",
    font=("Segoe UI", 12),
    fg="#c2d6df",
    bg="#0e2a3a"
).pack(pady=(0, 24))

# Username
tk.Label(
    card,
    text="Username",
    font=("Segoe UI", 12),
    fg="#e6f2f8",
    bg="#0e2a3a"
).pack(anchor="w", padx=56)

username_entry = tk.Entry(
    card,
    font=("Segoe UI", 12),
    width=36,
    bg="#ffffff",
    fg="#000000",
    relief="flat",
    bd=4
)
username_entry.pack(pady=8)

# Password
tk.Label(
    card,
    text="Password",
    font=("Segoe UI", 12),
    fg="#e6f2f8",
    bg="#0e2a3a"
).pack(anchor="w", padx=56, pady=(10, 0))

password_entry = tk.Entry(
    card,
    font=("Segoe UI", 12),
    width=36,
    show="*",
    bg="#ffffff",
    fg="#000000",
    relief="flat",
    bd=4
)
password_entry.pack(pady=8)

# Buttons (peacock blue)python -c "import bcrypt; print('bcrypt working')"

btn_frame = tk.Frame(card, bg="#0e2a3a")
btn_frame.pack(pady=30)

tk.Button(
    btn_frame,
    text="Register",
    font=("Segoe UI", 13, "bold"),
    bg=ACCENT_BLUE,
    fg="white",
    width=16,
    relief="flat",
    command=gui_register,
    activebackground=ACCENT_BLUE
).grid(row=0, column=0, padx=12)

login_button = tk.Button(
    btn_frame,
    text="Login",
    font=("Segoe UI", 13, "bold"),
    bg="#000000",
    fg="white",
    width=16,
    relief="flat",
    command=gui_login,
    activebackground="#222222"
)
login_button.grid(row=0, column=1, padx=12)

# Status message
status_label = tk.Label(
    card,
    text="",
    font=("Segoe UI", 10),
    fg="#ffd37a",
    bg="#0e2a3a"
)
status_label.pack()

# Footer
tk.Label(
    root,
    text="© Secure Authentication Demo | Python + SQLite",
    font=("Segoe UI", 10),
    fg="#9aaab5",
    bg="#0f1419"
).pack(side="bottom", pady=14)

root.mainloop()
# Close the database connection when the GUI is closed
conn.close()
