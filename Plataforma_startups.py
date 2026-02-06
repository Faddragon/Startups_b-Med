
"""
PLATAFORMA DE SUBMISSÃO b-Med
-----------------------------
Aplicação Streamlit para submissão e triagem de startups da saúde.

Autor: b-Med Tech Team
Versão: 2.0 (Clean Code Refactor)
"""

import streamlit as st
import os
from datetime import datetime
from typing import Dict, Any, List

# Local Modules
from settings import ALL_NICHES, GROUPS_DEFINITION, get_cluster_from_niche
from utils import save_uploaded_file, validate_email, save_to_jsonl, save_to_excel_db
from form_logic import render_cluster_questions

# --- SETUP & CONFIG ---
st.set_page_config(
    page_title="Submissão de Startups | b-Med",
    layout="centered",
    page_icon="🚀"
)

def load_css() -> None:
    """Carrega estilos CSS personalizados."""
    css_file = "styles.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def init_session_state() -> None:
    """Inicializa variáveis de estado para persistência."""
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    # Defaults para evitar ValueError em widgets
    if 'niche' not in st.session_state:
        st.session_state.niche = ALL_NICHES[0]

    # Campos de formulário persistentes
    form_keys = [
        'startup_name', 'email', 'product_name', 'cnpj', 'website', 
        'founder_name', 'founder_name2', 'phone', 'description', 'manual_cluster'
    ]
    for k in form_keys:
        if k not in st.session_state:
            st.session_state[k] = ""
            
    if 'start_date' not in st.session_state:
        st.session_state.start_date = datetime.today()

def render_header() -> None:
    """Renderiza o cabeçalho e logo da aplicação."""
    logo_files = ["bmed.png", "bmed slogan.jfif", "bmed_logo.png"]
    
    col1, col2, col_r = st.columns([1, 2, 1])
    with col2:
        logo_found = False
        for logo in logo_files:
            if os.path.exists(logo):
                st.image(logo, use_column_width=True)
                logo_found = True
                break
        if not logo_found:
             st.markdown("<div style='text-align: center; font-size: 3em;'>🚀</div>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center;'>Portal de Submissão de Startups</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Preencha os dados e anexe a documentação técnica para avaliação.</p>", unsafe_allow_html=True)
    st.markdown("---")

def process_step_1() -> None:
    """Renderiza e processa a Etapa 1 (Dados Gerais)."""
    st.subheader("1. Dados e Categorização")
    
    with st.form("step1_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Nome da Startup", key="startup_name")
            st.text_input("Nome da solução/produto", key="product_name")
            st.text_input("CNPJ (Opcional)", key="cnpj")
            st.text_input("Website (Opcional)", key="website")
            st.date_input("Data de Início das operações", key="start_date")
        with col2:
            st.text_input("Nome do Responsável (CEO)", key="founder_name")
            st.text_input("Nome do Responsável (CTO)", key="founder_name2")
            st.text_input("E-mail de Contato", key="email")
            st.text_input("Telefone / WhatsApp", key="phone")

        st.markdown("---")
        st.subheader("2. Categorização")
        st.info("Selecione onde sua solução melhor se encaixa.")
        
        st.selectbox("Qual o nicho da sua solução?", ALL_NICHES, key="niche")
        
        st.markdown("**Se não encontrou seu nicho:**")
        st.selectbox("Selecione o Grupo Macro (caso 'Nicho não listado'):", [""] + list(GROUPS_DEFINITION.keys()), key="manual_cluster")

        st.text_area("Descreva sua solução em poucas palavras (Elevator Pitch):", height=100, key="description")
        
        if st.form_submit_button("Confirmar Dados e Avançar >>", type="primary"):
            validate_step_1()

def validate_step_1() -> None:
    """Valida os dados da Etapa 1 e avança se estiver ok."""
    errors = []
    
    # Validations
    if not st.session_state.startup_name:
        errors.append("Nome da Startup é obrigatório.")
    if not st.session_state.email:
        errors.append("E-mail é obrigatório.")
    elif not validate_email(st.session_state.email):
        errors.append("E-mail com formato inválido.")
    if not st.session_state.niche:
        errors.append("Nicho é obrigatório.")
    
    # Cluster Logic
    final_cluster = None
    if st.session_state.niche == "Nicho não listado":
        if not st.session_state.manual_cluster:
            errors.append("Selecione o Grupo Macro para nicho não listado.")
        else:
            final_cluster = st.session_state.manual_cluster
    else:
        final_cluster = get_cluster_from_niche(st.session_state.niche)
    
    if errors:
        for err in errors:
            st.error(err)
    else:
        st.session_state.target_cluster = final_cluster
        st.session_state.step = 2
        st.rerun()

