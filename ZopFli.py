import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import threading

def get_unique_filename(directory, base, ext, counter=1):
    # Cette fonction génère un nouveau nom unique pour le fichier de sortie.
    test_base = f"{base}-{counter}" if counter > 0 else base
    test_path = f"{test_base}{ext}"
    
    if os.path.exists(os.path.join(directory, test_path)):
        return get_unique_filename(directory, base, ext, counter + 1)
    else:
        return test_path

def compress_image_thread(input_file_path, output_file_path, options, button):
    # Construction de la commande en tant que chaîne
    command_str = " ".join(["/opt/homebrew/bin/zopflipng"] + options + [input_file_path, output_file_path])
    print("Executing command:", command_str)  # Pour le débogage
    
    try:
        subprocess.run(command_str, check=True, shell=True)
        print("Compression réussie.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {e}")
    finally:
        button.config(state=tk.NORMAL)

def compress_image():
    compress_button.config(state=tk.DISABLED)
    
    input_file_path = filedialog.askopenfilename(title="Sélectionnez l'image à compresser", filetypes=[("PNG files", "*.png")])
    if not input_file_path:
        compress_button.config(state=tk.NORMAL)
        return

    directory, filename = os.path.split(input_file_path)
    base, ext = os.path.splitext(filename)
    unique_name = get_unique_filename(directory, base, ext)
    
    output_file_path = filedialog.asksaveasfilename(
        title="Enregistrez l'image optimisée",
        initialdir=directory,
        initialfile=unique_name,
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")])
    
    if not output_file_path:
        compress_button.config(state=tk.NORMAL)  # Réactiver le bouton si l'opération est annulée
        return

    options = [
        f"--iterations={iterations_slider.get()}",  # Utiliser .get() pour obtenir la valeur actuelle
        f"--splitting={splitting_slider.get()}",  # Utiliser .get() pour obtenir la valeur actuelle
        f"--filters={filter_strategy_var.get()}",  # Utiliser .get() pour obtenir la valeur actuelle
        "--lossy_transparent" if lossy_transparent_var.get() else "",  # Utiliser .get() ici aussi
        "--lossy_8bit" if lossy_8bit_var.get() else "",  # Et ici
        "--keepchunks=iCCP,exIf",
    ]

    print("Input file path:", input_file_path)
    print("Output file path:", output_file_path)

    # En passant les chemins d'accès directement sans recodage en bytes
    thread = threading.Thread(target=compress_image_thread, args=(input_file_path, output_file_path, options, compress_button))
    thread.start()

root = tk.Tk()
root.title("Compresseur d'images ZopfliPNG")
root.geometry("300x410")  # Ajusté pour ajouter plus d'espace

iterations_slider = tk.Scale(root, from_=1, to=1000, label="Iterations", orient="horizontal", length=280)
iterations_slider.set(20)
iterations_slider.pack(pady=10)  # Ajoute un peu d'espace vertical

splitting_slider = tk.Scale(root, from_=0, to=3, label="Splitting", orient="horizontal", length=280)
splitting_slider.set(3)
splitting_slider.pack(pady=10)

filter_strategy_var = tk.StringVar(value="e")
for strategy in [("Minsum", "m"), ("Entropie", "e"), ("Prédictive", "p"), ("Brute Force", "b")]:
    tk.Radiobutton(root, text=strategy[0], variable=filter_strategy_var, value=strategy[1]).pack(anchor=tk.W,pady=3,padx=7)

lossy_transparent_var = tk.BooleanVar(value=True)
lossy_transparent_check = tk.Checkbutton(root, text="Lossy Transparent", variable=lossy_transparent_var)
lossy_transparent_check.pack(pady=10)

lossy_8bit_var = tk.BooleanVar()
lossy_8bit_check = tk.Checkbutton(root, text="Lossy 8bit", variable=lossy_8bit_var)
lossy_8bit_check.pack()

compress_button = tk.Button(root, text="Compresser Image", command=compress_image)
compress_button.pack(pady=15) # Ajoute un peu d'espace vertical

root.mainloop()
