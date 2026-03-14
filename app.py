import streamlit as st
import replicate
import os
import tempfile
from PIL import Image

st.set_page_config(page_title="RenderVerse AI", layout="wide")

# Sidebar
st.sidebar.title("RenderVerse AI")

REPLICATE_API_TOKEN = st.sidebar.text_input(
    "Masukkan Replicate API Token",
    type="password"
)

if REPLICATE_API_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

mode = st.sidebar.selectbox(
    "Mode",
    ["Architecture", "Interior Design", "Landscape Design"]
)

suasana = st.sidebar.selectbox(
    "Lighting",
    [
        "Golden hour sunlight",
        "High noon harsh light",
        "Blue hour twilight",
        "Overcast moody sky",
        "Night time with artificial lights"
    ]
)

lensa = st.sidebar.slider("Focal Length", 14, 85, 35)

material = st.sidebar.selectbox(
    "Material",
    [
        "Raw exposed concrete",
        "Smooth white stucco",
        "Aluminum Composite Panel",
        "Corten steel",
        "Natural walnut wood"
    ]
)

view = st.sidebar.selectbox(
    "Camera View",
    [
        "Eye level",
        "Bird eye drone shot",
        "Low angle",
        "Macro detail"
    ]
)

environment = st.sidebar.selectbox(
    "Environment",
    [
        "Metropolitan city",
        "Tropical forest",
        "Coastal beach",
        "Suburban neighborhood"
    ]
)

st.header("RenderVerse AI Workspace")

uploaded_file = st.file_uploader(
    "Upload Screenshot SketchUp",
    type=["png", "jpg", "jpeg"]
)

col1, col2 = st.columns(2)

if uploaded_file:

    image = Image.open(uploaded_file)

    with col1:
        st.subheader("SketchUp Image")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("AI Photorealistic Render")

        if st.button("GENERATE RENDER"):

            if not REPLICATE_API_TOKEN:
                st.error("Masukkan Replicate API Token terlebih dahulu")
            else:

                with st.spinner("Generating AI render..."):

                    try:

                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                            image.save(tmp.name)
                            path = tmp.name

                        prompt = f"""
                        Photorealistic {mode} render,
                        {suasana},
                        building with {material},
                        {view},
                        environment {environment},
                        shot with {lensa}mm lens,
                        ultra realistic,
                        architectural photography,
                        8k
                        """

                        output = replicate.run(
                            "black-forest-labs/flux-pro",
                            input={
                                "prompt": prompt,
                                "image": open(path, "rb"),
                                "strength": 0.8
                            }
                        )

                        st.image(output, use_container_width=True)

                        os.remove(path)

                        st.success("Render selesai!")

                    except Exception as e:
                        st.error(f"Error: {e}")

else:
    st.info("Upload screenshot SketchUp untuk memulai render.")
