from re import I
from typing import Dict
import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import datetime
import json
from utils import (
    make_centered_title,
    drawing_mode_format_func,
    make_colored_square,
    show_map,
    back_callback,
    add_veggie_callback,
    save_layout_as_image,
    edit_callback,
    save_json_with_current_time,
    get_latest_json,
    update_mapping,
    get_json_files,
)


def update_state(canvas_result):
    to_save = {
        "canvas_data": canvas_result.json_data,
        "mapping": update_mapping(canvas_result.json_data),
    }

    save_json_with_current_time(to_save)

    # st.session_state.mapping = to_save["mapping"]
    st.session_state.base_layout = to_save["canvas_data"]

    if canvas_result.image_data is not None:
        save_layout_as_image(canvas_result.image_data)
    back_callback()
    st.experimental_rerun()


def edit_legend(obj=None):
    edited = False
    local_obj = obj or st
    # save_button = local_obj.form_submit_button("Save Changes")

    col_1, col_2, col_3, col_4 = local_obj.columns([2, 6, 4, 2])

    df = pd.json_normalize(st.session_state.mapping)
    col_1.subheader("Color")
    col_2.subheader("Name")
    col_3.subheader("Planted")
    to_save = get_latest_json()
    mapping = to_save["mapping"]
    geometry = to_save["canvas_data"]["objects"]
    for row in df.itertuples():
        # form = local_obj.form(f"form_{row.name}")
        col_1, col_2, col_3, col_4 = local_obj.columns([2, 6, 4, 2])

        new_color = col_1.color_picker("", value=row.color, key=f"color_{row.name}")
        new_name = col_2.text_input("", value=row.name, key=f"name_{row.name}")
        if row.date != "":
            new_date = col_3.date_input(
                "", value=datetime.datetime.strptime(row.date, "%Y%m%d"), key=f"date_{row.name}"
            )
        else:
            new_date = ""
        # if col_4.form_submit_button("Save"):
        if (
            (new_color != row.color)
            or (new_date != "" and new_date.strftime("%Y%m%d") != row.date)
            or (new_name != row.name)
        ):
            local_obj.write("triggered")

            old_index_mapping = next(i for i, m in enumerate(mapping) if m["color"] == row.color)
            old_index_geomentry = next(i for i, m in enumerate(geometry) if m["fill"] == row.color)
            mapping[old_index_mapping]["color"] = new_color
            mapping[old_index_mapping]["name"] = new_name
            mapping[old_index_mapping]["date"] = new_date.strftime("%Y%m%d")
            geometry[old_index_geomentry]["fill"] = new_color

            return to_save

    return None
    # if save_button:
    # save_json_with_current_time(to_save)
    # st.session_state.mapping = mapping
    # st.session_state.base_layout["objects"] = geometry
    # col_4.info("Change saved.")
    # edited = True
    # st.experimental_rerun()

    # # else:
    # # col_4.warning("No change.")
    # return edited


def edit():
    base_layout = st.session_state.base_layout

    make_centered_title("Edit current layout", 30)
    make_centered_title("Edit layout", 20, st.sidebar)
    st.sidebar.info(
        "Here you can move or resize existing shapes. \
        To delete a shape, double click on it."
    )
    st.sidebar.button("Back", on_click=back_callback)
    st.button("Back", on_click=back_callback, key="back_edit_1")

    show_legend(st.sidebar)

    edit_form = st.form("edit_form")
    col_1, _, col_3 = edit_form.columns([2, 1, 10])
    save_button = col_1.form_submit_button("Save Changes")
    with edit_form:
        canvas_result = st_canvas(
            background_image=st.session_state.background_img,
            height=1000,
            width=1600,
            drawing_mode="transform",
            initial_drawing=base_layout,
            key="edit_canvas",
        )

    # edit_form_2 = st.form("edit_form_2")

    test = edit_legend(edit_form)
    # st.session_state.canvas_result = canvas_result

    if save_button:
        if (canvas_result is None) or (
            canvas_result.json_data["objects"] == base_layout["objects"]
        ):
            col_3.warning("No change.")

        if canvas_result.image_data is not None:
            save_layout_as_image(canvas_result.image_data)

        if test is not None:
            save_json_with_current_time(test)
            st.session_state.mapping = test["mapping"]
            st.session_state.base_layout["objects"] = test["canvas_data"]["objects"]
            save_layout_as_image(canvas_result.image_data)
            st.experimental_rerun()

        # elif test:
        #     if canvas_result.image_data is not None:
        #         save_layout_as_image(canvas_result.image_data)
        #     back_callback()
        #     st.experimental_rerun()
        # else:
        # update_state(canvas_result)

        # save_layout_as_image(canvas_result.image_data)

    # if edit_legend():
    # save_layout_as_image(canvas_result.image_data)
    # st.experimental_rerun()
    # update_state(canvas_result)

    st.button("Back", on_click=back_callback, key="back_edit_2")


