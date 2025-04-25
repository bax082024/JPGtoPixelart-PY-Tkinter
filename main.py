import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, ExifTags
import numpy as np
import os

# --- Global State ---
original_image = None
pixelated_image = None

# --- Preset Palettes ---
PRESET_PALETTES = {
    "Default (16 colors)": None,
    "GameBoy": [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)],
    "NES": [(0, 0, 0), (255, 255, 255), (128, 128, 128), (255, 0, 0)]
}

# --- Image Loading ---
def load_image_from_path(file_path):
    global original_image
    if file_path:
        img = Image.open(file_path)
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif is not None:
                orientation_value = exif.get(orientation)
                if orientation_value == 3:
                    img = img.rotate(180, expand=True)
                elif orientation_value == 6:
                    img = img.rotate(270, expand=True)
                elif orientation_value == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass
        original_image = img.copy()
        show_image(img)

# --- Open File Dialog ---
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    load_image_from_path(file_path)

# --- Display Image ---
def show_image(image):
    preview = image.copy()
    preview.thumbnail((300, 300))
    bg_color = bg_color_var.get()
    if bg_color != "Transparent":
        bg = Image.new("RGB", (300, 300), bg_color.lower())
        offset = ((300 - preview.width) // 2, (300 - preview.height) // 2)
        bg.paste(preview, offset)
        preview = bg
    preview = ImageTk.PhotoImage(preview)
    label.config(image=preview)
    label.image = preview

# --- Pixelation ---
def pixelate_image():
    global original_image, pixelated_image
    if original_image:
        level = pixel_slider.get()
        small = original_image.resize((level, level), resample=Image.NEAREST)
        pixelated = small.resize((300, 300), resample=Image.NEAREST)

        selected_palette = palette_combo.get()
        palette = PRESET_PALETTES.get(selected_palette)

        if palette:
            pixelated = apply_custom_palette(pixelated, palette)
        else:
            colors = int(color_entry.get()) if color_entry.get().isdigit() else 16
            pixelated = pixelated.convert("P", palette=Image.ADAPTIVE, colors=colors).convert("RGB")

        pixelated_image = pixelated
        show_image(pixelated)

# --- Save Image ---
def save_image():
    global pixelated_image
    if pixelated_image:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("BMP", "*.bmp"), ("ICO", "*.ico"), ("GIF", "*.gif")]
        )
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".gif":
                pixelated_image.save(file_path, save_all=True)
            else:
                pixelated_image.save(file_path)
            print(f"Image saved to: {file_path}")

# --- Export 2x Sprite ---
def export_2x_sprite():
    global pixelated_image
    if pixelated_image:
        sprite = pixelated_image.resize((600, 600), resample=Image.NEAREST)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            title="Save 2x Sprite Image"
        )
        if file_path:
            sprite.save(file_path)
            print(f"2x sprite image saved: {file_path}")

# --- Reset Image ---
def reset_image():
    global original_image
    if original_image:
        show_image(original_image)

# --- Apply Custom Palette ---
def apply_custom_palette(img, palette):
    img = img.convert("RGB")
    data = np.array(img)
    flat_data = data.reshape((-1, 3))
    new_data = np.array([min(palette, key=lambda c: np.linalg.norm(p - c)) for p in flat_data], dtype=np.uint8)
    new_data = new_data.reshape(data.shape)
    return Image.fromarray(new_data)

# --- Drag & Drop ---
def handle_drop(event):
    dropped_file = event.data.strip('{}')
    load_image_from_path(dropped_file)

# --- Background Color Logic ---
def apply_bg_color(_=None):
    color = bg_color_var.get()
    if color == "Transparent":
        label.config(bg=root.cget("bg"))
    else:
        label.config(bg=color.lower())

# --- UI Setup ---
root = TkinterDnD.Tk()
root.title("Pixel Art Converter")
root.geometry("420x650")

bg_color_var = tk.StringVar(value="White")

btn_open = tk.Button(root, text="Open Image", command=open_file)
btn_open.pack(pady=5)

btn_pixelate = tk.Button(root, text="Pixelate Image", command=pixelate_image)
btn_pixelate.pack(pady=5)

pixel_slider = tk.Scale(root, from_=4, to=64, resolution=4, orient="horizontal", label="Pixelation Level")
pixel_slider.set(32)
pixel_slider.pack(pady=5)

color_label = tk.Label(root, text="Color Palette Limit")
color_label.pack()
color_entry = tk.Entry(root)
color_entry.insert(0, "16")
color_entry.pack(pady=5)

palette_label = tk.Label(root, text="Preset Palette")
palette_label.pack()
palette_combo = Combobox(root, values=list(PRESET_PALETTES.keys()))
palette_combo.set("Default (16 colors)")
palette_combo.pack(pady=5)

bg_label = tk.Label(root, text="Preview Background")
bg_label.pack()
bg_dropdown = tk.OptionMenu(root, bg_color_var, "White", "Black", "Gray", "Transparent", command=apply_bg_color)
bg_dropdown.pack(pady=5)

btn_save = tk.Button(root, text="Save Pixelated Image", command=save_image)
btn_save.pack(pady=5)

btn_export_2x = tk.Button(root, text="Export 2x Sprite Size", command=export_2x_sprite)
btn_export_2x.pack(pady=5)

btn_reset = tk.Button(root, text="Reset to Original", command=reset_image)
btn_reset.pack(pady=5)

label = tk.Label(root)
label.pack(pady=10)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', handle_drop)

root.mainloop()
