import os
from typing import Dict, List
import datetime
import re
import streamlit as st


def get_formatted_name(name: str, line_length: int = 15):
    if len(name) <= 15:
        return name
    return "\n".join(name[i : i + line_length] for i in range(0, len(name), line_length))


def get_json_files():
    return sorted(os.listdir("data"))


def make_centered_title(text: str, size: int = 25, obj=None):
    html = f"<h1 style='text-align: center; font-size:{size}px'>{text}</h1>"
    if obj is None:
        st.markdown(html, unsafe_allow_html=True)
    else:
        obj.markdown(html, unsafe_allow_html=True)


def drawing_mode_format_func(inp: str):
    return "Rectangle" if inp == "rect" else inp.capitalize()


def hex_to_rgb_str(hex: str):
    h = hex.lstrip("#")
    rgb = tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.5)"


def make_colored_square(hex_color: str, size: int = 30, obj=None):
    local_obj = obj or st
    local_obj.markdown(
        f'<div style="height:{size}px;width:{size}px;background-color:{hex_color};border-radius:10px 10px 10px 10px;border-style:dotted;border-color:#19191A"></div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    print(get_formatted_name("öasdljkfaösdlkfjaösdlfkadsfölkajsdfölaksjdfasöldfkjasödlfköj"))
