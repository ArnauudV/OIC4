import streamlit as st
import piexif
from PIL import Image
import urllib.request

st.title("Éditeur de métadonnées EXIF")

# URL de l'image de Dwayne Johnson
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Dwayne_Johnson_2%2C_2013.jpg/1920px-Dwayne_Johnson_2%2C_2013.jpg"

# Charger l'image
with urllib.request.urlopen(image_url) as url:
    img = Image.open(url)

# Afficher l'image
st.image(img, caption="Dwayne Johnson", use_column_width=True)

# Charger les métadonnées EXIF
exif_dict = piexif.load(img.info["exif"])

# Créer un formulaire pour éditer les métadonnées EXIF
with st.form(key="exif_form"):
    st.write("Modifier les métadonnées EXIF")
    for ifd_name in exif_dict:
        if ifd_name == "thumbnail":
            continue
        st.write(ifd_name)
        for tag in exif_dict[ifd_name]:
            tag_value = exif_dict[ifd_name][tag]
            tag_name = piexif.TAGS[ifd_name][tag]["name"]
            new_value = st.text_input(f"{tag_name} ({tag})", tag_value)
            if new_value != tag_value:
                if isinstance(tag_value, bytes):
                    exif_dict[ifd_name][tag] = new_value.encode("utf-8")
                else:
                    try:
                        exif_dict[ifd_name][tag] = type(tag_value)(new_value)
                    except ValueError:
                        st.warning(f"Erreur de conversion pour {tag_name}: la valeur entrée n'est pas valide.")
                    
    submit_button = st.form_submit_button("Enregistrer les modifications")
    if submit_button:
        exif_bytes = piexif.dump(exif_dict)
        img.save("edited_image.jpg", exif=exif_bytes)
        st.write("Les modifications ont été enregistrées.")

