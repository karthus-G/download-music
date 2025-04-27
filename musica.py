import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, Toplevel

# Crear y activar un entorno virtual
def setup_virtual_environment():
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'myenv')
    pip_executable = os.path.join(venv_path, 'bin', 'pip')

    # Verificar si el entorno virtual ya está creado
    if not os.path.exists(venv_path) or not os.path.exists(pip_executable):
        print("El entorno virtual no existe o está incompleto. Creándolo nuevamente...")
        subprocess.check_call([sys.executable, '-m', 'venv', venv_path])
        print("Entorno virtual creado.")

    # Activar el entorno virtual
    if not os.getenv('VIRTUAL_ENV'):
        print("Activando entorno virtual...")
        os.environ['VIRTUAL_ENV'] = venv_path
        os.environ['PATH'] = os.path.join(venv_path, 'bin') + os.pathsep + os.environ['PATH']
        print("Entorno virtual activado.")

    # Asegurarse de que pip esté instalado y actualizado
    print("Verificando pip...")
    try:
        subprocess.check_call([pip_executable, "--version"])
    except FileNotFoundError:
        print("pip no está disponible. Instalándolo...")
        subprocess.check_call([sys.executable, '-m', 'ensurepip'])
    subprocess.check_call([pip_executable, "install", "--upgrade", "pip"])
    print("pip actualizado.")

    # Instalar las dependencias necesarias
    print("Instalando dependencias...")
    subprocess.check_call([pip_executable, "install", "google-api-python-client", "python-vlc", "yt-dlp"])
    print("Dependencias instaladas correctamente.")

    # Crear el archivo leeme.txt
    create_leeme_file()

def create_leeme_file():
    """Crea un archivo leeme.txt en la misma ubicación que el archivo .py si no existe."""
    leeme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leeme.txt")
    if not os.path.exists(leeme_path):
        with open(leeme_path, "w") as leeme_file:
            leeme_file.write("Este es un archivo editable. Puedes escribir aquí lo que desees.\n")
        print(f"Archivo 'leeme.txt' creado en {leeme_path}.")
    else:
        print(f"El archivo 'leeme.txt' ya existe en {leeme_path}.")

# Verificar e instalar dependencias automáticamente
def check_and_install_dependencies():
    required_packages = {
        "google-api-python-client": "googleapiclient",
        "python-vlc": "vlc",
        "yt-dlp": "yt_dlp"
    }
    pip_executable = os.path.join(os.getenv('VIRTUAL_ENV', ''), 'bin', 'pip')

    for package, module in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            print(f"Instalando {package}...")
            subprocess.check_call([pip_executable, "install", package])
            print(f"{package} instalado correctamente.")

            # Intentar importar el módulo nuevamente después de instalarlo
            try:
                __import__(module)
            except ImportError as e:
                print(f"Error al importar {package} después de la instalación: {e}")
                print(f"Verifica que el módulo '{module}' esté instalado correctamente en el entorno virtual.")
                sys.exit(1)

# Configurar el entorno virtual y las dependencias
setup_virtual_environment()
check_and_install_dependencies()



# Importar las dependencias después de la instalación
from googleapiclient.discovery import build
import vlc
import yt_dlp
import threading
import time

# Configuración de la API de YouTube
API_KEY = 'AIzaSyBwy28pFViJ0u8tOmqH-6Z1DvzKsr7IlBc'
youtube = build('youtube', 'v3', developerKey=API_KEY)


