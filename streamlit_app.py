from typing import Dict
import pandas as pd
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import datetime
import json
from utils import (
    make_centered_title,
    drawing_mode_format_func,
    hex_to_rgb_str,
    make_colored_square,
    get_json_files,
    show_map,
    back_callback,
    add_veggie_callback,
    save_layout_as_image,
)


def show_legend(base_layout: Dict, obj=None):
    local_obj = obj or st
    make_centered_title("Current plants", 20, local_obj)
    local_obj.info("Here you can see the plant legend.")

    COLS = ["name", "date", "color"]
    df = pd.json_normalize(base_layout["objects"])
    for col in COLS:
        df[col] = df[col].astype("str")
    col_1, col_2, col_3 = local_obj.columns([2, 6, 4])

    col_1.subheader("Color")
    col_2.subheader("Name")
    col_3.subheader("Planted")

    for name, group in df[COLS].groupby(["date", "name"]):
        if name[1] == "Base Layout":
            continue

        # recreate the columns to get some spacing
        col_1, col_2, col_3 = local_obj.columns([2, 6, 4])
        color = group.color.iloc[0]
        make_colored_square(color, obj=col_1)
        col_2.write(name[1])
        col_3.write(datetime.datetime.strptime(name[0], "%Y%m%d").date())

    st.sidebar.markdown("***")


def add_new_veggie(base_layout: Dict):
    # st.session_state.show_add_button = False
    make_centered_title("Add New Veggie", 20, st.sidebar)
    st.sidebar.info(
        "To add a new plant, enter a name, select which date is was planted and pick a color. Then draw it on the \
            right and when you're done, click on 'Save Veggie'."
    )
    form = st.sidebar.form("new_veggie_form")
    veggie_name = form.text_input("Name")
    planted_date = form.date_input("Date planted", value=datetime.date.today())
    fill_color = form.color_picker("Fill color: ", value="#0E28D0")
    add_button = form.form_submit_button("Save Veggie")

    # drawing_mode_ph = st.sidebar.empty()
    drawing_mode = st.sidebar.selectbox(
        "Tool:", ("rect", "freedraw", "line", "transform"), format_func=drawing_mode_format_func
    )
    stroke_width = st.sidebar.slider("Border width: ", 1, 15, 4)
    # stroke_color = st.sidebar.color_picker("Border color: ")

    st.sidebar.button("Back", on_click=back_callback)
    background_image = Image.open("img/background.png")
    canvas_result = st_canvas(
        fill_color=hex_to_rgb_str(fill_color),
        stroke_width=stroke_width,
        # stroke_color=stroke_color,
        # background_color=bg_color,
        background_image=background_image,
        # background_image=Image.open("img/canvas_background.jpg"),
        update_streamlit=False,
        height=1000,
        # height=800
        width=1600,
        drawing_mode=drawing_mode,
        initial_drawing=base_layout,
        # initial_drawing=base_layout["geometry_data"],
        # point_display_radius=point_display_radius if drawing_mode == "point" else 0,
        # key="canvas",
    )
    loaded_length = len(base_layout["objects"])

    if add_button:
        if veggie_name == "":
            st.sidebar.error("Please enter a name.")
        else:
            new_objects = canvas_result.json_data["objects"][loaded_length:]

            if len(new_objects) > 0:
                for obj in new_objects:
                    obj["name"] = veggie_name
                    obj["date"] = planted_date.strftime("%Y%m%d")
                    obj["color"] = fill_color

            file_name = f'data/{datetime.datetime.now().strftime("%Y-%m-%d - %H:%M:%S")}.json'
            objects_to_save = new_objects + base_layout["objects"]
            to_save = canvas_result.json_data
            to_save["objects"] = objects_to_save
            with open(file_name, "w") as f:
                json.dump(to_save, f, indent=4)

            if canvas_result.image_data is not None:
                save_layout_as_image(canvas_result.image_data)
            back_callback()
            st.experimental_rerun()


def layout():
    # st.write(st.session_state)
    # st.sidebar.markdown("***")
    if "layout_mode" not in st.session_state:
        st.session_state.layout_mode = "legend"
    to_load = f"data/{get_json_files()[-1]}"
    with open(to_load, "r") as f:
        base_layout = json.load(f)

    legend = st.sidebar.container()

    if st.session_state.layout_mode == "add_veggie":
        add_new_veggie(base_layout)
    else:
        make_centered_title("Garden Layout", 30)
        st.image("img/current_layout.png")
        show_legend(base_layout, legend)
        st.sidebar.info("Click here to add a new vegetable.")
        st.sidebar.button("Add New Veggie", on_click=add_veggie_callback)

    st.sidebar.markdown("***")
    make_centered_title("Create new / modify layout", 20, st.sidebar)
    st.sidebar.info("Here you can change the base layout (paths etc.).")
    side_col_1, side_col_2 = st.sidebar.columns(2)
    new_base = side_col_1.button("Create new layout")
    modify_base = side_col_2.button("Modify current layout")

    if new_base:
        st.sidebar.warning("Not available yet.")

    if modify_base:
        st.sidebar.warning("Not available yet.")

    st.sidebar.markdown("***")


def map_page():
    make_centered_title("Map", 30)
    st.info(
        "The garden can be a bit hard to find the first time you go there, as it's not were you will land if you search for 'Grantoftegaard' \
        on Google. Instead, you can navigate to 'Grantoftegård (Stalde)'."
    )
    show_map((55.737438, 12.335938))


PAGES = {"Garden Layout": layout, "Map": map_page}


def main():
    st.set_page_config(
        page_title="Grantoftegaard",
        page_icon="https://st4.depositphotos.com/2046901/20637/v/1600/depositphotos_206373408-stock-illustration-spring-plant-icon-vector-illustration.jpg",
        layout="wide",
    )
    make_centered_title("Grantoftegaard Garden", 40)
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    st.sidebar.markdown("***")

    PAGES[selection]()


if __name__ == "__main__":
    main()
