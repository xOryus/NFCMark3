import sys
import time
import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox

################################################################
###########            CREATED BY Strix              ########### 
###########           Discord: strixmosh             ###########
################################################################

# Version information (more updates coming soon)
Version = "1.0.1"
BuildTime = "2024-05-21 12:00:00"
GitHash = "undefined"

# Mapping for NFC card types based on ATQA and SAK values
NFC_CARD_TYPES = {
    ("0400", "08"): "Mifare Classic 1K",
    ("0200", "18"): "Mifare Classic 1K",
    ("0400", "09"): "Mifare Mini",
    ("4400", "00"): "Mifare Ultralight",
    ("4400", "20"): "Bank card",
    ("4403", "20"): "Mifare DESFire",
}

def generate_flipper_format(card_data):
    """
    Convert proxmark JSON data into Flipper Zero NFC format.
    """
    output_data = []

    card_info = card_data["Card"]
    atqa_sak = (card_info["ATQA"], card_info["SAK"])
    card_type = NFC_CARD_TYPES.get(atqa_sak, card_info["UID"])

    num_sectors = len(card_data.get("SectorKeys", []))
    key_map = f"{int('1' * num_sectors, 2):016X}"

    output_data.append(
        f"""
Filetype: Flipper NFC device
Version: 2
# Generated with NFC Converter
# {time.ctime()}
# Device types: UID, Mifare Ultralight, Mifare Classic, Bank card
Device type: {card_type}
UID: {' '.join(card_info['UID'][i:i+2] for i in range(0, len(card_info['UID']), 2))}
ATQA: {card_info['ATQA'][:2]} {card_info['ATQA'][2:]}
SAK: {card_info['SAK']}
Mifare Classic type: 1K
Data format version: 1
Key A map: {key_map}
Key B map: {key_map}
# Mifare Classic blocks"""
    )

    for block_num, block_val in card_data.get("blocks", {}).items():
        formatted_block = " ".join(block_val[i:i+2] for i in range(0, len(block_val), 2))
        output_data.append(f"Block {block_num}: {formatted_block}")

    return output_data

def open_json_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        return

    try:
        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        messagebox.showerror("Error", f"Error reading input file: {error}")
        return

    formatted_data = generate_flipper_format(data)
    output_display.delete(1.0, tk.END)
    output_display.insert(tk.END, "\n".join(formatted_data))

def save_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".nfc", filetypes=[("NFC files", "*.nfc")])
    if not file_path:
        return

    output_content = output_display.get(1.0, tk.END)
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(output_content)
        messagebox.showinfo("Success", "File saved successfully")
    except Exception as error:
        messagebox.showerror("Error", f"Error saving file: {error}")

# GUI setup
app = tk.Tk()
app.title("NFC Converter")
app.geometry("800x600")
app.configure(bg="#1a1a1a")

# Style configuration
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", background="#ff8c00", foreground="white", font=("Helvetica", 12))
style.map("TButton", background=[("active", "#ffb84d")])
style.configure("TLabel", background="#1a1a1a", foreground="white", font=("Helvetica", 14))
style.configure("TFrame", background="#1a1a1a")

main_frame = ttk.Frame(app, padding="10")
main_frame.pack(expand=True, fill=tk.BOTH)

title = ttk.Label(main_frame, text="NFC Converter")
title.pack(pady=10)

load_btn = ttk.Button(main_frame, text="Load JSON File", command=open_json_file)
load_btn.pack(pady=5)

save_btn = ttk.Button(main_frame, text="Save Output to File", command=save_output_file)
save_btn.pack(pady=5)

output_display = tk.Text(main_frame, wrap="word", bg="#262626", fg="white", font=("Helvetica", 12), insertbackground="white")
output_display.pack(expand=True, fill=tk.BOTH, pady=10)

app.mainloop()
