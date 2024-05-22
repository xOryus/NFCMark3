import tkinter as tk
from tkinter import messagebox, filedialog
import json
import binascii
import time

################################################################
###########            CREATED BY Strix              ########### 
###########           Discord: strixmosh             ###########
################################################################

# Version information (more updates coming soon)
Version = "1.0.1"
BuildTime = "2024-05-21 12:00:00"
GitHash = "undefined"

class UsageError(Exception):
    pass

# NFC device type can be UID, Mifare Ultralight, Mifare Classic, bank card
CARD_TYPE = {
    ("0004", "08"): "Mifare Classic",  # 1k
    ("0200", "18"): "Mifare Classic",  # 4k
    ("0400", "09"): "Mifare Mini",
    ("4400", "00"): "Mifare Ultralight",  # "NTAG213" "NTAG216"
    ("4400", "20"): "Bank card",
    ("4403", "20"): "Mifare DESFire",
}
def main():
    root = tk.Tk()
    root.title("Proxmark3 to NFC Converter")
    root.geometry("800x500")
    root.configure(bg='black')

    label = tk.Label(root, text="Convert Proxmark3 Dump file to NFC file", bg='black', fg='orange', font=('Helvetica', 16))
    label.pack(pady=10)

    input_frame = tk.Frame(root, bg='black')
    input_frame.pack(pady=10)

    input_label = tk.Label(input_frame, text="Input Proxmark3 dump file:", bg='black', fg='orange', font=('Helvetica', 12))
    input_label.grid(row=0, column=0, padx=10, pady=10)

    input_entry = tk.Entry(input_frame, bg='orange', fg='black', font=('Helvetica', 12))
    input_entry.grid(row=0, column=1, padx=10, pady=10)

    input_button = tk.Button(input_frame, text="Browse", bg='orange', fg='black', font=('Helvetica', 12), command=lambda: browse_file(input_entry, "open"))
    input_button.grid(row=0, column=2, padx=10, pady=10)

    output_frame = tk.Frame(root, bg='black')
    output_frame.pack(pady=10)

    output_label = tk.Label(output_frame, text="Output NFC file:", bg='black', fg='orange', font=('Helvetica', 12))
    output_label.grid(row=0, column=0, padx=10, pady=10)

    output_entry = tk.Entry(output_frame, bg='orange', fg='black', font=('Helvetica', 12))
    output_entry.grid(row=0, column=1, padx=10, pady=10)

    output_button = tk.Button(output_frame, text="Browse", bg='orange', fg='black', font=('Helvetica', 12), command=lambda: browse_file(output_entry, "save"))
    output_button.grid(row=0, column=2, padx=10, pady=10)

    log_text = tk.Text(root, height=8, width=50, bg='orange', fg='black', font=('Helvetica', 12))
    log_text.pack(pady=10)

    convert_button = tk.Button(root, text="Convert", bg='orange', fg='black', font=('Helvetica', 12), command=lambda: convert_files(input_entry.get(), output_entry.get(), log_text))
    convert_button.pack(pady=20)

    root.mainloop()

def browse_file(entry, mode):
    if mode == "open":
        filename = filedialog.askopenfilename()
    elif mode == "save":
        filename = filedialog.asksaveasfilename(defaultextension=".nfc", filetypes=[("NFC files", "*.nfc"), ("All files", "*.*")])
    if filename:
        entry.delete(0, tk.END)
        entry.insert(tk.END, filename)

def convert_files(input_file, output_file, log_text):
    try:
        card = parse_proxmark3_json_file(input_file)
        write_nfc_file(output_file, card)
        log_text.insert(tk.END, "Conversion completed successfully!\n")
        log_text.insert(tk.END, f"Output file saved as: {output_file}\n")
    except Exception as e:
        log_text.insert(tk.END, f"Error: {str(e)}\n")
        messagebox.showerror("Error", str(e))

def parse_proxmark3_json_file(file_name):
    with open(file_name, "r") as json_file:
        return parse_proxmark3_json(json_file)

def parse_proxmark3_json(json_file):
    proxmark3_json = json.load(json_file)

    if proxmark3_json.get("Created") != "proxmark3":
        raise ValueError("JSON file must be produced by Proxmark3")

    card_data = proxmark3_json["Card"]
    uid = card_data["UID"]
    atqa = card_data["ATQA"]
    sak = card_data["SAK"]

    blocks_map = proxmark3_json.get("blocks", {})
    blocks = [blocks_map.get(str(i), "??") for i in range(len(blocks_map))]

    sector_keys = proxmark3_json.get("SectorKeys", {})

    # Guess card type by looking at ATQA/SAK combo
    card_type = CARD_TYPE.get((atqa, sak), "Unknown")

    # Generate Key maps if sector_keys are provided
    if sector_keys:
        y = len(sector_keys)
        s = int("1" * y, 2)
        ska = skb = f"{s:016X}"
    else:
        ska = skb = "0" * 16

    return {
        "UID": uid,
        "ATQA": atqa,
        "SAK": sak,
        "Blocks": blocks,
        "CardType": card_type,
        "KeyAMap": ska,
        "KeyBMap": skb,
        "SectorKeys": sector_keys
    }

def write_nfc_file(file_name, card):
    with open(file_name, "w") as nfc_file:
        write_nfc(nfc_file, card)

def write_nfc(nfc_file, card):
    uid_formatted = " ".join(card['UID'][i:i+2] for i in range(0, len(card['UID']), 2))
    atqa_formatted = " ".join(card['ATQA'][i:i+2] for i in range(0, len(card['ATQA']), 2))
    sak_formatted = card['SAK']

    nfc_file.write(f"""Filetype: Flipper NFC device
Version: 2
# {time.ctime()}
# NFC device type can be UID, Mifare Ultralight, Mifare Classic, Bank card
Device type: {card['CardType']}
# UID, ATQA and SAK are common for all formats
UID: {uid_formatted}
ATQA: {atqa_formatted}
SAK: {sak_formatted}
""")

    if card['CardType'] == "Mifare Classic":
        nfc_file.write(f"""# Mifare Classic specific data
Mifare Classic type: 1K
Data format version: 1
# Key map is the bit mask indicating valid key in each sector
Key A map: {card['KeyAMap']}
Key B map: {card['KeyBMap']}
# Mifare Classic blocks
""")
        for i, block in enumerate(card["Blocks"]):
            block_formatted = " ".join(block[j:j+2] for j in range(0, len(block), 2))
            nfc_file.write(f"Block {i}: {block_formatted}\n")
    else:
        for i, block in enumerate(card["Blocks"]):
            block_formatted = " ".join(block[j:j+2] for j in range(0, len(block), 2))
            nfc_file.write(f"Block {i}: {block_formatted}\n")

if __name__ == "__main__":
    main()
