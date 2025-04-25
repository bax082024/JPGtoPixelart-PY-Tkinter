import tkinter as tk
from tkinter import filedialog, Label
from PIL import Image, ImageTk, ExifTags

original_image = None


def open_file():
    global original_image
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
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


def show_image(image):
    image.thumbnail((300, 300))
    preview = ImageTk.PhotoImage(image)
    label.config(image=preview)
    label.image = preview


def pixelate_image():
    global original_image
    if original_image:
        pixelated = original_image.resize((32, 32), resample=Image.NEAREST)
        pixelated = pixelated.resize((300, 300), resample=Image.NEAREST)
        show_image(pixelated)


# --- UI ---
root = tk.Tk()
root.title("Pixel Art Converter")
root.geometry("400x450")

btn_open = tk.Button(root, text="Open Image", command=open_file)
btn_open.pack(pady=10)

btn_pixelate = tk.Button(root, text="Pixelate Image", command=pixelate_image)
btn_pixelate.pack(pady=5)

label = Label(root)
label.pack()

root.mainloop()
