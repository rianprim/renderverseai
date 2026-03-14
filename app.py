import streamlit as st
import replicate
import os
import tempfile
from PIL import Image

# --- KONFIGURASI API ---
# Masukkan token Replicate Anda di sini, atau lebih aman menggunakan environment variable
REPLICATE_API_TOKEN = st.sidebar.text_input("Masukkan Replicate API Token:", type="password")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

st.set_page_config(page_title="RenderVerse AI", layout="wide")

# --- SISTEM ISOLASI MEMORI ---
# Menjamin tidak ada sisa visual atau prompt dari gambar sebelumnya yang mempengaruhi hasil baru
def clean_memory():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.sidebar.success("Ruang kerja steril. Memori visual dan cache desain sebelumnya telah dihapus total.")

# --- SIDEBAR: KONTROL ---
with st.sidebar:
    st.title("RenderVerse AI")
    
    if st.button("🧹 Clean Memory & New Project", type="primary", use_container_width=True):
        clean_memory()
        
    st.divider()
    mode = st.radio("Pilih Bidang:", ["Architecture", "Interior Design", "Landscape Design"], horizontal=True)
    
    st.subheader("1. Pencahayaan & Atmosfer")
    suasana = st.selectbox("Suasana Waktu:", ["Golden hour sunlight", "High noon harsh light", "Blue hour twilight", "Overcast moody sky", "Night time with artificial lights"])
    
    st.subheader("2. Pengaturan Kamera")
    lensa = st.slider("Focal Length (mm)", 14, 85, 35)
    
    st.subheader("3. Pengaturan Material Utama")
    material_utama = st.selectbox("Pilih Material Fasad/Permukaan:", [
        "Raw exposed concrete with highly detailed rough texture", 
        "Smooth clean white stucco", 
        "Reflective Aluminum Composite Panel (ACP)",
        "Weathered corten steel",
        "Natural matte walnut wood"
    ])
    
    st.subheader("4. Perspektif & Environment")
    view = st.selectbox("Perspektif View:", ["Eye-level perspective", "Bird's eye view, drone shot", "Worm's eye view, low angle", "Close-up macro detail"])
    environment = st.selectbox("Latar Belakang:", ["Metropolitan city background", "Lush tropical forest background", "Coastal beach background", "Quiet suburban neighborhood"])

# --- MAIN CANVAS ---
st.header(f"Workspace: Mode {mode}")

uploaded_file = st.file_uploader("Upload Screenshot SketchUp (JPG/PNG)", type=["jpg", "jpeg", "png"])

col1, col2 = st.columns(2)

if uploaded_file is not None:
    with col1:
        st.subheader("Before: SketchUp Mentah")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
    with col2:
        st.subheader("After: Hasil Photorealism")
        
        if st.button("🚀 GENERATE RENDER", type="primary", use_container_width=True):
            if not REPLICATE_API_TOKEN:
                st.error("Silakan masukkan API Token Replicate Anda di panel kiri terlebih dahulu.")
            else:
                with st.spinner("Membangun geometri dan menyusun material fisik..."):
                    try:
                        # 1. Simpan gambar upload ke file temporary agar bisa dibaca oleh Replicate
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                            image.save(temp_file.name)
                            temp_file_path = temp_file.name
                        
                        # 2. Merakit Dynamic Prompt dari UI
                        # Prompt dirangkai secara segar untuk menghindari kontaminasi dari sesi sebelumnya
                        final_prompt = f"A photorealistic {mode} render, {suasana}, building features {material_utama}, {view}, surrounded by {environment}, shot on {lensa}mm lens DSLR, 8k resolution, ultra-detailed, architectural photography, hyperrealistic"
                        negative_prompt = "cartoon, 3d render, sketch, blurry, bad architecture, deformed, crooked lines, overexposed, distorted proportions, watermark"
                        
                        st.info("Mengirim instruksi ke flux-2-pro AI...")
                        
                        # 3. Memanggil API Replicate (Menggunakan Model Flux Pro)
                        # Parameter 'strength' (0.0 - 1.0) menentukan seberapa besar perubahan dari gambar asli.
                        # Angka 0.8 hingga 0.85 ideal untuk mempertahankan bentuk bangunan namun mengubah total tekstur dan pencahayaan.
                        output = replicate.run(
                            "black-forest-labs/flux-pro", # Gunakan endpoint resmi Flux Pro di Replicate
                            input={
                                "prompt": final_prompt,
                                "image": open(temp_file_path, "rb"), # Mengirim screenshot SketchUp sebagai base image
                                "strength": 0.85, # Semakin rendah angkanya, semakin mirip dengan gambar mentah SketchUp
                                "prompt_upsampling": True,
                                "guidance": 3.0,
                                "output_format": "png",
                                "safety_tolerance": 5
                            }
                        )
                        
                        # 4. Menampilkan Hasil
                        # Berbeda dengan ControlNet yang menghasilkan list (array), endpoint Flux Pro langsung mengembalikan URL gambar hasil akhir.
                        result_image_url = output
                        
                        st.image(result_image_url, use_container_width=True)
                        st.success("Render dengan Flux Pro berhasil diselesaikan!")
                        
                        # Bersihkan file temporary
                        os.remove(temp_file_path)
                        
                    except Exception as e:
                        st.error(f"Terjadi kesalahan pada API: {e}")
else:
    st.info("Silakan upload gambar screenshot dari SketchUp di panel sebelah kiri untuk memulai.")