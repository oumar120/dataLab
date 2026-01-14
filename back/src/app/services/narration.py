from groq import Groq
import json
import os


def _get_groq_client() -> Groq | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

PROMPT_TEMPLATE = """
Tu es un expert en économie et en politiques publiques.
Analyse les données suivantes et rédige une interprétation claire, précise, en 2-3 paragraphes :
il y a 2 types d'analyses possibles en fonction des données fournies :
si tu reconnais que les données concernent une simulation d'impact d'une variation d'un indicateur cible sur d'autres indicateurs dans un pays donné,suis les règles pour la narration de simulation.
si tu reconnais que les données concernent l'évolution d'un indice composite pour un ou plusieurs pays (il y a toujours la variable indice),suis les règles pour la narration de l'indice composite.

[DATA]
1. pour la simulation:
Règles :
- D'abord expliquer l'évolution de l'indicateur cible (1, 3, 5 ans).
- Ensuite les indicateurs impactés dont |corrélation| > 0.3.
- Pour corrélation négative, expliquer pourquoi la réduction est logique.
- Ton neutre,variant et adapté à un rapport universitaire.
IMPORTANT :
- Ne jamais interpréter les corrélations comme des causalités directes.
- Préciser lorsque la relation observée provient de conditions socio-économiques communes.
- Expliquer les résultats dans le cadre de la transition démographique lorsque la fécondité ou la mortalité sont impliquées.
- Le texte doit aider un décideur : mettre en contexte, nuancer, interpréter, pas seulement décrire.
2. pour la narration de l'indice composite:
Règles :
- Expliquer l'évolution de l'indice composite sur la période donnée.
- Identifier les indicateurs clés qui ont le plus contribué à cette évolution.
- Proposer des recommandations politiques basées sur les tendances observées.
- Ton neutre, variant et adapté à un rapport universitaire.
IMPORTANT :
- Ne pas inventer de données ou de tendances non présentes dans les chiffres.
- Fournir des analyses nuancées, en évitant les généralisations hâtives.
- Le texte doit aider un décideur : mettre en contexte, nuancer, interpréter, pas seulement décrire.
- se fonder plus sur l indice composite que sur les indicateurs individuels.
"""

def generate_narration(simulation_result: dict):
    client = _get_groq_client()
    if client is None:
        return (
            "Narration IA indisponible: variable d’environnement GROQ_API_KEY manquante. "
            "Configurez GROQ_API_KEY puis relancez le backend."
        )

    prompt = PROMPT_TEMPLATE.replace("[DATA]", json.dumps(simulation_result, indent=2))

    # Appel du modèle LLaMA 
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Tu es un analyste économique expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=1,   
        stream=False
    )

    # Retourne le texte généré
    return completion.choices[0].message.content
