import streamlit as st
from typing import Dict, Any

def render_cluster_questions(target_cluster: str) -> Dict[str, Any]:
    """
    Renders specific form fields based on the selected Cluster.
    
    Args:
        target_cluster (str): The name of the selected macro cluster.
        
    Returns:
        Dict[str, Any]: A dictionary containing the collected specific data.
    """
    specific_data = {}
    
    st.markdown("### 4. Detalhamento Específico da Solução")
    st.caption(f"Perguntas baseadas no grupo: {target_cluster}")

    # --- CLUSTER A: GESTÃO E FLUXO ---
    if target_cluster == "Ferramentas de Gestão e Fluxo":
        with st.expander("Detalhes: Gestão e Fluxo", expanded=True):
            st.markdown("**Interoperabilidade**")
            specific_data['integration_type'] = st.selectbox(
                "Tipo de Integração:", 
                ["Não tem/CSV", "API Proprietária", "Padrão HL7 FHIR/v2"]
            )
            specific_data['vocabularies'] = st.selectbox(
                "Vocabulários Controlados:", 
                ["Texto Livre", "TUSS/TISS/CID/SNOMED"]
            )
            
            st.markdown("**Usabilidade & Estabilidade**")
            specific_data['click_count'] = st.selectbox(
                "Cliques para tarefa simples (Ex: Prescrição):", 
                ["> 10 cliques", "6-9 cliques", "< 5 cliques"]
            )
            specific_data['rto_rpo'] = st.selectbox(
                "Política de Backup/Recuperação:", 
                ["Backup Diário", "Tempo Real / Failover Automático"]
            )

    # --- CLUSTER B: SUPORTE À DIAGNÓSTICO ---
    elif target_cluster == "Suporte à Diagnóstico e Conduta":
        with st.expander("Detalhes: Suporte à Diagnóstico (Passo a Passo)", expanded=True):
            st.markdown("#### 1. Finalidade do Software (Intended Use)")
            st.info("Para que serve a informação fornecida pelo software?")
            
            specific_data['sd_intended_use'] = st.radio(
                "Finalidade Principal:", 
                [
                    "Tratar ou Diagnosticar (Treat or Diagnose)",
                    "Auxiliar/Direcionar Conduta (Drive Clinical Management)",
                    "Fornecer Informação Clínica (Inform Clinical Management)"
                ], 
                key="sd_use"
            )
            
            st.markdown("#### 2. Criticidade da Situação")
            st.info("Qual o estado de saúde do paciente alvo?")
            specific_data['sd_criticality'] = st.radio(
                "Situação de Saúde:",
                [
                    "Crítica (Risco iminente de morte ou deterioração irreversível)",
                    "Séria (Requer intervenção oportuna, mas não imediata)",
                    "Não Séria (Condição leve ou gestão de bem-estar)"
                ], 
                key="sd_crit"
            )

            st.markdown("#### 3. Regulação e Validação")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                specific_data['validation_type'] = st.selectbox(
                    "Tipo de Validação realizada:", 
                    ["Nenhuma", "Validação Interna (Dados Retrospectivos)", "Validação Prospectiva", "Validação Externa"]
                )
            with col_v2: 
                specific_data['samd_class'] = st.selectbox(
                    "Classe de Risco Estimada (ANVISA/MDR):", 
                    ["Classe I (Baixo)", "Classe II (Médio)", "Classe III (Alto)", "Classe IV (Máximo)"]
                )

    # --- CLUSTER C: TERAPÊUTICAS DIGITAIS ---
    elif target_cluster == "Terapêuticas Digitais e Reabilitação":
        with st.expander("Detalhes: Terapêuticas Digitais", expanded=True):
            # 1. Evidência Clínica
            st.markdown("##### 1. Evidência Clínica")
            clinical_evidence = st.radio(
                "Selecione o nível de evidência disponível:", 
                ["Ensaio Clínico Randomizado (ECR)", "Estudo Pré e Pós utilização", "Estudo Piloto", "Não possuo evidência estruturada"],
                key="td_evidence"
            )
            specific_data['clinical_evidence'] = clinical_evidence

            if clinical_evidence in ["Ensaio Clínico Randomizado (ECR)", "Estudo Pré e Pós utilização"]:
                col_doi, col_file = st.columns(2)
                with col_doi:
                    specific_data['study_doi'] = st.text_input("DOI do Estudo/Artigo (Link ou ID):")
                with col_file:
                    specific_data['study_file'] = st.file_uploader("Ou anexe o PDF do Estudo Completo:", type=['pdf'])
            
            elif clinical_evidence == "Estudo Piloto":
                st.warning("Para Estudo Piloto, é necessário o projeto de pesquisa.")
                specific_data['study_file'] = st.file_uploader("Anexar Projeto Submetido ao CEP/CONEP:", type=['pdf'])
            
            st.markdown("---")
            
            # 2. Responsabilidade Técnica
            st.markdown("##### 2. Responsabilidade Técnica / Conteúdo")
            has_prof = st.checkbox("O conteúdo é assinado/supervisionado por profissional de saúde?", key="td_has_prof")
            
            if has_prof:
                col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
                with col_p1:
                    specific_data['prof_name'] = st.text_input("Nome do Profissional Responsável:")
                with col_p2:
                    specific_data['prof_council_type'] = st.selectbox("Conselho:", ["CRM", "COREN", "CREFITO", "CRP", "CRO", "CRN", "Outros"])
                with col_p3:
                    specific_data['prof_council_num'] = st.text_input("Nº Registro / UF:")
            else:
                specific_data['prof_council'] = "Não aplicável"

            # 3. Engajamento
            st.markdown("##### 3. Modelo de Engajamento")
            specific_data['engagement_process'] = st.text_area("Descreva a estratégia de engajamento do paciente:", height=80)

            # 4. Monetização
            st.markdown("##### 4. Modelo de Negócio")
            specific_data['monetization_process'] = st.text_area("Como é o processo de monetização?", height=80)

            # 5. UX/UI
            st.markdown("##### 5. UX/UI")
            specific_data['last_layout_update'] = st.date_input("Data da última atualização de Interface:")

    return specific_data
