import tkinter as tk
from math import radians


def on_press_button(button):
    """Zmienia kolor przycisku na jaśniejszy przy wciśnięciu."""
    button.config(bg="#444444")  # Zmiana koloru na jaśniejszy odcień szarości

def on_release_button(button, label, send_command=None):
    """Przywraca oryginalny kolor przycisku po zwolnieniu."""
    button.config(bg="#222222")  # Powrót do ciemniejszego koloru
    if send_command:
        send_command(label)

def update_connection_status(label, status, color):
    """Aktualizuje etykietę statusu połączenia."""
    label.config(text=status, fg=color)

def create_gui(send_command, on_close, connection_status, connection_color):
    """Tworzy GUI sterowania dronem."""
    root = tk.Tk()
    root.title("Sterowanie Dronem")
    root.geometry("700x400")
    root.configure(bg="#333333")

    # Status połączenia z zaokrąglonym tłem
    frame_label = tk.Frame(root, bg="#333333", bd=0, relief="solid", padx=10, pady=5, height=20)
    frame_label.place(relx=0.125, rely=0.05, relwidth=0.75, relheight=0.1)

    connection_label = tk.Label(
        frame_label, text=connection_status, bg="#333333", fg=connection_color,
        font=("Arial", 16), anchor="center", relief="flat", bd=0, padx=10, pady=5)
    connection_label.pack(expand=True, fill="both")

    # Tworzenie przycisków sterowania
    button_objects = {}
    button_config = {
        "w": (1, 1, "W"),
        "s": (2, 1, "S"),
        "a": (2, 0, "A"),
        "d": (2, 2, "D"),
        "r": (1, 4, "R"),
        "f": (2, 4, "F"),
    }

    frame = tk.Frame(root, bg="#333333")
    frame.place(relx=0.15, rely=0.3, relwidth=0.7, relheight=0.6)

    for key, (row, col, label) in button_config.items():
        button = tk.Button(
            frame,
            text=label,
            width=10,
            height=3,
            bg="#222222",
            fg="white",
            activebackground="#444444",
            activeforeground="white",
            font=("Arial", 12),
            command=lambda k=key: send_command(k.upper())  # Wyślij komendę po kliknięciu
        )
        button.grid(row=row, column=col, padx=10, pady=10)
        button_objects[key] = button

    root.protocol("WM_DELETE_WINDOW", on_close)  # Obsługa zamknięcia okna
    return root, connection_label, button_objects
