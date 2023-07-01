# This demo lets you to explore the Udacity self-driving car image dataset.

import streamlit as st
import pandas as pd
import os, urllib

from lib.io_utils import download_file
from lib.ui_components import render_frame_selector_ui, render_object_detector_ui
from lib.image_utils import draw_image_with_boxes, load_image
from lib.yolo_model import yolo_v3_predict


from configs import DATA_URL_ROOT, EXTERNAL_DEPENDENCIES


# Download a single file and make its content available as a string.
@st.cache_resource(show_spinner=False)
def get_file_content_as_string(path):
    return open(path, "r").read()


def main():
    st.set_page_config(layout="wide")

    st.markdown("# Udacity self-driving-car object detection demo")
    st.markdown(
        """
        This project demonstrates the [Udacity self-driving-car dataset](https://github.com/udacity/self-driving-car) and 
        [YOLO object detection](https://pjreddie.com/darknet/yolo) into an interactive [Streamlit](https://streamlit.io) app. 
        This project is based on the publicly available [Streamlit Udacity borswer demo](https://github.com/streamlit/demo-self-driving/tree/master).
        """
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Download external dependencies.
    for filename in EXTERNAL_DEPENDENCIES.keys():
        download_file(filename)

    app_mode = st.selectbox("Choose the app mode", ["<select>", "Show the main.py source code", "Run the app"])
    st.markdown("""---""")
    if app_mode == "Show the main.py source code":
        st.code(get_file_content_as_string("main.py"))
    elif app_mode == "Run the app":
        run()


# This is the main app app itself, which appears when the user selects "Run the app".
def run():
    @st.cache_data
    def create_summary(metadata):
        one_hot_encoded = pd.get_dummies(metadata[["frame", "label"]], columns=["label"])
        summary = (
            one_hot_encoded.groupby(["frame"])
            .sum()
            .rename(
                columns={
                    "label_biker": "biker",
                    "label_car": "car",
                    "label_pedestrian": "pedestrian",
                    "label_trafficLight": "traffic light",
                    "label_truck": "truck",
                }
            )
        )
        return summary

    metadata = pd.read_csv(os.path.join(DATA_URL_ROOT, "labels.csv.gz"))
    summary = create_summary(metadata)

    # Draw the UI elements to search for objects and select parameters for the YOLO object detector
    col1, _, col2 = st.columns([0.49, 0.02, 0.49])
    with col1:
        st.markdown("### Frame configuration")
        selected_frame_index, selected_frame = render_frame_selector_ui(summary)
        if selected_frame_index == None:
            st.error("No frames fit the criteria. Please select different label or number.")
            return
    with col2:
        st.markdown("### Model configuration")
        confidence_threshold, overlap_threshold = render_object_detector_ui()

    # Load the image from S3.
    image_url = os.path.join(DATA_URL_ROOT, selected_frame)
    image = load_image(image_url)

    col1, _, col2 = st.columns([0.49, 0.02, 0.49])
    with col1:
        # Add boxes for objects on the image. These are the boxes for the ground image.
        boxes = metadata[metadata.frame == selected_frame].drop(columns=["frame"])
        draw_image_with_boxes(image, boxes, "Ground Truth", "**Human-annotated data** (frame `%i`)" % selected_frame_index)
    with col2:
        # Run the YOLO model to get boxes.
        yolo_boxes = yolo_v3_predict(image, confidence_threshold, overlap_threshold)
        draw_image_with_boxes(
            image,
            yolo_boxes,
            "Real-time Computer Vision",
            "**YOLO v3 Model** (overlap `%3.1f`) (confidence `%3.1f`)" % (overlap_threshold, confidence_threshold),
        )


if __name__ == "__main__":
    main()
