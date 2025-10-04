# CTkCodeBox.py
"""
CTkCodeBox
Author: Akash Bora
License: MIT
"""

import customtkinter
from tkinter import Text, END, INSERT, SEL
import re

class CTkCodeBox(customtkinter.CTkFrame):
    def __init__(self,
                 master: any,
                 width: int = 500,
                 height: int = 400,
                 corner_radius: int | str | None = 10,
                 border_width: int | str | None = 1,
                 fg_color: str | tuple[str, str] | None = "transparent",
                 border_color: str | tuple[str, str] | None = "grey50",
                 text_color: str | tuple[str, str] | None = None,
                 font: tuple | customtkinter.CTkFont = ("Courier New", 14),
                 wrap: str = "none",
                 language: str = "python",
                 theme: str = "classic",
                 **kwargs):

        super().__init__(master, width=width, height=height, corner_radius=corner_radius,
                 border_width=border_width, **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.border_width = border_width
        self.language = language

        self.text_color = customtkinter.ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else text_color

        self.font = customtkinter.CTkFont(family=font[0], size=font[1]) if isinstance(font, tuple) else font
        
        self.linenumbers = Text(self, width=4, height=15, bd=0, relief="flat",
                                     font=self.font, state="disabled",
                                     highlightthickness=0, bg=self._apply_appearance_mode(
                                         customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]))
        
        self.linenumbers.grid(row=0, column=0, sticky="ns", padx=(self.border_width,0), pady=self.border_width)

        self.textbox = Text(self, width=15, height=15, bd=0, wrap=wrap, insertofftime=0,
                            highlightthickness=self.border_width,
                            font=self.font, relief="flat",
                            highlightcolor=self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["border_color"]),
                            highlightbackground=self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["border_color"]))
        
        self.textbox.grid(row=0, column=1, sticky="nsew", pady=self.border_width, padx=(0,self.border_width))

        self.v_scroll = customtkinter.CTkScrollbar(self, orientation="vertical", command=self.textbox.yview)
        #self.v_scroll.grid(row=0, column=2, sticky="ns", pady=self.border_width, padx=(0,self.border_width))
        self.h_scroll = customtkinter.CTkScrollbar(self, orientation="horizontal", command=self.textbox.xview)
        #self.h_scroll.grid(row=1, column=1, sticky="ew", pady=(0,self.border_width), padx=(0,self.border_width))
        
        self.textbox.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
       
        self.textbox.bind("<<Modified>>", self._on_text_modified)
        self.textbox.bind("<MouseWheel>", self.handle_mouse_wheel)
        self.textbox.bind("<Button-4>", self.handle_mouse_wheel)
        self.textbox.bind("<Button-5>", self.handle_mouse_wheel)
        
        # for tab spaces
        self.textbox.bind("<Tab>", self._on_tab)
        self.textbox.bind("<Shift-Tab>", self._on_shift_tab)
        self.textbox.bind("<Return>", self._on_return)
        
        self.set_theme(theme)
        self.color_syntax()
        
    def _on_tab(self, event=None):
        self.textbox.insert(INSERT, " " * 4)
        return "break"

    def _on_shift_tab(self, event=None):
        # get the current line
        line_start = self.textbox.index(f"{INSERT} linestart")
        line_end = self.textbox.index(f"{INSERT} lineend")
        line_text = self.textbox.get(line_start, line_end)

        # remove 4 spaces from the beginning of the line
        if line_text.startswith(" " * 4):
            self.textbox.delete(line_start, f"{line_start} + 4c")
            
        return "break"
        
    def _on_return(self, event=None):
        # get the current line
        line_start = self.textbox.index(f"{INSERT} linestart")
        line_text = self.textbox.get(line_start, f"{INSERT} lineend")

        # count the number of leading spaces
        leading_spaces = len(line_text) - len(line_text.lstrip(" "))
        
        # insert a newline and the same number of leading spaces
        self.textbox.insert(INSERT, f"\n{' ' * leading_spaces}")
        
        return "break"
    
    def handle_mouse_wheel(self, event):
        if event.delta > 0 or event.num==4:
            self.textbox.yview_scroll(-1, "units")
            self.linenumbers.yview_scroll(-1, "units")
        elif event.delta < 0 or event.num==5:
            self.textbox.yview_scroll(1, "units")
            self.linenumbers.yview_scroll(1, "units")

        return "break"

    def _on_text_modified(self, event=None):
        self.update_line_numbers()
        self.color_syntax()
        
    def update_line_numbers(self):
        # Get the number of lines in the textbox
        num_lines = self.textbox.get("1.0", "end-1c").count("\n") + 1
        
        # Update the line numbers in the line number text widget
        self.linenumbers.config(state="normal")
        self.linenumbers.delete("1.0", "end")
        for i in range(1, num_lines + 1):
            self.linenumbers.insert("end", f"{i}\n")
        self.linenumbers.config(state="disabled")

        # scroll the line numbers and textbox together
        self.linenumbers.yview_moveto(self.textbox.yview()[0])

    def color_syntax(self):
        # Remove all previous tags
        for tag in self.textbox.tag_names():
            if tag != SEL:
                self.textbox.tag_remove(tag, "1.0", "end")

        # Add new tags
        for token, content in self.syntax.items():
            for keyword in content:
                for match in re.finditer(keyword, self.textbox.get("1.0", "end")):
                    start = match.start()
                    end = match.end()
                    self.textbox.tag_add(token, f"1.0 + {start}c", f"1.0 + {end}c")
        
    def set_theme(self, theme: str):
        if theme=="dark":
            self.syntax = {
                "keywords": ["\mif\M", "\melse\M", "\melif\M", "\mfor\M", "\mwhile\M", "\mbreak\M", "\mcontinue\M",
                             "\mpass\M", "\mtry\M", "\mexcept\M", "\mfinally\M", "\mraise\M", "\mimport\M",
                             "\mfrom\M", "\mas\M", "\min\M", "\mis\M", "\mwith\M", "\myield\M", "\massert\M",
                             "\mclass\M", "\mdef\M", "\mdel\M", "\mglobal\M", "\mnonlocal\M", "\mlambda\M",
                             "\mreturn\M", "\mexec\M", "\min\M", "\mis\M", "\mnot\M", "\mor\M", "\mand\M"],
                "builtins": ["\mstr\M", "\mint\M", "\mfloat\M", "\mlist\M", "\mtuple\M", "\mdict\M", "\mset\M",
                             "\mbool\M", "\mbytes\M", "\mbytearray\M", "\mobject\M", "\mtype\M", "\mNone\M", "\mTrue\M",
                             "\mFalse\M", "\msuper\M", "\mprint\M", "\mdict\M", "\mproperty\M", "\mround\M", "\mabs\M",
                             "\mall\M", "\many\M", "\mascii\M", "\mbin\M", "\mcallable\M", "\mchr\M", "\mclassmethod\M",
                             "\mcomplex\M", "\mdelattr\M", "\mdivmod\M", "\menumerate\M", "\mfilter\M", "\mformat\M",
                             "\mhash\M", "\mhex\M", "\mid\M", "\minput\M", "\misinstance\M", "\missubclass\M",
                             "\miter\M", "\mlen\M", "\mmap\M", "\mmax\M", "\mmin\M", "\mnext\M", "\moct\M", "\mopen\M",
                             "\mord\M", "\mpow\M", "\mrepr\M", "\mreversed\M", "\msorted\M", "\mstaticmethod\M",
                             "\msum\M", "\mvars\M", "\mzip\M", "\m__import__\M"],
                "comments": [r"#.*"],
                "string": [r"\"(.*?)\"", r"\'(.*?)\'"],
                "function": [r"\b(\w+)\s*\("],
                "self": ["\mself\M"],
                "numbers": [r"\b(\d+)\b"],
            }
            self.textbox.config(
                background="#2b2b2b",
                foreground="#d0d0d0",
                insertbackground="white"
            )
            self.linenumbers.config(
                background="#2b2b2b",
                foreground="#d0d0d0",
            )
            self.textbox.tag_config("keywords", foreground="#cc7832")
            self.textbox.tag_config("comments", foreground="#808080")
            self.textbox.tag_config("string", foreground="#6a8759")
            self.textbox.tag_config("function", foreground="#ffc66d")
            self.textbox.tag_config("builtins", foreground="#9876aa")
            self.textbox.tag_config("self", foreground="#94558D")
            self.textbox.tag_config("numbers", foreground="#6897bb")
            self.textbox.tag_config(SEL, background=customtkinter.ThemeManager.theme["CTkTextbox"]["fg_color"][1])
            return
        
        if theme=="dracula":
            self.syntax = {
                "keywords": ["\mif\M", "\melse\M", "\melif\M", "\mfor\M", "\mwhile\M", "\mbreak\M", "\mcontinue\M",
                             "\mpass\M", "\mtry\M", "\mexcept\M", "\mfinally\M", "\mraise\M", "\mimport\M",
                             "\mfrom\M", "\mas\M", "\min\M", "\mis\M", "\mwith\M", "\myield\M", "\massert\M",
                             "\mclass\M", "\mdef\M", "\mdel\M", "\mglobal\M", "\mnonlocal\M", "\mlambda\M",
                             "\mreturn\M", "\mexec\M", "\min\M", "\mis\M", "\mnot\M", "\mor\M", "\mand\M"],
                "builtins": ["\mstr\M", "\mint\M", "\mfloat\M", "\mlist\M", "\mtuple\M", "\mdict\M", "\mset\M",
                             "\mbool\M", "\mbytes\M", "\mbytearray\M", "\mobject\M", "\mtype\M", "\mNone\M", "\mTrue\M",
                             "\mFalse\M", "\msuper\M", "\mprint\M", "\mdict\M", "\mproperty\M", "\mround\M", "\mabs\M",
                             "\mall\M", "\many\M", "\mascii\M", "\mbin\M", "\mcallable\M", "\mchr\M", "\mclassmethod\M",
                             "\mcomplex\M", "\mdelattr\M", "\mdivmod\M", "\menumerate\M", "\mfilter\M", "\mformat\M",
                             "\mhash\M", "\mhex\M", "\mid\M", "\minput\M", "\misinstance\M", "\missubclass\M",
                             "\miter\M", "\mlen\M", "\mmap\M", "\mmax\M", "\mmin\M", "\mnext\M", "\moct\M", "\mopen\M",
                             "\mord\M", "\mpow\M", "\mrepr\M", "\mreversed\M", "\msorted\M", "\mstaticmethod\M",
                             "\msum\M", "\mvars\M", "\mzip\M", "\m__import__\M"],
                "comments": [r"#.*"],
                "string": [r"\"(.*?)\"", r"\'(.*?)\'"],
                "function": [r"\b(\w+)\s*\("],
                "self": ["\mself\M"],
                "numbers": [r"\b(\d+)\b"],
            }
            self.textbox.config(
                background="#282a36",
                foreground="#f8f8f2",
                insertbackground="white"
            )
            self.linenumbers.config(
                background="#282a36",
                foreground="#f8f8f2",
            )
            self.textbox.tag_config("keywords", foreground="#ff79c6")
            self.textbox.tag_config("comments", foreground="#6272a4")
            self.textbox.tag_config("string", foreground="#f1fa8c")
            self.textbox.tag_config("function", foreground="#50fa7b")
            self.textbox.tag_config("builtins", foreground="#8be9fd")
            self.textbox.tag_config("self", foreground="#bd93f9")
            self.textbox.tag_config("numbers", foreground="#bd93f9")
            self.textbox.tag_config(SEL, background=customtkinter.ThemeManager.theme["CTkTextbox"]["fg_color"][1])
            return
        
        self.syntax = {
            "keywords": ["\mif\M", "\melse\M", "\melif\M", "\mfor\M", "\mwhile\M", "\mbreak\M", "\mcontinue\M",
                         "\mpass\M", "\mtry\M", "\mexcept\M", "\mfinally\M", "\mraise\M", "\mimport\M",
                         "\mfrom\M", "\mas\M", "\min\M", "\mis\M", "\mwith\M", "\myield\M", "\massert\M",
                         "\mclass\M", "\mdef\M", "\mdel\M", "\mglobal\M", "\mnonlocal\M", "\mlambda\M",
                         "\mreturn\M", "\mexec\M", "\min\M", "\mis\M", "\mnot\M", "\mor\M", "\mand\M"],
            "builtins": ["\mstr\M", "\mint\M", "\mfloat\M", "\mlist\M", "\mtuple\M", "\mdict\M", "\mset\M",
                         "\mbool\M", "\mbytes\M", "\mbytearray\M", "\mobject\M", "\mtype\M", "\mNone\M", "\mTrue\M",
                         "\mFalse\M", "\msuper\M", "\mprint\M", "\mdict\M", "\mproperty\M", "\mround\M", "\mabs\M",
                         "\mall\M", "\many\M", "\mascii\M", "\mbin\M", "\mcallable\M", "\mchr\M", "\mclassmethod\M",
                         "\mcomplex\M", "\mdelattr\M", "\mdivmod\M", "\menumerate\M", "\mfilter\M", "\mformat\M",
                         "\mhash\M", "\mhex\M", "\mid\M", "\minput\M", "\misinstance\M", "\missubclass\M",
                         "\miter\M", "\mlen\M", "\mmap\M", "\mmax\M", "\mmin\M", "\mnext\M", "\moct\M", "\mopen\M",
                         "\mord\M", "\mpow\M", "\mrepr\M", "\mreversed\M", "\msorted\M", "\mstaticmethod\M",
                         "\msum\M", "\mvars\M", "\mzip\M", "\m__import__\M"],
            "comments": [r"#.*"],
            "string": [r"\"(.*?)\"", r"\'(.*?)\'"],
            "function": [r"\b(\w+)\s*\("],
            "self": ["\mself\M"],
            "numbers": [r"\b[0-9]+\b"],
        }
        self.textbox.config(
            background=self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkTextbox"]["fg_color"]),
            foreground=self._apply_appearance_mode(self.text_color),
            insertbackground=self._apply_appearance_mode(self.text_color)
        )
        self.linenumbers.config(
            background=self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkTextbox"]["fg_color"]),
            foreground=self._apply_appearance_mode(self.text_color),
        )
        self.textbox.tag_config("keywords", foreground="blue")
        self.textbox.tag_config("comments", foreground="green")
        self.textbox.tag_config("string", foreground="red")
        self.textbox.tag_config("function", foreground="purple")
        self.textbox.tag_config("builtins", foreground="orange")
        self.textbox.tag_config("self", foreground="brown")
        self.textbox.tag_config("numbers", foreground="cyan")
        self.textbox.tag_config(SEL, background=self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkTextbox"]["border_color"]))

    def get(self, start="1.0", end="end-1c"):
        return self.textbox.get(start,end)

    def insert(self, index="end", text=""):
        self.textbox.insert(index, text)
        
    def delete(self, start="1.0", end="end"):
        self.textbox.delete(start, end)

    def configure(self, **kwargs):
        if "language" in kwargs:
            self.language = kwargs.pop("language")
            
        if "font" in kwargs:
            self.font = customtkinter.CTkFont(family=font[0], size=font[1]) if isinstance(font, tuple) else font
            self.textbox.configure(font=self.font)
            self.linenumbers.configure(font=self.font)
            
        if "text_color" in kwargs:
            self.text_color = kwargs.pop("text_color")
            self.textbox.configure(fg=self.text_color)
            self.linenumbers.configure(fg=self.text_color)

        if "fg_color" in kwargs:
            self.textbox.configure(bg=kwargs["fg_color"])
            self.linenumbers.configure(bg=kwargs["fg_color"])
            
        super().configure(**kwargs)

    def _apply_appearance_mode(self, color):
        if customtkinter.get_appearance_mode()=="Light":
            return color[0]
        else:
            return color[1]