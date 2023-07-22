import streamlit as st
import piexif
from PIL import Image
from geopy.geocoders import Nominatim
import fractions

def handle_image(image_path):
    image = Image.open(image_path)
    exif_data = piexif.load(image.info['exif'])

    return exif_data

def degToDmsRational(degFloat):
    minFloat = degFloat % 1 * 60
    secFloat = minFloat % 1 * 60
    deg = fractions.Fraction(round(degFloat), 1)
    min = fractions.Fraction(round(minFloat), 1)
    sec = fractions.Fraction(round(secFloat * 10000), 10000)

    return ((deg.numerator, deg.denominator), (min.numerator, min.denominator), (sec.numerator, sec.denominator))

def handle_form(exif_dict):
    st.subheader('Modifier les métadonnées EXIF')
    with st.form(key='exif_form'):
        new_author = st.text_input(label='Nouveau auteur', value=exif_dict['0th'].get(piexif.ImageIFD.Artist, b'').decode())
        new_location = st.text_input(label='Nouvelle localisation')
        new_datetime = st.text_input(label='Nouvelle date et heure (format: "YYYY:MM:DD HH:MM:SS")', value=exif_dict['Exif'].get(piexif.ExifIFD.DateTimeOriginal, b'').decode())
        submit_button = st.form_submit_button(label='Appliquer les modifications')

    if submit_button:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(new_location)
        st.map([{"lat": location.latitude, "lon": location.longitude}]) # Map displaying

        exif_dict['0th'][piexif.ImageIFD.Artist] = new_author.encode()
        exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = degToDmsRational(location.latitude)
        exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = degToDmsRational(location.longitude)
        
        if new_datetime:  # Add the new datetime only if provided by the user
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_datetime.encode()

    return exif_dict


def main():
    st.title("Modificateur de métadonnées EXIF")

    uploaded_file = st.file_uploader("Choisissez une image", type=['jpg', 'jpeg'])
    if uploaded_file is not None:
        with open("temp.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())
        exif_dict = handle_image("temp.jpg")
        modified_exif_dict = handle_form(exif_dict)

        if modified_exif_dict:
            exif_bytes = piexif.dump(modified_exif_dict)
            im = Image.open('temp.jpg')
            im.save('output.jpg', exif=exif_bytes)

        st.image('output.jpg')

if __name__ == "__main__":
    main()

