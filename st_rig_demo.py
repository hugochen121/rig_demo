
# Standard library imports
import os
import json

# Third party imports
import streamlit as st
from PIL import Image, ImageDraw



st.set_page_config(
    page_title="Vangeles - Rig Demo Pipeline",
    page_icon="⛏",  # 💵🔨⚒🛠⛏🔬⚙️🪙✢✣✤✥♚♛🇹🇼🛡
    layout="wide"   
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
                    draw_combined_img_copy.rectangle(coordinate, outline="red", width=5)
                else:
                    draw_combined_img_copy.rectangle(coordinate, outline="green", width=5)

            st.image(cropped_img, use_container_width=True)
            





else:

    pass