class PlaylistApp:
    def __init__(self, root):
        self.root = root

        # Aplicar estilos personalizados
        self.root.title("Playlist Manager")
        self.root.geometry("800x600")  # Tamaño de la ventana
        self.root.configure(bg="#2b2b2b")  # Fondo oscuro
        self.root.resizable(False, False)

        # Ruta predeterminada para guardar canciones
        self.music_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "musica")
        if not os.path.exists(self.music_folder):
            os.makedirs(self.music_folder)

        # Configurar el diseño de la ventana principal
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Marco principal
        main_frame = tk.Frame(root, bg="#2b2b2b")  # Fondo oscuro
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Entrada de búsqueda
        self.search_entry = tk.Entry(main_frame, width=50, font=("Helvetica", 12), bg="#3c3f41", fg="white", insertbackground="white")
        self.search_entry.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.search_youtube())

        # Botón de búsqueda
        self.search_button = tk.Button(
            main_frame, text="Buscar", command=self.search_youtube, bg="#4caf50", fg="white", font=("Helvetica", 10), relief="flat"
        )
        self.search_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Resultados de búsqueda
        self.search_results = tk.Listbox(main_frame, bg="#3c3f41", fg="white", font=("Helvetica", 10), selectbackground="#4caf50", selectforeground="black")
        self.search_results.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Playlist
        self.playlist = tk.Listbox(main_frame, bg="#3c3f41", fg="white", font=("Helvetica", 10), selectbackground="#4caf50", selectforeground="black")
        self.playlist.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Botones de control
        control_frame = tk.Frame(main_frame, bg="#2b2b2b")
        control_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

        self.add_button = tk.Button(
            control_frame, text="Agregar a Playlist", command=self.add_to_playlist, bg="#2196f3", fg="white", font=("Helvetica", 10), relief="flat"
        )
        self.add_button.pack(side="left", padx=5, pady=5)

        self.remove_button = tk.Button(
            control_frame, text="Eliminar de Playlist", command=self.remove_from_playlist, bg="#f44336", fg="white", font=("Helvetica", 10), relief="flat"
        )
        self.remove_button.pack(side="left", padx=5, pady=5)

        self.play_button = tk.Button(
            control_frame, text="Reproducir Canción", command=self.play_video, bg="#ff9800", fg="white", font=("Helvetica", 10), relief="flat"
        )
        self.play_button.pack(side="left", padx=5, pady=5)

        self.video_urls = []
        self.current_index = None
        self.is_paused = False

        # Cargar canciones descargadas al iniciar la aplicación
        self.load_downloaded_songs()

    def load_downloaded_songs(self):
        """Carga las canciones descargadas previamente desde la carpeta predeterminada."""
        self.playlist.delete(0, tk.END)
        self.video_urls.clear()

        if os.path.exists(self.music_folder):
            for file_name in os.listdir(self.music_folder):
                if file_name.endswith(".mp3"):
                    file_path = os.path.join(self.music_folder, file_name)
                    self.playlist.insert(tk.END, file_name)
                    self.video_urls.append(file_path)

    def search_youtube(self):
        query = self.search_entry.get()
        if not query.strip():
            messagebox.showwarning("Advertencia", "Por favor, ingresa un término de búsqueda.")
            return

        try:
            # Solicitar hasta 100 resultados
            request = youtube.search().list(
                q=query,
                part="snippet",
                type="video",
                maxResults=100
            )
            response = request.execute()

            self.search_results.delete(0, tk.END)
            self.video_urls = []

            for item in response['items']:
                if 'videoId' in item['id']:
                    title = item['snippet']['title']
                    video_id = item['id']['videoId']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"  # URL del video
                    self.search_results.insert(tk.END, title)
                    self.video_urls.append(video_url)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la búsqueda: {e}")

    def add_to_playlist(self):
        selected = self.search_results.curselection()
        if selected:
            index = selected[0]
            title = self.search_results.get(index)
            video_url = self.video_urls[index]

            # Descargar el archivo en formato MP3
            try:
                # Configurar las opciones de descarga
                ydl_opts = {
                    "format": "bestaudio/best",  # Descargar solo el mejor audio disponible
                    "outtmpl": f"{self.music_folder}/{title}.%(ext)s",  # Guardar en la carpeta predeterminada
                    "postprocessors": [
                        {  # Convertir a MP3
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",  # Calidad de audio en kbps
                        }
                    ],
                }

                # Descargar el archivo
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                # Verificar que el archivo descargado existe
                file_path = f"{self.music_folder}/{title}.mp3"
                if not os.path.exists(file_path):
                    messagebox.showerror("Error", f"No se encontró el archivo descargado: {file_path}")
                    return

                # Actualizar la playlist
                self.load_downloaded_songs()
                messagebox.showinfo("Éxito", f"{title} se descargó correctamente en {self.music_folder}.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo descargar el archivo: {e}")

    def remove_from_playlist(self):
        selected = self.playlist.curselection()
        if selected:
            index = selected[0]
            file_path = self.video_urls[index]

            # Eliminar el archivo del sistema
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar el archivo: {e}")
                    return

            # Actualizar la playlist
            self.load_downloaded_songs()
            messagebox.showinfo("Éxito", "La canción se eliminó correctamente.")

    def play_video(self):
        selected = self.playlist.curselection()
        if selected:
            self.current_index = selected[0]
            self._play_video_at_index(self.current_index)
        else:
            messagebox.showwarning("Advertencia", "Selecciona un video de la playlist para reproducir.")

    def _play_video_at_index(self, index):
        # Obtener la ruta del archivo desde la lista de URLs
        file_path = self.video_urls[index]
        title = self.playlist.get(index)

        try:
            # Verificar si el archivo existe
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"El archivo no existe: {file_path}")
                return

            # Crear una ventana emergente para reproducir el audio
            audio_window = Toplevel(self.root)
            audio_window.title("Reproduciendo Canción")
            audio_window.geometry("300x160")  # Tamaño ajustado para incluir todos los elementos
            audio_window.configure(bg="black")

            # Configurar el diseño de la ventana
            audio_window.rowconfigure(0, weight=1)  # Información de la canción
            audio_window.rowconfigure(1, weight=0)  # Etiquetas de tiempo
            audio_window.rowconfigure(2, weight=0)  # Barra de progreso
            audio_window.rowconfigure(3, weight=0)  # Botones de control
            audio_window.columnconfigure(0, weight=1)

            # Mostrar el título de la canción con animación
            title_var = tk.StringVar(value=title + "  ")  # Agregar dos espacios al final del título
            title_label = tk.Label(audio_window, textvariable=title_var, font=("Courier", 12), fg="white", bg="black")
            title_label.grid(row=0, column=0, pady=5, sticky="n")

            def scroll_title():
                current_text = title_var.get()
                title_var.set(current_text[1:] + current_text[0])  # Mover el primer carácter al final
                audio_window.after(200, scroll_title)  # Actualizar cada 200 ms

            scroll_title()  # Iniciar la animación

            # Crear un reproductor VLC
            instance = vlc.Instance("--no-xlib")
            player = instance.media_player_new()
            media = instance.media_new(file_path)
            player.set_media(media)
            player.play()

            # Detener la música al cerrar la ventana
            def on_close():
                player.stop()  # Detener el reproductor VLC
                audio_window.destroy()  # Cerrar la ventana

            audio_window.protocol("WM_DELETE_WINDOW", on_close)

            # Etiquetas para mostrar el tiempo actual y la duración total
            time_frame = tk.Frame(audio_window, bg="black")
            time_frame.grid(row=1, column=0, pady=5, sticky="ew")

            current_time_label = tk.Label(time_frame, text="00:00", font=("Courier", 10), fg="white", bg="black")
            current_time_label.pack(side="left", padx=5)

            total_time_label = tk.Label(time_frame, text="00:00", font=("Courier", 10), fg="white", bg="black")
            total_time_label.pack(side="right", padx=5)

            # Barra de progreso gráfica
            progress_canvas = tk.Canvas(audio_window, height=10, bg="gray")
            progress_canvas.grid(row=2, column=0, pady=5, sticky="ew")
            progress_bar = progress_canvas.create_rectangle(0, 0, 0, 10, fill="green")

            # Función para actualizar la barra de progreso y las etiquetas de tiempo
            def update_progress():
                while True:
                    if player.is_playing():
                        current_time = player.get_time() // 1000  # Convertir a segundos
                        duration = player.get_length() // 1000  # Duración total en segundos

                        # Actualizar etiquetas de tiempo
                        current_time_label.config(text=self._format_time(current_time))
                        total_time_label.config(text=self._format_time(duration))

                        # Actualizar barra de progreso
                        if duration > 0:
                            progress_width = (current_time / duration) * progress_canvas.winfo_width()
                            progress_canvas.coords(progress_bar, 0, 0, progress_width, 10)

                        time.sleep(0.5)  # Actualizar cada 500 ms

            threading.Thread(target=update_progress, daemon=True).start()

            # Función para manejar clics en la barra de progreso
            def seek(event):
                duration = player.get_length() // 1000  # Duración total en segundos
                if duration > 0:
                    # Calcular la posición clicada como porcentaje de la barra
                    click_position = event.x / progress_canvas.winfo_width()
                    new_time = int(click_position * duration * 1000)  # Convertir a milisegundos
                    player.set_time(new_time)  # Ajustar el tiempo de reproducción

            # Vincular el evento de clic a la barra de progreso
            progress_canvas.bind("<Button-1>", seek)

            # Botones de control
            control_frame = tk.Frame(audio_window, bg="black")
            control_frame.grid(row=3, column=0, pady=5, sticky="ew")
            control_frame.columnconfigure(0, weight=1)
            control_frame.columnconfigure(1, weight=1)
            control_frame.columnconfigure(2, weight=1)

            prev_button = tk.Button(control_frame, text="Anterior", command=lambda: self._play_previous(player, audio_window))
            prev_button.grid(row=0, column=0, padx=5, sticky="ew")

            pause_button = tk.Button(control_frame, text="Pausa", command=lambda: self._toggle_pause(player, pause_button))
            pause_button.grid(row=0, column=1, padx=5, sticky="ew")

            next_button = tk.Button(control_frame, text="Siguiente", command=lambda: self._play_next(player, audio_window))
            next_button.grid(row=0, column=2, padx=5, sticky="ew")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir el archivo: {e}")

    def _format_time(self, seconds):
        """Convierte segundos en formato mm:ss."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def _toggle_pause(self, player, button):
        if self.is_paused:
            player.play()
            button.config(text="Pausa")
        else:
            player.pause()
            button.config(text="Reanudar")
        self.is_paused = not self.is_paused

    def _play_previous(self, player, video_window):
        if self.current_index is not None and self.current_index > 0:
            self.current_index -= 1
            player.stop()
            video_window.destroy()
            self._play_video_at_index(self.current_index)

    def _play_next(self, player, video_window):
        if self.current_index is not None and self.current_index < len(self.video_urls) - 1:
            self.current_index += 1
            player.stop()
            video_window.destroy()
            self._play_video_at_index(self.current_index)


if __name__ == "__main__":
    root = tk.Tk()
    app = PlaylistApp(root)
    root.mainloop()
