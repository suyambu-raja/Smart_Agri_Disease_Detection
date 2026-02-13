"""
Recommendation Engine – Knowledge Base
========================================
Maps each known crop disease to recommended fertilizers,
pesticides, organic treatments, and preventive measures.

This acts as a rule-based expert system. In production you
could back this with a Firestore collection or a vector DB.
"""

# ──────────────────────────────────────────────────────────────
# DISEASE → RECOMMENDATION MAP
# Keys are the formatted disease names (e.g. "Tomato Early Blight")
# ──────────────────────────────────────────────────────────────

RECOMMENDATIONS = {
    # ── Tomato ──
    'Tomato Early Blight': {
        'fertilizers': [
            'Potassium-rich fertilizer (Muriate of Potash)',
            'Calcium Ammonium Nitrate',
        ],
        'pesticides': [
            'Mancozeb 75% WP – 2.5 g/L',
            'Chlorothalonil 75% WP – 2 g/L',
            'Azoxystrobin 23% SC – 1 ml/L',
        ],
        'organic_treatments': [
            'Neem oil spray (5 ml/L)',
            'Trichoderma viride soil application',
        ],
        'preventive_measures': [
            'Remove infected lower leaves immediately',
            'Practice crop rotation (3-year cycle)',
            'Ensure adequate plant spacing for air circulation',
            'Avoid overhead irrigation',
        ],
    },
    'Tomato Late Blight': {
        'fertilizers': [
            'Phosphorus-containing fertilizer',
            'Micronutrient mixture (Zn, Mn, Fe)',
        ],
        'pesticides': [
            'Metalaxyl + Mancozeb (Ridomil Gold) – 2.5 g/L',
            'Cymoxanil 8% + Mancozeb 64% WP – 3 g/L',
            'Copper Oxychloride 50% WP – 3 g/L',
        ],
        'organic_treatments': [
            'Bordeaux mixture (1%)',
            'Pseudomonas fluorescens spray',
        ],
        'preventive_measures': [
            'Use resistant varieties',
            'Destroy infected plant debris',
            'Avoid planting during heavy monsoon',
            'Provide proper drainage',
        ],
    },
    'Tomato Bacterial Spot': {
        'fertilizers': ['Balanced NPK 19-19-19'],
        'pesticides': [
            'Streptomycin sulphate 100 ppm',
            'Copper Hydroxide 77% WP – 2 g/L',
        ],
        'organic_treatments': [
            'Neem cake application to soil',
        ],
        'preventive_measures': [
            'Use disease-free seeds',
            'Avoid working with wet plants',
            'Hot water seed treatment at 50°C for 25 min',
        ],
    },
    'Tomato Leaf Mold': {
        'fertilizers': ['Calcium-enriched foliar spray'],
        'pesticides': [
            'Mancozeb 75% WP – 2 g/L',
            'Propiconazole 25% EC – 1 ml/L',
        ],
        'organic_treatments': [
            'Sulphur-based fungicide',
        ],
        'preventive_measures': [
            'Improve greenhouse ventilation',
            'Maintain humidity below 85%',
            'Remove lower infected leaves',
        ],
    },
    'Tomato Septoria Leaf Spot': {
        'fertilizers': ['Balanced NPK fertilizer'],
        'pesticides': [
            'Chlorothalonil 75% WP – 2 g/L',
            'Mancozeb 75% WP – 2.5 g/L',
        ],
        'organic_treatments': ['Neem oil spray'],
        'preventive_measures': [
            'Remove infected leaves',
            'Mulch around the base of plants',
            'Avoid overhead watering',
        ],
    },
    'Tomato Spider Mites Two-Spotted Spider Mite': {
        'fertilizers': ['Micronutrient spray (Zn, Fe)'],
        'pesticides': [
            'Dicofol 18.5% EC – 2.5 ml/L',
            'Spiromesifen 240 SC – 0.8 ml/L',
            'Abamectin 1.9% EC – 0.5 ml/L',
        ],
        'organic_treatments': [
            'Neem oil spray (5 ml/L)',
            'Release predatory mites',
        ],
        'preventive_measures': [
            'Maintain field hygiene',
            'Avoid water stress',
            'Regular monitoring of undersides of leaves',
        ],
    },
    'Tomato Target Spot': {
        'fertilizers': ['Balanced NPK with micronutrients'],
        'pesticides': [
            'Azoxystrobin 23% SC – 1 ml/L',
            'Mancozeb 75% WP – 2 g/L',
        ],
        'organic_treatments': ['Trichoderma viride'],
        'preventive_measures': [
            'Crop rotation',
            'Remove infected debris',
        ],
    },
    'Tomato Yellow Leaf Curl Virus': {
        'fertilizers': ['Potassium-rich fertilizer', 'Humic acid foliar spray'],
        'pesticides': [
            'Imidacloprid 17.8% SL – 0.3 ml/L (against whitefly vector)',
            'Thiamethoxam 25% WG – 0.3 g/L',
        ],
        'organic_treatments': [
            'Yellow sticky traps for whiteflies',
            'Neem oil spray',
        ],
        'preventive_measures': [
            'Use virus-resistant varieties',
            'Control whitefly population',
            'Use silver-colored mulch to repel whiteflies',
            'Remove infected plants immediately',
        ],
    },
    'Tomato Mosaic Virus': {
        'fertilizers': ['Balanced micro-nutrient mixture'],
        'pesticides': [
            'No direct chemical control for virus',
            'Control aphid vectors with Imidacloprid 0.3 ml/L',
        ],
        'organic_treatments': ['Milk spray (10%) to inhibit virus spread'],
        'preventive_measures': [
            'Disinfect tools with 10% bleach solution',
            'Wash hands before handling plants',
            'Remove and destroy infected plants',
            'Use resistant varieties',
        ],
    },
    'Tomato Healthy': {
        'fertilizers': ['Continue balanced NPK (10-26-26) at recommended doses'],
        'pesticides': ['No treatment needed — plant is healthy!'],
        'organic_treatments': ['Preventive neem oil spray every 15 days'],
        'preventive_measures': [
            'Continue good agricultural practices',
            'Maintain proper irrigation schedule',
            'Regular field scouting',
        ],
    },

    # ── Potato ──
    'Potato Early Blight': {
        'fertilizers': ['Potash-rich fertilizer', 'Calcium Ammonium Nitrate'],
        'pesticides': [
            'Mancozeb 75% WP – 2.5 g/L',
            'Azoxystrobin 23% SC – 1 ml/L',
        ],
        'organic_treatments': ['Trichoderma soil application', 'Neem oil spray'],
        'preventive_measures': [
            'Use certified disease-free seed tubers',
            'Practise 3-year crop rotation',
        ],
    },
    'Potato Late Blight': {
        'fertilizers': ['Phosphorus-containing fertilizer'],
        'pesticides': [
            'Metalaxyl + Mancozeb – 2.5 g/L',
            'Cymoxanil 8% + Mancozeb 64% – 3 g/L',
        ],
        'organic_treatments': ['Bordeaux mixture (1%)'],
        'preventive_measures': [
            'Destroy volunteer potato plants',
            'Ensure proper drainage',
            'Plant resistant varieties',
        ],
    },
    'Potato Healthy': {
        'fertilizers': ['Continue recommended NPK schedule'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Preventive Trichoderma application'],
        'preventive_measures': ['Continue regular monitoring'],
    },

    # ── Apple ──
    'Apple Apple Scab': {
        'fertilizers': ['Balanced NPK with micro-nutrients'],
        'pesticides': [
            'Mancozeb 75% WP – 3 g/L',
            'Carbendazim 50% WP – 1 g/L',
        ],
        'organic_treatments': ['Bordeaux mixture (1%)'],
        'preventive_measures': ['Remove fallen infected leaves', 'Prune for air circulation'],
    },
    'Apple Black Rot': {
        'fertilizers': ['Calcium-enriched foliar spray'],
        'pesticides': ['Captan 50% WP – 3 g/L', 'Thiophanate-methyl'],
        'organic_treatments': ['Neem oil spray'],
        'preventive_measures': ['Remove mummified fruits', 'Sanitize pruning tools'],
    },
    'Apple Cedar Apple Rust': {
        'fertilizers': ['Balanced micro-nutrients'],
        'pesticides': ['Mancozeb 75% WP – 2.5 g/L', 'Myclobutanil'],
        'organic_treatments': ['Sulphur-based spray'],
        'preventive_measures': ['Remove nearby juniper hosts', 'Plant resistant varieties'],
    },
    'Apple Healthy': {
        'fertilizers': ['Continue regular fertilization'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Preventive neem oil spray'],
        'preventive_measures': ['Annual pruning schedule'],
    },

    # ── Corn (Maize) ──
    'Corn (Maize) Cercospora Leaf Spot Gray Leaf Spot': {
        'fertilizers': ['Nitrogen top-dressing', 'Potash application'],
        'pesticides': ['Propiconazole 25% EC – 1 ml/L', 'Azoxystrobin 23% SC'],
        'organic_treatments': ['Trichoderma seed treatment'],
        'preventive_measures': ['Crop rotation', 'Hybrid resistant varieties'],
    },
    'Corn (Maize) Common Rust': {
        'fertilizers': ['Balanced NPK'],
        'pesticides': ['Mancozeb 75% WP – 2.5 g/L', 'Propiconazole'],
        'organic_treatments': ['Neem oil spray'],
        'preventive_measures': ['Plant resistant hybrids', 'Early sowing'],
    },
    'Corn (Maize) Northern Leaf Blight': {
        'fertilizers': ['Nitrogen and Potassium top-dressing'],
        'pesticides': ['Mancozeb', 'Propiconazole'],
        'organic_treatments': ['Trichoderma viride'],
        'preventive_measures': ['Destroy crop residue', 'Use tolerant varieties'],
    },
    'Corn (Maize) Healthy': {
        'fertilizers': ['Continue standard fertilization'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Bio-fertilizer application'],
        'preventive_measures': ['Maintain adequate plant population'],
    },

    # ── Grape ──
    'Grape Black Rot': {
        'fertilizers': ['Potassium and Calcium foliar spray'],
        'pesticides': ['Mancozeb – 2.5 g/L', 'Myclobutanil'],
        'organic_treatments': ['Bordeaux mixture'],
        'preventive_measures': ['Remove mummified berries', 'Proper canopy management'],
    },
    'Grape Esca (Black Measles)': {
        'fertilizers': ['Micronutrient mixture'],
        'pesticides': ['No effective chemical — manage via cultural practices'],
        'organic_treatments': ['Trichoderma trunk injection'],
        'preventive_measures': ['Avoid large pruning wounds', 'Remove dead wood'],
    },
    'Grape Leaf Blight (Isariopsis Leaf Spot)': {
        'fertilizers': ['Balanced NPK'],
        'pesticides': ['Mancozeb 75% WP – 2.5 g/L'],
        'organic_treatments': ['Neem oil spray'],
        'preventive_measures': ['Improve air circulation', 'Remove infected leaves'],
    },
    'Grape Healthy': {
        'fertilizers': ['Continue regular vine nutrition'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Preventive sulphur spray'],
        'preventive_measures': ['Annual canopy management'],
    },

    # ── Pepper (Bell) ──
    'Pepper, Bell Bacterial Spot': {
        'fertilizers': ['Calcium Nitrate foliar spray'],
        'pesticides': ['Copper Hydroxide 77% WP – 2 g/L', 'Streptomycin 100 ppm'],
        'organic_treatments': ['Neem cake soil application'],
        'preventive_measures': ['Hot water seed treatment', 'Avoid overhead irrigation'],
    },
    'Pepper, Bell Healthy': {
        'fertilizers': ['Balanced NPK 19-19-19'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Preventive neem oil spray'],
        'preventive_measures': ['Continue good practices'],
    },

    # ── Others (healthy) ──
    'Cherry (Including Sour) Powdery Mildew': {
        'fertilizers': ['Balanced NPK'],
        'pesticides': ['Sulphur 80% WP – 3 g/L', 'Hexaconazole 5% SC – 2 ml/L'],
        'organic_treatments': ['Baking soda spray (5 g/L)'],
        'preventive_measures': ['Prune for air circulation', 'Avoid high-nitrogen fertilizers'],
    },
    'Cherry (Including Sour) Healthy': {
        'fertilizers': ['Regular orchard fertilization'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Preventive sulphur spray'],
        'preventive_measures': ['Annual pruning'],
    },
    'Orange Haunglongbing (Citrus Greening)': {
        'fertilizers': ['Micronutrient mixture (Zn, Mn, Fe, Cu)', 'Foliar urea spray'],
        'pesticides': [
            'Imidacloprid 17.8% SL – 0.3 ml/L (for psyllid vector)',
            'Thiamethoxam 25% WG',
        ],
        'organic_treatments': ['Neem oil spray', 'Release natural predators of psyllid'],
        'preventive_measures': [
            'Use certified disease-free nursery stock',
            'Control Asian Citrus Psyllid vector',
            'Remove and destroy infected trees',
        ],
    },
    'Peach Bacterial Spot': {
        'fertilizers': ['Balanced NPK'],
        'pesticides': ['Copper Oxychloride 50% WP – 3 g/L'],
        'organic_treatments': ['Neem oil spray'],
        'preventive_measures': ['Plant resistant varieties', 'Avoid overhead watering'],
    },
    'Peach Healthy': {
        'fertilizers': ['Standard orchard fertilization'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Preventive neem oil'],
        'preventive_measures': ['Regular pruning'],
    },
    'Strawberry Leaf Scorch': {
        'fertilizers': ['Potash-rich fertilizer'],
        'pesticides': ['Mancozeb 75% WP – 2 g/L', 'Captan 50% WP'],
        'organic_treatments': ['Neem oil spray'],
        'preventive_measures': ['Remove infected leaves', 'Avoid overhead irrigation'],
    },
    'Strawberry Healthy': {
        'fertilizers': ['Balanced NPK'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Preventive bio-agent application'],
        'preventive_measures': ['Mulching and proper spacing'],
    },
    'Squash Powdery Mildew': {
        'fertilizers': ['Potash application'],
        'pesticides': ['Sulphur 80% WP – 3 g/L', 'Dinocap 48% EC – 1 ml/L'],
        'organic_treatments': ['Baking soda + neem oil spray'],
        'preventive_measures': ['Plant resistant varieties', 'Adequate spacing'],
    },

    # Healthy catch-alls
    'Blueberry Healthy': {
        'fertilizers': ['Acidic fertilizer (Ammonium Sulphate)'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Mulch with pine needles'],
        'preventive_measures': ['Maintain soil pH 4.5-5.5'],
    },
    'Raspberry Healthy': {
        'fertilizers': ['Balanced NPK'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Compost application'],
        'preventive_measures': ['Regular pruning of old canes'],
    },
    'Soybean Healthy': {
        'fertilizers': ['Rhizobium inoculant + Phosphorus'],
        'pesticides': ['No treatment needed.'],
        'organic_treatments': ['Bio-fertilizer application'],
        'preventive_measures': ['Seed treatment before sowing'],
    },
}


def get_recommendation(disease_name: str) -> dict | None:
    """
    Look up treatment recommendations for a given disease name.

    Args:
        disease_name: The formatted disease name (e.g., "Tomato Early Blight")

    Returns:
        dict with fertilizers, pesticides, organic_treatments, preventive_measures
        or None if the disease is not found.
    """
    # Try exact match first
    if disease_name in RECOMMENDATIONS:
        return RECOMMENDATIONS[disease_name]

    # Try case-insensitive match
    lower_name = disease_name.lower()
    for key, value in RECOMMENDATIONS.items():
        if key.lower() == lower_name:
            return value

    # Try partial/fuzzy match
    for key, value in RECOMMENDATIONS.items():
        if lower_name in key.lower() or key.lower() in lower_name:
            return value

    return None
