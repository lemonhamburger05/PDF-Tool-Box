import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from pypdf import PdfReader, PdfWriter
from PIL import ImageTk, Image
from tkinter import ttk
from tkinter import simpledialog

merge_file_data = []


def merge_pdfs():
    if not merge_file_data:
        messagebox.showwarning("Warning", "No PDF files added for merging.")
        return

    writer = PdfWriter()
    try:
        for item in merge_file_data:
            path = item['path']
            page_range = item['pages']
            reader = PdfReader(path)
            total_pages = len(reader.pages)

            if page_range.lower() == "all":
                pages = range(total_pages)
            elif "-" in page_range:
                start, end = map(int, page_range.split("-"))
                pages = range(start - 1, end)
            else:
                pages = [int(x.strip()) - 1 for x in page_range.split(",")]

            for i in pages:
                if 0 <= i < total_pages:
                    writer.add_page(reader.pages[i])
                else:
                    messagebox.showerror("Error", f"Page out of range in file {os.path.basename(path)}: {i + 1}")
                    return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")],
                                                   title="Save merged PDF")
        if output_path:
            with open(output_path, "wb") as f:
                writer.write(f)
            messagebox.showinfo("Success", f"PDF merged successfully: {output_path}")
            status_label.config(text="Merge completed.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def extract_text_from_pdf():
    if not merge_file_data:
        messagebox.showwarning("Warning", "No PDF files added in the list.")
        return

    try:
        text_output = ""

        for item in merge_file_data:
            path = item['path']
            filename = os.path.basename(path)
            page_range = item['pages']
            reader = PdfReader(path)
            total_pages = len(reader.pages)

            text_output += f"\n=== File: {filename} ===\n"

            if page_range.lower() == "all":
                pages = range(total_pages)
            elif "-" in page_range:
                start, end = map(int, page_range.split("-"))
                pages = range(start - 1, end)
            else:
                pages = [int(x.strip()) - 1 for x in page_range.split(",")]

            for i in pages:
                if 0 <= i < total_pages:
                    text = reader.pages[i].extract_text()
                    if text:
                        text_output += f"\n--- Page {i + 1} ---\n{text}"
                else:
                    messagebox.showerror("Error", f"Page out of range in file {filename}: {i + 1}")
                    return

        if not text_output.strip():
            messagebox.showinfo("Info", "No text found on the selected pages.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save extracted text"
        )
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text_output)
            messagebox.showinfo("Success", f"Text extracted successfully: {output_path}")
            status_label.config(text="Text extraction completed.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def add_files_to_merge():
    files = filedialog.askopenfilenames(title="Select PDF files", filetypes=[("PDF Files", "*.pdf")])
    for file in files:
        filepath = file
        filename = os.path.basename(file)
        merge_file_data.append({'path': filepath, 'pages': 'all'})
        tree.insert("", "end", values=(filename, 'all'))
    update_status()


def on_range_edit(event):
    selected = tree.focus()
    if selected:
        item = tree.item(selected)
        col = tree.identify_column(event.x)
        if col == "#2":  # 2nd column = Page Range
            new_range = simpledialog.askstring("Page Range", "Enter page range (e.g., 1-3, 1,3 or 'all'):")
            if new_range:
                tree.set(selected, column="Page Range", value=new_range)
                idx = tree.index(selected)
                merge_file_data[idx]['pages'] = new_range
    update_status()


def move_up():
    selected = tree.focus()
    if not selected:
        return
    idx = tree.index(selected)
    if idx > 0:
        swap_items(idx, idx - 1)
    update_status()


def move_down():
    selected = tree.focus()
    if not selected:
        return
    idx = tree.index(selected)
    if idx < len(merge_file_data) - 1:
        swap_items(idx, idx + 1)
    update_status()


def swap_items(i, j):
    merge_file_data[i], merge_file_data[j] = merge_file_data[j], merge_file_data[i]
    tree.delete(*tree.get_children())
    for item in merge_file_data:
        tree.insert("", "end", values=(os.path.basename(item['path']), item['pages']))


def remove_selected():
    selected = tree.focus()
    if not selected:
        return
    idx = tree.index(selected)
    if 0 <= idx < len(merge_file_data):
        merge_file_data.pop(idx)
        tree.delete(selected)
    update_status()


def update_status():
    status_label.config(text=f"{len(merge_file_data)} PDF file(s) loaded")


def encrypt_pdf():
    if not merge_file_data:
        messagebox.showwarning("Warning", "No PDF file selected.")
        return

    # Only use the first selected file for encryption
    file_info = merge_file_data[0]
    file_path = file_info['path']

    try:
        password = simpledialog.askstring("Encrypt PDF", "Enter password to set:", show="*")
        if not password:
            return

        reader = PdfReader(file_path)
        writer = PdfWriter()

        # Add all pages (or use the specified page range if you prefer)
        page_range = file_info['pages']
        if page_range.lower() == "all":
            pages = range(len(reader.pages))
        elif "-" in page_range:
            start, end = map(int, page_range.split("-"))
            pages = range(start - 1, end)
        else:
            pages = [int(x.strip()) - 1 for x in page_range.split(",")]

        for i in pages:
            if 0 <= i < len(reader.pages):
                writer.add_page(reader.pages[i])
            else:
                messagebox.showerror("Error", f"Page out of range: {i + 1}")
                return

        writer.encrypt(password)

        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save encrypted PDF"
        )
        if output_path:
            with open(output_path, "wb") as f:
                writer.write(f)
            messagebox.showinfo("Success", f"PDF encrypted successfully: {output_path}")
            status_label.config(text="Encryption completed.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def decrypt_pdf():
    if not merge_file_data:
        messagebox.showwarning("Warning", "No PDF file selected.")
        return

    # Only use the first selected file for decryption
    file_info = merge_file_data[0]
    file_path = file_info['path']

    try:
        reader = PdfReader(file_path)

        if not reader.is_encrypted:
            messagebox.showinfo("Info", "The selected PDF is not encrypted.")
            return

        password = simpledialog.askstring("Decrypt PDF", "Enter password to unlock:", show="*")
        if not password:
            return

        if reader.decrypt(password) == 0:
            messagebox.showerror("Error", "Incorrect password.")
            return

        writer = PdfWriter()

        # Add all pages (or use the specified page range if you prefer)
        page_range = file_info['pages']
        if page_range.lower() == "all":
            pages = range(len(reader.pages))
        elif "-" in page_range:
            start, end = map(int, page_range.split("-"))
            pages = range(start - 1, end)
        else:
            pages = [int(x.strip()) - 1 for x in page_range.split(",")]

        for i in pages:
            if 0 <= i < len(reader.pages):
                writer.add_page(reader.pages[i])
            else:
                messagebox.showerror("Error", f"Page out of range: {i + 1}")
                return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save decrypted PDF"
        )
        if output_path:
            with open(output_path, "wb") as f:
                writer.write(f)
            messagebox.showinfo("Success", f"PDF decrypted successfully: {output_path}")
            status_label.config(text="Decryption completed.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Main window using TkinterDnD
root = TkinterDnD.Tk()
root.title("PDF Toolbox")
root.geometry("520x650")  # Increased height to accommodate new buttons
root.resizable(False, False)

tk.Label(root, text="PDF Toolbox", font=("Arial", 16)).pack(pady=10)

# File list section
tk.Label(root, text="PDF File List", font=("Arial", 12)).pack(pady=5)
tree = ttk.Treeview(root, columns=("Filename", "Page Range"), show="headings", height=8)
tree.heading("Filename", text="Filename")
tree.heading("Page Range", text="Page Range")
tree.column("Filename", width=300)
tree.column("Page Range", width=120)
tree.pack(pady=5)
tree.bind("<Double-1>", on_range_edit)

# Button frame for file operations
button_frame = tk.Frame(root)
button_frame.pack(pady=5)
tk.Button(button_frame, text="Add PDFs", command=add_files_to_merge).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Remove", command=remove_selected).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Move Up", command=move_up).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Move Down", command=move_down).grid(row=0, column=3, padx=5)

# Operation buttons
operation_frame = tk.Frame(root)
operation_frame.pack(pady=10)
tk.Button(operation_frame, text="Get PDFs", font=("Arial", 12), command=merge_pdfs).grid(row=0, column=0, padx=10)
tk.Button(operation_frame, text="Extract Text", font=("Arial", 12), command=extract_text_from_pdf).grid(row=0, column=1,
                                                                                                        padx=10)

# Security buttons
security_frame = tk.Frame(root)
security_frame.pack(pady=10)
tk.Button(security_frame, text="Encrypt PDF", font=("Arial", 12), command=encrypt_pdf).grid(row=0, column=0, padx=10)
tk.Button(security_frame, text="Decrypt PDF", font=("Arial", 12), command=decrypt_pdf).grid(row=0, column=1, padx=10)

# Status label
status_label = tk.Label(root, text="No PDF files loaded", font=("Arial", 10), fg="green")
status_label.pack(pady=5)

root.mainloop()