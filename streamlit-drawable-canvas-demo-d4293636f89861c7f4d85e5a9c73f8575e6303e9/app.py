import base64
import json
import os
import re
import time
import uuid
from io import BytesIO
from pathlib import Path
import cv2

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from svgpathtools import parse_path


import SessionState
import sys


def main():
    if 'button_id' not in st.session_state:
        st.session_state['button_id'] = ''
    if 'color_to_label' not in st.session_state:
        st.session_state['color_to_label'] = {}
    PAGES = {
        #"About": about,
        #"Basic example": color_annotation_app,
        #"Get center coords of circles": center_circle_app,
        "Color-based image annotation": color_annotation_app,
        #"Download Base64 encoded PNG": png_export,
        #"Compute the length of drawn arcs": compute_arc_length,
    }
    page = st.sidebar.selectbox("Page:", options=list(PAGES.keys()))
    PAGES[page]()

    # with st.sidebar:
    #     st.markdown("---")
    #     st.markdown(
    #         '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://twitter.com/andfanilo">@andfanilo</a></h6>',
    #         unsafe_allow_html=True,
    #     )
    #     st.markdown(
    #         '<div style="margin: 0.75em 0;"><a href="https://www.buymeacoffee.com/andfanilo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a></div>',
    #         unsafe_allow_html=True,
    #     )

def color_annotation_app():
    folder_path = st.text_input("Path of source folder")
    #if len(folder_path)==0:
       # st.write("Please enter a valid image path")
    mask_folder_path = st.text_input("Path of mask folder")
    if len(folder_path) > 0 :
        sys.path.append(folder_path)
        sys.path.append(mask_folder_path)
        image_paths = []
        image_names = os.listdir(folder_path)
        image_names.remove(".ipynb_checkpoints")
        for i in range(len(image_names)):
            image_paths.append(folder_path + '/' + image_names[i])
        

    
        #image_paths = ["e:/LiTS Dataset/segmented/240201_201208_0000000010_CAM4_NG.bmp", "C:/Users/viplo/Downloads/Video/streamlit-drawable-canvas-demo-d4293636f89861c7f4d85e5a9c73f8575e6303e9\modified_image.jpg"]
        # Check if there's already a selected image index in the session state
        if 'selected_image_index' not in st.session_state:
            st.session_state['selected_image_index'] = 0
        
        # Load the selected image
        selected_image_index = st.session_state['selected_image_index']
        bg_image = Image.open(image_paths[selected_image_index])
        label_color = (
            st.sidebar.color_picker("Annotation color: ", "#EA1010") + "77"
        )  # for alpha from 00 to FF
        label = st.sidebar.text_input("Label", "Default")
        mode = "transform" if st.sidebar.checkbox("Move ROIs", False) else "rect"

        canvas_result = st_canvas(
            fill_color=label_color,
            stroke_width=0,
            background_image=bg_image,
            height=225,
            width=768,
            drawing_mode=mode,
            key="color_annotation_app",
        )

        df = pd.json_normalize(canvas_result.json_data["objects"])
        checkbox_result1 = st.checkbox('OK')
        checkbox_result2 = st.checkbox('NG')
        if checkbox_result1 and not checkbox_result2:
            label = 0
        elif checkbox_result2 and not checkbox_result1:
            label = 1
        elif not checkbox_result2 and not checkbox_result1:
            st.write("Select a label")
        else:
            st.write("Select only one")
        if st.button("Next"):
            st.session_state['selected_image_index'] = (selected_image_index + 1) % len(image_paths)
        if len(df)>0:
            df.to_csv(f"modified_image{selected_image_index}.csv", index=False)
            
        if st.button("Save"):    
            if canvas_result.json_data is not None:
                modified_image = canvas_result.image_data
                df = pd.json_normalize(canvas_result.json_data["objects"])
                if len(df) == 0:
                    return
                st.session_state["color_to_label"][label_color] = label
                cv2.imwrite( mask_folder_path + "/" + image_names[selected_image_index], modified_image)
                    # modified_image.save("modified_image.jpg")  # Save as JPEG or any other desired format
                st.success("Modified image saved successfully.")

                df["label"] = df["fill"].map(st.session_state["color_to_label"])
                st.dataframe(df[["top", "left", "width", "height", "fill", "label"]])

            with st.expander("Color to label mapping"):
                st.json(st.session_state["color_to_label"])
    
    else:
        st.write("Please enter a valid folder path")




if __name__ == "__main__":
    st.set_page_config(
        page_title="Streamlit Drawable Canvas Demo", page_icon=":pencil2:"
    )
    st.title("Pill Image annotation")
    st.sidebar.subheader("Configuration")
    main()
