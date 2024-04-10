image_paths = ["img/tennis-balls.jpg", "modified_image.jpg", "modified_image0.jpg"]
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
        stroke_width=3,
        background_image=bg_image,
        height=320,
        width=512,
        drawing_mode=mode,
        key="color_annotation_app",
    )
    if st.button("Next"):
        st.session_state['selected_image_index'] = (selected_image_index + 1) % len(image_paths)
        if len(df)>0:
            df.to_csv(f"modified_image{selected_image_index}.csv", index=False)
        if canvas_result.json_data is not None:
            modified_image = canvas_result.image_data
            df = pd.json_normalize(canvas_result.json_data["objects"])
            #if len(df) == 0:
            #   return
            st.session_state["color_to_label"][label_color] = label
            cv2.imwrite(f"modified_image{selected_image_index}.jpg", modified_image)
                # modified_image.save("modified_image.jpg")  # Save as JPEG or any other desired format
            st.success("Modified image saved successfully.")

            df["label"] = df["fill"].map(st.session_state["color_to_label"])
            st.dataframe(df[["top", "left", "width", "height", "fill", "label"]])

        with st.expander("Color to label mapping"):
            st.json(st.session_state["color_to_label"])
