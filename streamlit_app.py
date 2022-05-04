import pandas as pd
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
    get_formatted_name,
)


def main():
    layout()


def layout():
    st.sidebar.markdown("***")
    make_centered_title("Current plants", 20, st.sidebar)
    st.sidebar.info("Here you can see the plant legend.")

    legend = st.sidebar.container()

    st.sidebar.markdown("***")

    make_centered_title("Add New Veggie", 20, st.sidebar)

    st.sidebar.info(
        "To add a new plant, enter a name, select which date is was planted and pick a color. Then draw it on the right and when you're done, click on 'Save Veggie'."
    )
    veggie_name = st.sidebar.text_input("Name")
    planted_date = st.sidebar.date_input("Date planted", value=datetime.date.today())
    fill_color = st.sidebar.color_picker("Fill color: ", value="#0E28D0")

    # drawing_mode_ph = st.sidebar.empty()
    drawing_mode = st.sidebar.selectbox(
        "Tool:", ("rect", "freedraw", "line", "transform"), format_func=drawing_mode_format_func
    )
    stroke_width = st.sidebar.slider("Border width: ", 1, 15, 4)
    # stroke_color = st.sidebar.color_picker("Border color: ")

    add_button = st.sidebar.button("Save Veggie")
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

    #     to_load = "data/0_base_layout.json"
    #     drawing_mode = "transform"
    #     save_modify = st.sidebar.button("Save")
    # else:
    to_load = f"data/{get_json_files()[-1]}"

    # realtime_update = st.sidebar.checkbox("Update in realtime", True)
    st.sidebar.markdown("***")

    make_centered_title("Garden Layout")

    st.write(to_load)
    # with open("data/0_base_layout.json", "r") as f:
    with open(to_load, "r") as f:
        base_layout = json.load(f)

    # st.write(base_layout)

    # st.write(base_layout)
    loaded_length = len(base_layout["objects"])
    st.write(loaded_length)
    # st.write(type(base_layout))

    canvas_result = st_canvas(
        fill_color=hex_to_rgb_str(fill_color),
        stroke_width=stroke_width,
        # stroke_color=stroke_color,
        # background_color=bg_color,
        background_image=Image.open("img/background.png"),
        # background_image=Image.open("img/canvas_background.jpg"),
        # update_streamlit=realtime_update,
        height=1000,
        # height=800
        width=1600,
        drawing_mode=drawing_mode,
        initial_drawing=base_layout,
        # initial_drawing=base_layout["geometry_data"],
        # point_display_radius=point_display_radius if drawing_mode == "point" else 0,
        key="canvas",
    )

    if add_button:
        if veggie_name == "":
            st.sidebar.error("Please enter a name.")
        else:
            # canvas_result.json_data["objects"][0]["test"] = "asdölkfgöslkdfklöjasölkdjfölkjasdfjkl"
            new_objects = canvas_result.json_data["objects"][loaded_length:]

            if len(new_objects) > 0:
                for obj in new_objects:
                    obj["name"] = veggie_name
                    obj["date"] = planted_date.strftime("%Y%m%d")
                    obj["color"] = fill_color

            st.write(new_objects)

            file_name = f'data/{datetime.datetime.now().strftime("%Y-%m-%d - %H:%M:%S")}.json'
            objects_to_save = new_objects + base_layout["objects"]
            to_save = canvas_result.json_data
            to_save["objects"] = objects_to_save
            with open(file_name, "w") as f:
                json.dump(to_save, f, indent=4)

    # for obj in canvas_result.json_data["objects"]:
    #     obj["name"] = veggie_name
    #     obj["date"] = planted_date.strftime("%Y%m%d")

    # st.write(canvas_result.json_data)

    # else:
    #     test = PlantField(
    #         geometry_data=canvas_result.json_data,
    #         color=fill_color,
    #         name=veggie_name,
    #         date=planted_date.strftime("%Y%m%d"),
    #     )
    #     st.write(test.json())

    # file_name = f"data/0_base_layout.json"

    # Do something interesting with the image data and paths
    # if canvas_result.image_data is not None:
    # st.image(canvas_result.image_data)

    # if canvas_result.json_data is not None:
    COLS = ["name", "date", "color"]
    df = pd.json_normalize(base_layout["objects"])
    for col in COLS:
        df[col] = df[col].astype("str")
    # st.dataframe(objects[COLS])

    # for row in df[COLS].itertuples():
    # st.write(row)
    col_1, col_2, col_3 = legend.columns([3, 5, 5])

    col_1.subheader("Color")
    col_2.subheader("Name")
    col_3.subheader("Planted")

    for name, group in df[COLS].sort_values("date").groupby(["name", "date"]):
        if name[0] == "Base Layout":
            continue
        color = group.color[0]
        name_str = get_formatted_name(name[0])

        make_colored_square(color, obj=col_1)
        col_2.write(name_str)
        col_3.write(datetime.datetime.strptime(name[1], "%Y%m%d").date())
        # make_colored_square("#000000", obj=col_1)
        # make_colored_square("#000000", obj=col_2)

    # col_2.write(get_formatted_name("aösldfjasödf ölasdjfölasdlfj"))
    # col_2.write("aösldfjasödfölasdjfölasdlfj")
    # col_3.write(datetime.datetime.strptime(name[1], "%Y%m%d").date())


if __name__ == "__main__":
    st.set_page_config(
        page_title="Grantoftegaard",
        page_icon="https://st4.depositphotos.com/2046901/20637/v/1600/depositphotos_206373408-stock-illustration-spring-plant-icon-vector-illustration.jpg",
        layout="wide",
    )
    make_centered_title("Grantoftegaard Garden", 40)
    # st.sidebar.subheader("Configuration")
    main()
