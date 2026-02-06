from typing import List, Dict

# Defines the Clusters and their respective Niches
GROUPS_DEFINITION: Dict[str, List[str]] = {
    "Ferramentas de Gestão e Fluxo": [
        "Prontuário Eletrônico", "Telemedicina", "Gestão de Consultório"
    ],
    "Suporte à Diagnóstico e Conduta": [
        "Dispositivo Médico", "IA Diagnóstica", 
        "Calculadoras Clínicas", "Monitoramento Remoto"
    ],
    "Terapêuticas Digitais e Reabilitação": [
        "Terapeuticas Digitais", "Realidade Virtual", "Mudança de Hábito"
    ]
}

# Flattens the list for the dropdown
ALL_NICHES: List[str] = sorted([n for sublist in GROUPS_DEFINITION.values() for n in sublist])
ALL_NICHES.append("Nicho não listado")

def get_cluster_from_niche(niche_name: str) -> str:
    """Returns the macro cluster for a given niche."""
    for cluster, niches in GROUPS_DEFINITION.items():
        if niche_name in niches:
            return cluster
    return None
