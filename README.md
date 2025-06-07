# Linux-Style GTK Calculator

A simple Linux-style calculator built with Python and GTK3. Inspired by the GNOME Calculator.

## Features

- Dark theme GTK UI  
- Full keyboard support  
- Functions: π, √, x², mod  
- History and input area  
- Custom styling with CSS  

## Requirements

- Python 3  
- GTK3  
- PyGObject  

## Installation

**For Ubuntu/Debian:**

```bash
sudo apt install python3-gi gir1.2-gtk-3.0
```

### Fedora

```bash
sudo dnf install python3-gobject gtk3
```
## How to Use

1. Place both `calc.py` and `backend.py` in the same folder.  
2. Open a terminal in that folder.  
3. Run the app using:

```bash
python3 calc.py
```


## File Structure

- `calc.py` — Main application window and UI
- `backend.py` — Expression evaluation logic

