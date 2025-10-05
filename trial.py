import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="NASA Exoplanets",
    page_icon="🚀",
    layout="wide"
)

# CSS personalizado
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("A World Away: Hunting for Exoplanets with AI")
st.markdown("---")

# Navegación con tabs
tab1, tab2, tab3, tab4 = st.tabs(["Try Model", "Info", "About Us", "Chatbot"])

with tab1:
    st.header("Sobre Nosotros")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("""
        ### ¡Hola! 

        """)
        

        if st.button("Conoce más"):
            st.balloons()
            st.success("¡Gracias por tu interés!")
    
    with col2:
        st.info("**Estadísticas**")
        st.metric("Clientes Satisfechos", "500+", "+50")
        st.metric("Proyectos Completados", "1,200", "+120")
        st.metric("Años de Experiencia", "10", "+1")

with tab2:
    st.header("Info ")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("""
        ### Exoplanets
        
        Exoplanets are planets that orbit stars outside our Solar System. Since the first confirmed discovery in 1995, astronomers have identified more than 6,000 confirmed exoplanets across over 4,600 planetary systems, with thousands more still awaiting confirmation (NASA, 2024). These discoveries have completely changed our understanding of how planetary systems form and what types of worlds might exist beyond Earth.

        NASA’s Exoplanets portal provides a general introduction to these distant worlds. It explains how scientists detect them, mainly through the transit method (measuring dips in a star’s brightness when a planet passes in front) and radial velocity (detecting wobbles in a star’s motion caused by a planet’s gravity) (NASA, 2024). The site also discusses the idea of the habitable zone, the region around a star where temperatures might allow liquid water to exist, making life possible as we know it (NASA, 2024).

        """)
        
        st.image("https://images.unsplash.com/photo-1707653056980-19175eb85e18?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTZ8fGV4b3BsYW5ldCUyMGtlcGxlcnxlbnwwfHwwfHx8MA%3D%3D", caption="Artistic representation of an exoplanet in deep space. Retrieved from https://unsplash.com/photos/[photo-id]. Copyright free image from Unsplash.", use_container_width=True)

        st.write("""

        The NASA Exoplanet Archive, managed by Caltech’s IPAC, serves as the official scientific database for exoplanet discoveries. It collects verified data from published studies and major space missions such as Kepler, TESS, and CoRoT (NASA Exoplanet Archive, 2024). Researchers can explore information about each planet’s size, orbit, host star, and discovery method. The archive also stores millions of light curves (graphs showing how stars’ brightness changes over time) which help astronomers confirm planetary transits (NASA Exoplanet Archive, 2024).

        For a more immersive experience, NASA offers Eyes on Exoplanets, a 3D interactive visualization tool. It allows anyone to explore thousands of known exoplanets and their host stars in real time. Users can fly through the galaxy, zoom into specific systems like TRAPPIST-1 (which has seven Earth-sized planets) or even visualize what alien skies might look like from their surfaces (NASA Eyes on Exoplanets, 2024).
        """)
        
        st.image("https://images.unsplash.com/photo-1712509846751-cd6082dcfff1?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8N3x8ZXhvcGxhbmV0JTIwa2VwbGVyfGVufDB8fDB8fHww", caption="Visualization of Kepler exoplanet discovery. Retrieved from https://unsplash.com/photos/[photo-id]. Copyright free image from Unsplash.", use_container_width=True)

        st.write("""
        Exoplanets come in a vast variety of types, including small rocky worlds like Earth, massive gas giants like Jupiter, and even exotic lava worlds or low-density planets that could float in water (NASA, 2024a). Some planets orbit two stars at once, while others (called rogue planets) wander through space without a star at all. The diversity is astonishing: about 30% of known exoplanets are gas giants, 35% are super-Earths, and the rest are a mix of mini-Neptunes and terrestrial planets (NASA Exoplanet Archive, 2024).

        Through these tools and databases, NASA continues to expand humanity’s view of the universe. With future missions like the James Webb Space Telescope and the upcoming Habitable Worlds Observatory, scientists aim not only to discover new exoplanets but also to study their atmospheres in search of signs of life (NASA, 2024a).
        """)

        st.image("https://cdn.pixabay.com/photo/2023/03/14/11/19/exoplanet-7852095_1280.jpg", caption="Digital illustration of an exoplanet system. Retrieved from https://pixabay.com/photos/exoplanet-7852095/. Copyright free image from Pixabay.", use_container_width=True)

        st.write("""
        ### References         
        
        NASA. (2024). *Exoplanets*. NASA Science. [https://science.nasa.gov/exoplanets/](https://science.nasa.gov/exoplanets/)

        NASA Exoplanet Archive. (2024). *NASA Exoplanet Archive*. California Institute of Technology (IPAC). [https://exoplanetarchive.ipac.caltech.edu/](https://exoplanetarchive.ipac.caltech.edu/)

        NASA Eyes on Exoplanets. (2024). *Eyes on Exoplanets*. NASA Jet Propulsion Laboratory. [https://eyes.nasa.gov/apps/exo/](https://eyes.nasa.gov/apps/exo/)      
        """)

    
    with col2:
        st.info("**Estadísticas**")
        st.metric("Exoplanetas Confirmados", "6,000+", "+200 (último año) (NASA, 2024)")
        st.metric("Sistemas Planetarios Descubiertos", "4,600+", "+180 (último año) (NASA Exoplanet Archive, 2024)")
        st.metric("Misiones Activas de Búsqueda", "3 (Kepler, TESS, JWST)", "+1 (nueva misión observacional) (NASA Eyes on Exoplanets, 2024)")

with tab3:
    st.header("About Us")
    
    st.subheader("Proyectos Destacados")

with tab4:
    st.header("Chatbot")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>© 2025 Mi Sitio Web. Todos los derechos reservados.</p>
        <p>Hecho usando Streamlit</p>
    </div>
    """, unsafe_allow_html=True)