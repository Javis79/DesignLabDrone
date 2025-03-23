import socket
import threading
from gui import create_gui, update_connection_status, on_press_button, on_release_button

# Konfiguracja połączenia TCP
server_ip = '192.168.137.10'  # Adres IP Raspberry Pi
server_port = 5000            # Port serwera

# Globalne zmienne
client_socket = None
connected = False  # Flaga, czy połączenie zostało nawiązane
connection_label = None
root = None
button_objects = {}

# Funkcja wysyłająca komendy
def send_command(command):
    global client_socket, connected
    if connected:
        try:
            client_socket.sendall(command.encode('utf-8'))
            print(f"Wysłano komendę: {command}")  # Wyświetlenie w terminalu
        except Exception as e:
            print(f"Błąd podczas wysyłania: {e}")
            connected = False  # Oznacz brak połączenia, aby spróbować ponownie

# Funkcja obsługująca zdarzenia naciśnięcia klawiszy
def handle_keypress(event):
    global button_objects
    key = event.char.lower()  # Pobierz wciśnięty klawisz
    if key in button_objects:
        button = button_objects[key]
        if not button.config('bg')[-1] == "#444444":  # Jeśli przycisk nie jest już wciśnięty
            on_press_button(button)  # Zmiana stylu przycisku w GUI
            send_command(key.upper())  # Wyślij komendę
            print(f"Klawiatura: wciśnięto {key.upper()}")  # Wyświetlenie w terminalu

# Funkcja obsługująca zdarzenia puszczenia klawiszy
def handle_keyrelease(event):
    global button_objects
    key = event.char.lower()  # Pobierz wciśnięty klawisz
    if key in button_objects:
        button = button_objects[key]
        if button.config('bg')[-1] == "#444444":  # Jeśli przycisk był wciśnięty
            on_release_button(button, key.upper(), send_command)  # Zmiana stylu przycisku w GUI
            print(f"Klawiatura: zwolniono {key.upper()}")  # Wyświetlenie w terminalu

# Funkcja nawiązywania połączenia z serwerem
def connect_to_server():
    global client_socket, connected, connection_label, root

    while True:
        if not connected:  # Próba połączenia, jeśli nie ma aktywnego połączenia
            try:
                print("Próba połączenia z serwerem...")
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((server_ip, server_port))
                connected = True
                update_connection_status(
                    connection_label,
                    f"Połączono z: {server_ip}:{server_port}",
                    "green"
                )
                print(f"Połączono z serwerem {server_ip}:{server_port}")
            except Exception as e:
                print(f"Nie udało się połączyć: {e}. Ponawianie...")
                update_connection_status(connection_label, "Rozłączono, ponowne łączenie...", "red")
                connected = False
                client_socket = None

        threading.Event().wait(2)  # Odczekaj 2 sekundy przed kolejną próbą

# Funkcja zamykająca połączenie
def on_close():
    global client_socket, root
    print("Zamykanie GUI i rozłączanie z serwerem...")
    if client_socket:
        try:
            client_socket.close()
        except Exception as e:
            print(f"Błąd podczas zamykania połączenia: {e}")
    root.destroy()

# Uruchomienie GUI
if __name__ == "__main__":
    # Start GUI i elementów połączenia
    root, connection_label, button_objects = create_gui(
        send_command=send_command,
        on_close=on_close,
        connection_status="Oczekiwanie na połączenie...",
        connection_color="red"
    )

    # Powiązanie obsługi klawiatury z oknem GUI
    root.bind("<KeyPress>", handle_keypress)
    root.bind("<KeyRelease>", handle_keyrelease)

    # Start wątku do obsługi połączenia z serwerem
    connection_thread = threading.Thread(target=connect_to_server, daemon=True)
    connection_thread.start()

    # Uruchomienie głównej pętli GUI
    root.mainloop()
