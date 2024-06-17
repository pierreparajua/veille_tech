import requests
from urllib.parse import quote
import streamlit as st
from datetime import datetime
from lxml import html

# Fonction pour récupérer les données de Feedly
def get_feedly_data():
    stream_id = quote("enterprise/ponchon/tag/602676c2-887d-41dc-83ff-cee4659666b5")
    access_token = "fe_F1Mpgz9oH4oH2at6UYrear2PzAKFQVV09vSGGYD2"
    headers = {
        "Authorization": f"OAuth {access_token}"
    }
    url = f"https://cloud.feedly.com/v3/streams/contents?streamId={stream_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to retrieve data: {response.status_code}")
        st.error(response.text)
        return None

# Fonction pour extraire le texte d'un contenu HTML en utilisant lxml
def extract_text_from_html(html_content):
    if html_content.strip():  # Vérifiez que le contenu n'est pas vide
        tree = html.fromstring(html_content)
        return tree.text_content()
    return ""

# Fonction principale pour afficher les données avec Streamlit
def main():
    st.set_page_config(page_title="Feedly Board Data", page_icon="📈", initial_sidebar_state="expanded")

    # Appliquer le style CSS personnalisé
    st.markdown(
        """
        <style>
        .article-separator {
            border-bottom: 2px solid white;
            margin: 20px 0;
        }
        .centered-title {
            text-align: center;
            font-size: 2em;
            font-weight: bold;
        }
        .section-title {
            font-size: 1.5em;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="centered-title">Feedly Board Data</div>', unsafe_allow_html=True)
    
    # Ajout d'une barre de recherche
    search_query = st.text_input("Rechercher un titre d'article:")

    # Bouton d'actualisation
    if st.button("Actualiser les données"):
        data = get_feedly_data()
        st.session_state['data'] = data
    else:
        data = st.session_state.get('data', get_feedly_data())
        st.session_state['data'] = data
    
    if data:
        # Récupérer toutes les sources disponibles
        sources = list(set(entry['origin']['title'] for entry in data.get('items', [])))
        
        # Créer une case à cocher pour chaque source
        selected_sources = []
        st.markdown('<div class="section-title">Sélectionner des sources :</div>', unsafe_allow_html=True)
        for source in sources:
            if st.checkbox(source, key=source):
                selected_sources.append(source)
        
        st.markdown('<div class="section-title">Données du board récupérées :</div>', unsafe_allow_html=True)
        for entry in data.get('items', []):
            title = entry['title']
            source = entry['origin']['title']
            if search_query.lower() in title.lower() and (not selected_sources or source in selected_sources):
                st.subheader(title)
                st.write(f"Source: {source}")
                # Afficher la date de publication si elle est disponible
                if 'published' in entry:
                    published_date = datetime.fromtimestamp(entry['published'] / 1000)
                    st.write(f"Date: {published_date.strftime('%Y-%m-%d %H:%M:%S')}")
                # Récupérer le lien de l'article
                if 'alternate' in entry and entry['alternate']:
                    article_url = entry['alternate'][0]['href']
                    st.write(f"[Lien vers l'article]({article_url})")
                # Afficher l'image si disponible
                if 'visual' in entry:
                    st.image(entry['visual']['url'], use_column_width=True)
                # Afficher le résumé de l'article sans les balises HTML
                summary_html = entry.get('summary', {}).get('content', '')
                summary_text = extract_text_from_html(summary_html)
                st.write(summary_text)
                st.markdown('<div class="article-separator"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
