
import streamlit as st
from PIL import Image
from modules.defect_detection import detect_possible_cracks


def render_site_analysis():
    st.subheader("📷 Construction Site Analysis")

    st.write(
        "Upload a construction-site image to preview it "
        "and perform preliminary edge-based screening."
    )

    uploaded_file = st.file_uploader(
        "Upload construction-site image",
        type=["jpg", "jpeg", "png"],
        key="site_image"
    )

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")

            st.success("Image uploaded successfully!")

            # Display image dimensions
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Image Width", f"{image.width} px")

            with col2:
                st.metric("Image Height", f"{image.height} px")

            st.divider()
            st.subheader("🔍 Preliminary Defect Screening")

            st.write(
                "Compare the original image with the edges detected "
                "by OpenCV. Highlighted edges are not confirmed cracks."
            )

            if st.button("Analyze Image", key="analyze_site"):
                with st.spinner("Processing image..."):
                    results = detect_possible_cracks(image)

                result_image = results["highlighted_image"]
                edge_count = results["edge_count"]
                edge_percentage = results["edge_percentage"]

                # Side-by-side image comparison
                col1, col2 = st.columns(2)

                with col1:
                    st.image(
                        image,
                        caption="Original Construction Image",
                        use_container_width=True
                    )

                with col2:
                    st.image(
                        result_image,
                        caption="Detected Edges",
                        use_container_width=True
                    )

                # Display analysis measurements
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Edge Pixels Detected",
                        f"{edge_count:,}"
                    )

                with col2:
                    st.metric(
                        "Edge Pixel Percentage",
                        f"{edge_percentage}%"
                    )

                st.warning(
                    "This is basic image processing, not a trained AI "
                    "defect detector. Detected edges may include cracks, "
                    "joints, shadows, textures, and other boundaries. "
                    "The edge percentage does not represent the percentage "
                    "of cracks. This result cannot confirm structural "
                    "defects or assess building safety."
                )

        except Exception as error:
            st.error(
                f"Unable to process the image: {error}"
            )
