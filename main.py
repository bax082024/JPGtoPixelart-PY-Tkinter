import tkinter as tk
from tkinter import filedialog, Label
from PIL import Image, ImageTk, ExifTags


def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    if file_path:
        load_image(file_path)


def load_image(path):
    img = Image.open(path)

    # Handle EXIF orientation tag if present
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
        pass  # Image has no EXIF or orientation tag

    img.thumbnail((300, 300))  # Resize for preview
    preview = ImageTk.PhotoImage(img)
    label.config(image=preview)
    label.image = preview  # Keep reference


# --- UI Setup ---
root = tk.Tk()
root.title("Pixel Art Converter")
root.geometry("400x400")

btn = tk.Button(root, text="Open Image", command=open_file)
btn.pack(pady=10)

label = Label(root)
label.pack()

root.mainloop()