def process_step_2() -> None:
    """Renderiza e processa a Etapa 2 (Questões Específicas e Uploads)."""
    
    # Review Header
    with st.expander("📝 Revisar Dados Iniciais (Clique para Editar)", expanded=False):
        st.write(f"**Startup:** {st.session_state.startup_name}")
        st.write(f"**Cluster:** {st.session_state.target_cluster}")
        if st.button("✏️ Editar Dados"):
            st.session_state.step = 1
            st.rerun()

    st.info(f"📋 Preenchendo ficha técnica para: **{st.session_state.target_cluster}**")
    
    with st.form("final_submission_form"):
        # Section 3: General Tech
        with st.expander("3. Checklist Técnico & Regulatório (Geral)", expanded=True):
            col_tech1, col_tech2 = st.columns(2)
            with col_tech1:
                anvisa_status = st.selectbox("Status na ANVISA:", 
                    ["Não se aplica", "Em processo", "Aprovado (Com Registro)", "Isento"])
                anvisa_num = st.text_input("Nº Registro ANVISA (se houver):")
            with col_tech2:
                lgpd = st.checkbox("Estamos adequados à LGPD?")
                cloud = st.checkbox("Dados hospedados em Nuvem Segura?", help="AWS, Azure, etc.")
                iso = st.checkbox("Possui Certificação ISO 27001 ou SBIS?")

        # Section 4: Specific Cluster Questions
        specific_data = render_cluster_questions(st.session_state.target_cluster)

        # Section 5: Uploads
        st.markdown("---")
        with st.expander("5. Anexo de Documentos Gerais", expanded=True):
            col_up1, col_up2 = st.columns(2)
            with col_up1:
                doc_deck = st.file_uploader("📂 Pitch Deck / Institucional", type=["pdf", "pptx"])
                doc_manual = st.file_uploader("📂 Manual do Usuário", type=["pdf"])
            with col_up2:
                doc_anvisa = st.file_uploader("📂 Comprovante ANVISA", type=["pdf", "jpg", "png"])
                doc_science = st.file_uploader("📂 Evidência Científica", type=["pdf"])

        st.markdown("---")
        if st.form_submit_button("✅ Enviar Submissão Completa", type="primary"):
            handle_final_submission(
                anvisa_status, anvisa_num, lgpd, cloud, iso,
                specific_data,
                doc_deck, doc_manual, doc_anvisa, doc_science
            )

def handle_final_submission(
    anvisa_status, anvisa_num, lgpd, cloud, iso,
    specific_data,
    doc_deck, doc_manual, doc_anvisa, doc_science
) -> None:
    """Processa a submissão final, salvando arquivos e dados."""
    
    # 1. Prepare Directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    clean_name = st.session_state.startup_name.replace(" ", "_").lower()
    folder_name = f"Submissoes/{clean_name}_{timestamp}"
    
    # 2. Save Global Files
    save_uploaded_file(doc_deck, folder_name)
    save_uploaded_file(doc_manual, folder_name)
    save_uploaded_file(doc_anvisa, folder_name)
    save_uploaded_file(doc_science, folder_name)
    
    # 3. Save Specific File (if any) using key handling
    if 'study_file' in specific_data and specific_data['study_file']:
        save_uploaded_file(specific_data['study_file'], folder_name)
        specific_data['study_file_name'] = specific_data['study_file'].name
        # Remove UploadedFile object before saving to JSON/Excel
        del specific_data['study_file']

    # 4. Compile Final Data Payload
    final_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "startup_name": st.session_state.startup_name,
        "product_name": st.session_state.product_name,
        "niche": st.session_state.niche,
        "cluster_macro": st.session_state.target_cluster,
        "founder_ceo": st.session_state.founder_name,
        "founder_cto": st.session_state.founder_name2,
        "email": st.session_state.email,
        "phone": st.session_state.phone,
        "cnpj": st.session_state.cnpj,
        "website": st.session_state.website,
        "start_date": str(st.session_state.start_date),
        "description": st.session_state.description,
        # Tech General
        "tech_anvisa_status": anvisa_status,
        "tech_anvisa_num": anvisa_num,
        "tech_lgpd": lgpd,
        "tech_cloud": cloud,
        "tech_iso": iso,
        "folder_path": folder_name,
        # Specific Data (merged later for Excel, kept separate for JSON)
        "specific_data": specific_data
    }
    
    # 5. Persist Data
    json_ok = save_to_jsonl(final_data)
    excel_ok = save_to_excel_db(final_data)
    
    if json_ok and excel_ok:
        st.balloons()
        st.success(f"✅ Sucesso! A startup **{st.session_state.startup_name}** foi registrada.")
        st.info(f"📂 Arquivos salvos em: `{folder_name}`")
        if st.button("Nova Submissão"):
            st.session_state.clear()
            st.rerun()

def main() -> None:
    """Função Principal."""
    load_css()
    init_session_state()
    render_header()

    if st.session_state.step == 1:
        process_step_1()
    elif st.session_state.step == 2:
        process_step_2()

if __name__ == "__main__":
    main()