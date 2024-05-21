import tkinter as tk
from tkinter import messagebox, filedialog
import json
import binascii


################################################################
###########            CREATED BY Strix              ########### 
###########           Discord: strixmosh             ###########
################################################################


# Version information (more updates coming soon)
Version = "1.0.0"
BuildTime = "2024-05-21 12:00:00"
GitHash = "undefined"

class UsageError(Exception):
    pass

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

    if proxmark3_json.get("FileType") != "mfcard":
        raise ValueError("Expecting Mifare card dump")

    card_data = proxmark3_json["Card"]
    uid = decode_hex_data(card_data["UID"])
    atqa = decode_hex_data(card_data["ATQA"])
    sak = decode_hex_data(card_data["SAK"])

    blocks_map = proxmark3_json["blocks"]
    blocks = [decode_hex_data(block_data) for block_data in blocks_map.values()]

    return {"UID": uid, "ATQA": atqa, "SAK": sak, "Blocks": blocks}

def decode_hex_data(hex_str):
    try:
        return binascii.unhexlify(hex_str)
    except binascii.Error as e:
        raise ValueError(f"Failed to parse hex data '{hex_str}': {e}")
    except TypeError as e:
        raise ValueError(f"Invalid type for hex data '{hex_str}': {e}")

def write_nfc_file(file_name, card):
    with open(file_name, "w") as nfc_file:
        write_nfc(nfc_file, card)

def write_nfc(nfc_file, card):
    nfc_file.write("""Filetype: Flipper NFC device
Version: 2
# Nfc device type can be UID, Mifare Ultralight, Mifare Classic, Bank card
Device type: Mifare Classic
# UID, ATQA and SAK are common for all formats
""")
    nfc_file.write(f"UID: {card['UID'].hex()}\n")
    nfc_file.write(f"ATQA: {card['ATQA'].hex()}\n")
    nfc_file.write(f"SAK: {card['SAK'].hex()}\n")
    nfc_file.write("# Mifare Classic specific data\n")
    mf_size = 0
    block_fmt = "{}\n"
    num_blocks = len(card["Blocks"])
    if num_blocks == 64:
        mf_size = 1
    elif num_blocks == 128:
        mf_size = 2
    elif num_blocks == 256:
        mf_size = 4
    else:
        block_fmt = "Block {}: {}\n"  # Custom format for unknown blocks

    nfc_file.write(f"Mifare Classic type: {mf_size}K\n")
    nfc_file.write("Data format version: 2\n# Mifare Classic blocks, '??' means unknown data\n")
    for i, block in enumerate(card["Blocks"]):
        nfc_file.write(block_fmt.format(i, block.hex()))

if __name__ == "__main__":
    main()
