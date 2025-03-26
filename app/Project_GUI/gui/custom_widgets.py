# gui/custom_widgets.py
"""
@file custom_widgets.py
@brief Enthält benutzerdefinierte Widgets (z.B. PlaceholderEntry).
"""

from ttkbootstrap import ttk
import tkinter as tk
from config.settings import THEME_COLORS

class PlaceholderEntry(ttk.Entry):
    """
    @class PlaceholderEntry
    @brief Ein ttk.Entry mit Platzhaltertext, der verschwindet, sobald man hineinklickt.
    """
    def __init__(self, master=None, placeholder="PLATZHALTER", color='grey', bg_color=None, style=None, *args, **kwargs):
        if style:
            kwargs['style'] = style
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['foreground']

        if bg_color:
            self.configure(background=bg_color)
        else:
            self.configure(background=THEME_COLORS["background_color"])

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        if not self.get():
            self.insert(0, self.placeholder)
            self['foreground'] = self.placeholder_color

    def foc_in(self, *args):
        if self.get() == self.placeholder:
            self.delete('0', 'end')
            self['foreground'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()
