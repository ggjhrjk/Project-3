from tkinter import *
from PIL import Image, ImageTk

def add_background_logo(parent, img_path="assets/logo.png", opacity=0.15):
    """Adds a semi-transparent background watermark logo to any Tkinter window/frame"""
    try:
        img = Image.open(img_path).convert("RGBA")

        # Get screen width and height dynamically
        w = parent.winfo_screenwidth()
        h = parent.winfo_screenheight()
        img = img.resize((int(w * 0.6), int(h * 0.6)))

        # Apply opacity
        alpha = img.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        img.putalpha(alpha)

        parent.bg_image = ImageTk.PhotoImage(img)

        bg_label = Label(parent, image=parent.bg_image, bg="#f2f2f2")
        bg_label.place(relx=0.5, rely=0.5, anchor="center")
    except Exception as e:
        print("Watermark Logo Warning:", e)


def smart_title(text):
    """Formats item names so uppercase acronyms stay uppercase while standard words are capitalized"""
    words = text.split()
    new_words = []
    for w in words:
        if w.isupper():
            new_words.append(w)
        else:
            new_words.append(w.capitalize())
    return " ".join(new_words)


def capitalize_words(event):
    """Capitalizes the first letter of each word in an Entry widget on FocusOut"""
    s = event.widget.get()
    formatted = ' '.join(word.capitalize() for word in s.split())
    event.widget.delete(0, END)
    event.widget.insert(0, formatted)