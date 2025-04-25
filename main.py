import tkinter as tk
from tkinter import filedialog, Label, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, ExifTags

original_image = None
last_pixelated_image = None


def load_image_from_path(file_path):
    global original_image
    if file_path:
        img = Image.open(file_path)

        # Handle EXIF orientation
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


def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    load_image_from_path(file_path)


def show_image(image):
    image.thumbnail((300, 300))
    preview = ImageTk.PhotoImage(image)
    label.config(image=preview)
    label.image = preview


def pixelate_image():
    global original_image, last_pixelated_image
    if original_image:
        pixel_size = pixel_slider.get()
        pixelated = original_image.resize((pixel_size, pixel_size), resample=Image.NEAREST)
        pixelated = pixelated.resize((300, 300), resample=Image.NEAREST)
        last_pixelated_image = pixelated.copy()
        show_image(pixelated)


def save_image():
    global last_pixelated_image
    if last_pixelated_image:
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if file_path:
            try:
                last_pixelated_image.save(file_path)
                messagebox.showinfo("Saved", f"Image saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{e}")
    else:
        messagebox.showwarning("No image", "Please pixelate an image before saving.")


def handle_drop(event):
    dropped_file = event.data.strip('{}')  # Strip curly braces if path has spaces
    load_image_from_path(dropped_file)


# --- UI Setup ---
root = TkinterDnD.Tk()
root.title("Pixel Art Converter")
root.geometry("400x580")

btn_open = tk.Button(root, text="Open Image", command=open_file)
btn_open.pack(pady=10)

btn_pixelate = tk.Button(root, text="Pixelate Image", command=pixelate_image)
btn_pixelate.pack(pady=5)

pixel_slider = tk.Scale(root, from_=4, to=64, resolution=4, orient="horizontal", label="Pixelation Level")
pixel_slider.set(32)
pixel_slider.pack(pady=10)

btn_save = tk.Button(root, text="Save Pixelated Image", command=save_image)
btn_save.pack(pady=10)

label = Label(root)
label.pack(pady=10)

# Enable drag and drop
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', handle_drop)


root.mainloop()
