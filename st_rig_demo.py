
# Standard library imports
import os
import json

# Third party imports
import streamlit as st
from PIL import Image, ImageDraw



st.set_page_config(
    page_title="Vangeles - Rig Demo Pipeline",
    page_icon="⚒",  # 💵🔨⚒🛠⛏🔬⚙️🪙✢✣✤✥♚♛🇹🇼🛡
    layout="wide"    # Set the layout to wide mode
)

def convert_label_to_boxes(label):
    boxes = []
    x, y = 0,0 # label['x'], label['y']
    w, h = label['w'], label['h']
    col_num = label['col_num']
    row_num = label['row_num'] 
    gap_x = label['gap_x']
    gap_y = label['gap_y']

    coordinate_list = []
    
    for i in range(row_num + 1):
        for j in range(col_num + 1):
            xmin = x + j * (w + gap_x)
            xmax = xmin + w
            ymin = y + i * (h + gap_y)
            ymax = ymin + h
            boxes.append([xmin, xmax, ymin, ymax, i, j])
            coordinate_list.append((j,i))
        
    return boxes, coordinate_list

def convert_label_to_whole_image_crop(label):
    x, y = label['x'], label['y']
    w, h = label['w'], label['h']
    col_num = label['col_num']
    row_num = label['row_num'] 
    gap_x = label['gap_x']
    gap_y = label['gap_y']
    
    xmin = x 
    xmax = x + (w+gap_x) *col_num
    ymin = y 
    ymax = y + (h+gap_y) *row_num
    return (xmin,ymin, xmax, ymax)


# Initialize sidebar in expanded state
st.sidebar.markdown("## Control Panel")
mode = st.sidebar.selectbox("Select mode", ["web", "local"])
st.sidebar.markdown("---")

if mode == "web":
    # File uploader for JSON configuration
    # st.sidebar.markdown("### Upload Configuration")
    json_file = st.sidebar.file_uploader("1. Upload JSON configuration file", type=['json'])

    if json_file is not None:
        # Load JSON data
        data = json.load(json_file)
        
        # Convert label to crop coordinates and boxes
        crop_label_whole = convert_label_to_whole_image_crop(data)
        crop_label_list, coordinate_list = convert_label_to_boxes(data)
        
        # Image uploader
        # st.sidebar.markdown("### Upload Image") 
        image_file = st.sidebar.file_uploader("2. Upload image file", type=['png', 'jpg', 'jpeg'])
        
        if image_file is not None:
            # Load and display the image
            img = Image.open(image_file)

            crop_label_whole = convert_label_to_whole_image_crop(data)
            crop_label_list, coordinate_list = convert_label_to_boxes(data)
            
            cropped_img = img.crop(crop_label_whole)
            cropped_label_list = crop_label_list   
            coordinate_list = coordinate_list


            cols = st.columns([1,1])
            selected_coordinate_list = cols[0].multiselect("Select coordinates", coordinate_list)
            cols[1].markdown(f"### {image_file.name}")

            for box in cropped_label_list:
                # (box[0], box[2]), (box[1], box[3]) = (xmin,ymin), (xmax,ymax)
                coordinate = (box[0], box[2], box[1], box[3])
                row, col = box[4], box[5]

                draw_combined_img_copy = ImageDraw.Draw(cropped_img)
                    
                if (col, row) in selected_coordinate_list:
                    # 
                    draw_combined_img_copy.rectangle(coordinate, outline="red", width=5)
                else:
                    draw_combined_img_copy.rectangle(coordinate, outline="green", width=5)

            st.image(cropped_img, use_column_width=True)
            





else:

    # Read left and right json files from rig_demo folders
    left_json_path = "rig_demo/left"
    right_json_path = "rig_demo/right"

    # Get list of json files
    left_jsons = [f for f in os.listdir(left_json_path) if f.endswith('.json')]
    right_jsons = [f for f in os.listdir(right_json_path) if f.endswith('.json')]

    if left_jsons:
        for json_file in left_jsons:
            with open(os.path.join(left_json_path, json_file), 'r') as f:
                left_data = json.load(f)
                
    if right_jsons:
        for json_file in right_jsons:
            with open(os.path.join(right_json_path, json_file), 'r') as f:
                right_data = json.load(f)
                
    if not left_jsons and not right_jsons:
        st.sidebar.warning("No JSON files found in rig_demo folders")

    left_crop_label_whole = convert_label_to_whole_image_crop(left_data)
    right_crop_label_whole = convert_label_to_whole_image_crop(right_data)

    left_crop_label_list, left_coordinate_list = convert_label_to_boxes(left_data)
    right_crop_label_list, right_coordinate_list = convert_label_to_boxes(right_data) 

    # Move controls to sidebar
    side = st.sidebar.selectbox("Select side", ["left", "right"])
    folder_path = f"rig_demo/{side}"


    # Get list of image files in selected folder and sort by name
    image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

    if not image_files:
        st.sidebar.warning(f"No image files found in {folder_path}")
    else:
        # Let user select an image file
        selected_image = st.sidebar.selectbox("Select image", image_files)
        
        # Load the selected image
        img = Image.open(os.path.join(folder_path, selected_image))






    if side == "left":
        cropped_img = img.crop(left_crop_label_whole)
        cropped_label_list = left_crop_label_list   
        coordinate_list = left_coordinate_list
    elif side == "right":
        cropped_img = img.crop(right_crop_label_whole)
        cropped_label_list = right_crop_label_list
        coordinate_list = right_coordinate_list


    selected_coordinate_list = st.sidebar.multiselect("Select coordinates", coordinate_list)

    for box in cropped_label_list:
        # (box[0], box[2]), (box[1], box[3]) = (xmin,ymin), (xmax,ymax)
        coordinate = (box[0], box[2], box[1], box[3])
        row, col = box[4], box[5]

        draw_combined_img_copy = ImageDraw.Draw(cropped_img)
            
        if (col, row) in selected_coordinate_list:
            # 
            draw_combined_img_copy.rectangle(coordinate, outline="red", width=5)
        else:
            draw_combined_img_copy.rectangle(coordinate, outline="green", width=5)

    # Create save button
    if st.sidebar.button("Save Image"):
        # Create result directory if it doesn't exist
        result_dir = f"rig_demo/result/{side}"
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        
        # Save image
        save_path = os.path.join(result_dir, selected_image)
        cropped_img.save(save_path)
        st.success(f"Image saved to {save_path}")

    st.image(cropped_img, use_column_width=True)


