import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

from configs import MIN_OBJECTS, MAX_OBJECTS


def render_frame_selector_ui(summary):
    object_type = st.selectbox("Search for which objects?", summary.columns, 2)

    selected_frames = summary[np.logical_and(summary[object_type] >= MIN_OBJECTS, summary[object_type] <= MAX_OBJECTS)].index
    if len(selected_frames) < 1:
        return None, None
    selected_frame_index = st.slider("Choose a frame (index)", 0, len(selected_frames) - 1, 0)

    objects_per_frame = summary.loc[selected_frames, object_type].reset_index(drop=True).reset_index()
    chart = (
        alt.Chart(objects_per_frame, height=120)
        .mark_area()
        .encode(alt.X("index:Q", scale=alt.Scale(nice=False)), alt.Y("%s:Q" % object_type))
    )
    selected_frame_df = pd.DataFrame({"selected_frame": [selected_frame_index]})
    vline = alt.Chart(selected_frame_df).mark_rule(color="red").encode(x="selected_frame")
    st.altair_chart(alt.layer(chart, vline), use_container_width=True)

    selected_frame = selected_frames[selected_frame_index]
    return selected_frame_index, selected_frame


def render_object_detector_ui():
    confidence_threshold = st.slider("Confidence threshold", 0.0, 1.0, 0.5, 0.01)
    overlap_threshold = st.slider("Overlap threshold", 0.0, 1.0, 0.3, 0.01)
    return confidence_threshold, overlap_threshold