def show_legend(obj=None):
    local_obj = obj or st

    col_1, col_2, col_3 = local_obj.columns([2, 6, 4])

    df = pd.json_normalize(st.session_state.mapping)
    # df.query("name != 'Base Layout'", inplace=True)

    # if df.empty:
    #     return

    col_1.subheader("Color")
    col_2.subheader("Name")
    col_3.subheader("Planted")

    for row in df.itertuples():
        # if row.name == "Base Layout":
        # continue

        # recreate the columns to get some spacing
        col_1, col_2, col_3 = local_obj.columns([2, 6, 4])
        make_colored_square(row.color, obj=col_1)
        col_2.write(row.name)
        col_3.write(
            datetime.datetime.strptime(row.date, "%Y%m%d").date() if row.date != "" else row.date
        )


def add_new_veggie():
    base_layout = st.session_state.base_layout
    make_centered_title("Add New Veggetable", 30)
    make_centered_title("Add New Veggie", 20, st.sidebar)
    st.sidebar.info(
        "To add a new plant, enter a name, select which date is was planted and pick a color. Then draw it on the \
            right and when you're done, click on 'Save Veggie'."
    )
    st.button("Back", on_click=back_callback, key="back_main_1")
    st.sidebar.button("Back", on_click=back_callback)
    show_legend(st.sidebar)
    col_1, col_2, col_3 = st.columns([2, 2, 2])
    col_1.text_input("Name", key="new_veggie_name")
    col_1.date_input("Date planted", value=datetime.date.today(), key="new_veggie_date")
    fill_color = col_1.color_picker("Fill color: ", value="#0E28D0", key="new_veggie_color")

    drawing_mode = col_3.selectbox(
        "Tool:",
        ("rect", "freedraw", "line", "circle", "point"),
        format_func=drawing_mode_format_func,
    )
    stroke_width = col_3.slider("Border width: ", 1, 15, 4)
    form = st.form("new_veggie_form")

    add_button = form.form_submit_button("Save Veggie")
    st.button("Back", on_click=back_callback, key="back_main_2")

    with form:
        canvas_result = st_canvas(
            fill_color=fill_color,
            stroke_width=stroke_width,
            background_image=st.session_state.background_img,
            height=1000,
            width=1600,
            drawing_mode=drawing_mode,
            initial_drawing=base_layout,
            key="canvas",
        )
    if add_button:
        if st.session_state.new_veggie_name == "":
            col_1.error("Please enter a name.")
        elif (canvas_result.json_data is not None) and (
            canvas_result.json_data["objects"] != base_layout["objects"]
        ):
            update_state(canvas_result)


def layout():
    if "layout_mode" not in st.session_state:
        st.session_state.layout_mode = "legend"

    if "background_img" not in st.session_state:
        st.session_state.background_img = Image.open("img/background.png")

    if "mapping" not in st.session_state:
        data = get_latest_json()
        st.session_state.mapping = data["mapping"]
        st.session_state.base_layout = data["canvas_data"]

    # base_layout = get_latest_json()
    new_veg_ph = st.sidebar.container()

    legend = st.sidebar.container()

    if st.session_state.layout_mode == "add_veggie":
        add_new_veggie()
    elif st.session_state.layout_mode == "edit":
        edit()
    else:
        make_centered_title("Garden Layout", 30)
        make_centered_title("Current plants", 20, legend)
        legend.info("Here you can see the plant legend.")

        st.image("img/current_layout.png")
        show_legend(legend)

        legend.button("Edit", on_click=edit_callback)
        new_veg_ph.info("Click here to add a new vegetable.")
        new_veg_ph.button("Add New Veggie", on_click=add_veggie_callback)
        new_veg_ph.markdown("***")

    st.sidebar.markdown("***")

    show_ss = st.sidebar.button("Show session state")
    if show_ss:
        import os

        st.write(st.session_state)
        # st.write(os.listdir(os.getcwd()))
        st.write(os.listdir("data"))
        # st.write(os.listdir("img"))

    st.download_button(
        "Download Layout Data",
        data=json.dumps(get_latest_json(), indent=4),
        file_name=get_json_files()[-1],
    )


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
