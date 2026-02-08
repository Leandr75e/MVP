import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import re
import io # Nécessaire pour le téléchargement Excel si on veut être propre


st.set_page_config(page_title="Vermaz Portfolio", layout="wide")

def check_password():
    """Renvoie True si l'utilisateur a le bon mot de passe."""

    def password_entered():
        """Vérifie si le mot de passe saisi correspond au secret."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # On ne garde pas le mdp en mémoire
        else:
            st.session_state["password_correct"] = False

    # 1. Si l'utilisateur est déjà connecté, on retourne True tout de suite
    if st.session_state.get("password_correct", False):
        return True

    # 2. Sinon, on affiche le champ de saisie
    st.text_input(
        "🔐 Mot de passe", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )
    
    # 3. Gestion des erreurs
    if "password_correct" in st.session_state:
        st.error("❌ Mot de passe incorrect")
        
    return False

# Si le mot de passe n'est pas bon, on arrête tout ici !
if not check_password():
    st.stop()

# --- FIN DU VERROUILLAGE ---


# 2. Définition des fonctions (On ne change rien ici)
def clean_currency(x):
    # ... (ton code existant) ...
    if pd.isna(x) or x == "": return 0.0
    if isinstance(x, (int, float)): return float(x)
    s = str(x).strip()
    s_clean = re.sub(r'[^\d,.-]', '', s)
    s_clean = s_clean.replace(',', '.')
    try:
        return float(s_clean)
    except ValueError:
        return 0.0

def calculate_max_drawdown(series):
    # ... (ton code existant) ...
    rolling_max = series.cummax()
    daily_drawdown = (series / rolling_max) - 1.0
    return daily_drawdown.min() * 100

def calculate_monthly_performance(df, col_val):
    # ... (ton code existant) ...
    df_temp = df.copy()
    if 'Date' in df_temp.columns:
        df_temp.set_index('Date', inplace=True)
    monthly_data = df_temp[col_val].resample('ME').last()
    monthly_returns = monthly_data.pct_change()
    perf_df = pd.DataFrame({'Returns': monthly_returns})
    perf_df['Year'] = perf_df.index.year
    perf_df['Month'] = perf_df.index.month
    pivot_table = perf_df.pivot(index='Year', columns='Month', values='Returns')
    months_map = {1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Juin',
                  7: 'Juil', 8: 'Août', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'}
    pivot_table.rename(columns=months_map, inplace=True)
    return pivot_table.sort_index(ascending=False)

@st.cache_data
def load_and_process_data():
    # ... (ton code existant pour charger le Excel) ...
    excel_files = glob.glob("data/*.xlsx")
    if not excel_files:
        return None, None, None, None
    
    file_path = excel_files[0]
    
    # ... (Tout ton bloc de traitement de données ici) ...
    # Je ne remets pas tout le code pour gagner de la place, 
    # mais garde bien tout le contenu de ta fonction load_and_process_data
    
    try:
        df_raw = pd.read_excel(file_path, sheet_name='EXPORT', header=0)
        # ... Tes traitements ...
        # (Copie colle le contenu de ta fonction load_and_process_data ici)
        
        # Pour l'exemple, je simule le retour :
        return df_arb, df_evo, df_expo, df_price 
    except:
        return None, None, None, None

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


df_arb, df_evo, df_expo, df_price = load_and_process_data()


# --- 2. FONCTION DE CONVERSION CSV ---
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


# --- 3. AFFICHAGE DE L'EN-TÊTE ET DU MENU ---
# Maintenant que df_arb existe, les conditions (if df_arb is not None) seront VRAIES

col_title, col_dl = st.columns([6, 1])

with col_title:
    st.title("📊 Tracking Crypto Portfolio")
    st.markdown("Suivi des performances, allocations et arbitrages.")

with col_dl:
    st.write("") 
    st.write("")
    # Le menu déroulant
    with st.popover("📥", use_container_width=True):
        st.markdown("### 📂 Exports disponibles")
        
        # A. Fichier Excel Source
        excel_files = glob.glob("data/*.xlsx")
        if excel_files:
            with open(excel_files[0], "rb") as f:
                st.download_button(
                    label="📄 Excel Source (.xlsx)",
                    data=f,
                    file_name="source_portfolio.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

def clean_currency(x):
    """Transforme n'importe quel format (1 200,50 $) en float (1200.50)"""
    if pd.isna(x) or x == "": return 0.0
    if isinstance(x, (int, float)): return float(x)
    
    s = str(x).strip()
    s_clean = re.sub(r'[^\d,.-]', '', s)
    s_clean = s_clean.replace(',', '.')
    
    try:
        return float(s_clean)
    except ValueError:
        return 0.0



def calculate_max_drawdown(series):
    """Calcule la perte maximale historique (en %) d'une série de prix."""
    rolling_max = series.cummax()
    daily_drawdown = (series / rolling_max) - 1.0
    max_drawdown = daily_drawdown.min() 
    return max_drawdown * 100  

def calculate_monthly_performance(df, col_val):
    """Calcule la performance mensuelle et renvoie un tableau croisé dynamique."""
    df_temp = df.copy()
    # On s'assure que la date est l'index
    if 'Date' in df_temp.columns:
        df_temp.set_index('Date', inplace=True)
    
    # Rééchantillonnage pour prendre la dernière valeur de chaque mois
    monthly_data = df_temp[col_val].resample('ME').last() # 'ME' pour Month End (ou 'M' selon version pandas)
    
    # Calcul du rendement en pourcentage
    monthly_returns = monthly_data.pct_change()
    
    # Création du DataFrame pour le pivot
    perf_df = pd.DataFrame({'Returns': monthly_returns})
    perf_df['Year'] = perf_df.index.year
    perf_df['Month'] = perf_df.index.month
    
    # Pivot (Lignes = Années, Colonnes = Mois)
    pivot_table = perf_df.pivot(index='Year', columns='Month', values='Returns')
    
    # Renommer les colonnes (1 -> Jan, 2 -> Fév...)
    months_map = {1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Juin',
                  7: 'Juil', 8: 'Août', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'}
    pivot_table.rename(columns=months_map, inplace=True)
    
    # On trie les années du plus récent au plus ancien
    pivot_table = pivot_table.sort_index(ascending=False)
    
    return pivot_table

@st.cache_data
@st.cache_data
def load_and_process_data():
    # 1. Trouver le fichier Excel
    excel_files = glob.glob("data/*.xlsx")
    if not excel_files:
        st.error("⚠️ Aucun fichier .xlsx trouvé dans le dossier 'data'.")
        return None, None, None, None
    
    file_path = excel_files[0]
    
    try:
        df_raw = pd.read_excel(file_path, sheet_name='EXPORT', header=0)
    except Exception as e:
        st.error(f"Erreur de lecture du fichier Excel : {e}")
        return None, None, None, None

    # --- 1. ARBITRAGES ---
    df_arb = df_raw.iloc[:, 0:5].copy()
    df_arb.dropna(subset=['DATE'], inplace=True)
    
    # --- 2. EVOLUTION PORTEFEUILLE ---
    df_evo = df_raw.iloc[:, 6:10].copy()
    df_evo.columns = [str(c).strip() for c in df_evo.columns]
    col_date_name = df_evo.columns[0]
    df_evo.dropna(subset=[col_date_name], inplace=True)
    df_evo['Date_Clean'] = pd.to_datetime(df_evo[col_date_name], dayfirst=True, errors='coerce')
    df_evo = df_evo.dropna(subset=['Date_Clean'])
    df_evo = df_evo[df_evo['Date_Clean'] >= pd.Timestamp('2024-01-01')]
    
    cols_vals = df_evo.columns[1:4]
    for col in cols_vals:
        df_evo[col] = df_evo[col].apply(clean_currency)
    
    df_evo = df_evo.groupby('Date_Clean')[cols_vals].last().reset_index()
    df_evo.rename(columns={'Date_Clean': 'Date'}, inplace=True)
    df_evo = df_evo.sort_values('Date') 

    # --- 3. EXPOSITION (CORRECTION ICI) ---
    df_expo = df_raw.iloc[:, 11:32].copy()
    
    # Nettoyage des noms de colonnes
    df_expo.columns = [str(c).strip() for c in df_expo.columns]
    col_date_expo = df_expo.columns[0] # On assume que la 1ere colonne est la Date
    
    # Nettoyage des lignes vides
    df_expo.dropna(subset=[col_date_expo], inplace=True)
    
    # Création de la Date propre
    df_expo['Date_Clean'] = pd.to_datetime(df_expo[col_date_expo], dayfirst=True, errors='coerce')
    df_expo.dropna(subset=['Date_Clean'], inplace=True)
    
    # NETTOYAGE DES VALEURS (CRUCIAL)
    # On prend toutes les colonnes sauf la première (Date originale) et la dernière (Date_Clean qu'on vient de créer)
    cols_to_clean = [c for c in df_expo.columns if c not in [col_date_expo, 'Date_Clean']]
    
    for col in cols_to_clean:
        # On force le nettoyage clean_currency sur chaque cellule
        df_expo[col] = df_expo[col].apply(clean_currency)

    df_expo.sort_values('Date_Clean', inplace=True)
    
    # --- 4. PRIX ---
    df_price = df_raw.iloc[:, 33:].copy()
    
    return df_arb, df_evo, df_expo, df_price

# --- CHARGEMENT ---
df_arb, df_evo, df_expo, df_price = load_and_process_data()

if df_evo is not None and not df_evo.empty:
    
# --- KPI HEADER ---
    # On récupère la première (date la plus ancienne) et la dernière ligne (date la plus récente)
    first_row = df_evo.iloc[0]
    last_row = df_evo.iloc[-1]
    
    col_vermaz = 'Portefeuille avec arbitrage'
    col_hold = 'Portefeuille sans arbitrage'
    col_btc = 'Portefeuille full BTC'
    
    # 1. Récupération des valeurs clés
    # Valeur initiale (Première ligne du fichier)
    val_depart = first_row.get(col_vermaz, 37467) 
    # Si tu préfères fixer le montant exact manuellement, décommente la ligne ci-dessous :
    # val_depart = 37467.0 

    val_actuelle = last_row.get(col_vermaz, 0)
    val_ref = last_row.get(col_hold, 0)
    val_btc = last_row.get(col_btc, 0)
    
    # 2. Calcul des Performances
    # Performance Globale (Actuel vs Départ)
    gain_total = val_actuelle - val_depart
    gain_total_pct = (gain_total / val_depart * 100) if val_depart != 0 else 0

    # Impact Gestion (Actuel vs Hold)
    delta = val_actuelle - val_ref
    delta_pct = (delta / val_ref * 100) if val_ref != 0 else 0
    
    # Performance vs Benchmark (Actuel vs Full BTC)
    delta_btc = val_actuelle - val_btc
    delta_pct_btc = (delta_btc / val_btc * 100) if val_btc != 0 else 0

    # 3. Affichage (On passe à 5 colonnes)
    c_init, c_now, c_impact, c_bench, c_date = st.columns(5)
    
    # J'ajoute le % de gain total à côté de la mise de départ, c'est motivant !
    c_init.metric("Mise de départ", f"{val_depart:,.0f} $")
    
    c_now.metric("Valeur Actuelle", f"{val_actuelle:,.0f} $", f"{gain_total_pct:+.2f} %") # J'ai arrondi à 0 décimale pour la lisibilité
    
    c_impact.metric("Impact Gestion", f"{delta:+,.0f} $", f"{delta_pct:+.2f} %")
    
    c_bench.metric("Vs 100% BTC (Benchmark)", f"{delta_btc:+,.0f} $", f"{delta_pct_btc:+.2f} %")
    
    c_date.metric("Mise à jour", last_row['Date'].strftime('%d/%m/%Y'))
    
    st.divider()  

    # --- SECTION GRAPHIQUE (MODIFIÉE POUR LISSAGE) ---
    st.header("📈 Performance & Comparaison")
    
    df_plot = df_evo[df_evo[col_vermaz] > 100] 
    
    if not df_plot.empty:
        fig = px.line(df_plot, x='Date', y=[col_vermaz, col_hold, col_btc],
                      title="Comparaison des Stratégies",
                      labels={"value": "Valeur ($)", "variable": "Stratégie", "Date": "Date"})
        
        # --- LISSAGE (EXISTANT) ---
        fig.update_traces(line_shape='spline', line_smoothing=0.4) 
        
        # --- AJOUT DU RANGE SELECTOR (NOUVEAU) ---
        fig.update_xaxes(
            rangeslider_visible=True,  # Affiche le petit slider en bas du graphique
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="MAX")
                ]),
                bgcolor="#262730",  # Couleur de fond des boutons (adapté au dark mode Streamlit)
                activecolor="#FF4B4B", # Couleur du bouton actif (Rouge Streamlit)
            )
        )

        # --- MISE EN PAGE ---
        fig.update_layout(
            hovermode="x unified", 
            legend=dict(
                orientation="h", 
                y=1.15,  # Je l'ai remonté un peu pour ne pas gêner les boutons
                title=None
            ),
            xaxis_title=None,
            yaxis_title="Valeur ($)",
            dragmode="zoom", # Permet de sélectionner une zone avec la souris
            title=dict(
                text="Comparaison des Stratégies",
                y=1,          # Position verticale (0 = bas, 1 = haut)
                x=0,             # Aligné à gauche
                xanchor='left',
                yanchor='top'
            ),
            # 2. On augmente la marge du HAUT (t=top) pour pousser le graphique vers le bas
            margin=dict(t=100)   # Augmente cette valeur (ex: 120) si tu veux encore plus d'espace
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Pas assez de données valides pour afficher le graphique.")

    st.divider()       

# --- SUITE DU DASHBOARD (Allocation) ---
    st.header("🍰 Allocation Actuelle")
    
    if df_expo is not None and not df_expo.empty:
        # 1. SÉLECTEUR DE DATE
        dates_dispo = sorted(df_expo['Date_Clean'].dt.date.unique(), reverse=True)
        
        col_sel, col_kpi = st.columns([1, 3])
        with col_sel:
            date_selectionnee = st.selectbox("📅 Date :", options=dates_dispo, index=0)
        
        # 2. PRÉPARATION DES DONNÉES
        mask_date = df_expo['Date_Clean'].dt.date == date_selectionnee
        # On récupère la ligne (Series)
        row_expo = df_expo[mask_date].iloc[0]
        
        data_pie = []
        usdc_val = 0
        total_portfolio_val = 0
        
        # Liste des colonnes à ignorer
        col_date_name = df_expo.columns[0] # La première colonne (souvent 'DATE')
        ignored_cols = ['Date', 'Date_Clean', col_date_name]
        
        cols_actifs = [c for c in df_expo.columns if c not in ignored_cols]

        for col in cols_actifs:
            try:
                val = float(row_expo[col])
            except:
                val = 0.0
                
            asset_name = str(col).replace('$','').strip().upper()
            
            # --- CORRECTION MAJEURE ICI ---
            # On change le filtre > 1 en > 0.0001 (pour garder les % mais virer les 0 absolus)
            # On exclut aussi "TOTAL" pour ne pas fausser le camembert
            if val > 0.0001 and "TOTAL" not in asset_name:
                
                clean_name = asset_name.replace(' VALEUR', '').strip()
                data_pie.append({'Asset': clean_name, 'Value': val})
                total_portfolio_val += val
                
                # Détection Cash
                if "USDC" in asset_name or "USD" in asset_name:
                    usdc_val += val

        # 3. AFFICHAGE
        if not data_pie:
            st.error("Aucune donnée d'allocation valide trouvée (vérifiez les valeurs).")
        else:
            # KPI Cash
            # Si total_portfolio_val ~ 1 (100%), le calcul reste correct
            pct_cash = (usdc_val / total_portfolio_val * 100) if total_portfolio_val > 0 else 0
            
            with col_kpi:
                st.metric(
                    label=f"Exposition Cash (USDC) au {date_selectionnee.strftime('%d/%m/%Y')}",
                    value=f"{pct_cash:.1f} %"
                    # J'ai retiré le paramètre 'delta' en $ car nous n'avons que des % ici
                )

            # GRAPHIQUES
            col_pie_chart, col_details = st.columns([2, 1])
            
            with col_pie_chart:
                df_pie_chart = pd.DataFrame(data_pie)
                fig_pie = px.pie(df_pie_chart, values='Value', names='Asset', hole=0.4)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)
            

            with col_details:
                st.markdown("#### Détails")
                df_summary = df_pie_chart.sort_values('Value', ascending=False)
                # On affiche la valeur brute (qui est un ratio) en pourcentage dans le tableau
                df_summary['Allocation'] = (df_summary['Value'] / total_portfolio_val * 100).map('{:.1f} %'.format)
                st.dataframe(df_summary[['Asset', 'Allocation']], use_container_width=True, hide_index=True)

    else:
        st.info("Données d'allocation non disponibles.")

        # --- AJOUT SECTION RISQUE (NOUVEAU) ---

    st.divider()  

    st.header("🛡️ Analyse du Risque")
    
    # 1. Calculs
    mdd_portfolio = calculate_max_drawdown(df_evo[col_vermaz])
    mdd_btc = calculate_max_drawdown(df_evo[col_btc])
    
    # 2. Affichage
    c_risk1, c_risk2, c_risk3 = st.columns(3)
    
    # Max Drawdown Vermaz
    c_risk1.metric(
        "Max Drawdown (Portfolio)", 
        f"{mdd_portfolio:.2f} %", 
        help="La baisse maximale enregistrée par votre portefeuille depuis un sommet historique."
    )
    
    # Max Drawdown BTC
    c_risk2.metric(
        "Max Drawdown (Bitcoin)", 
        f"{mdd_btc:.2f} %",
        help="La baisse maximale du Bitcoin sur la même période."
    )
    
    # Comparaison (Êtes-vous plus safe que le marché ?)
    risk_diff = mdd_portfolio - mdd_btc 
    # Si Vermaz = -10% et BTC = -30%, risk_diff = +20% (C'est bon, donc vert)
    
    c_risk3.metric(
        "Protection vs BTC", 
        f"{risk_diff:+.2f} pts", 
        help="Une valeur positive signifie que votre chute maximale a été moins violente que celle du Bitcoin."
    )

    st.expander("📉 Voir le détail des zones de baisse (Underwater Plot)")
                # On recalcule les drawdowns quotidiens pour le graphique
    df_plot['DD_Portfolio'] = (df_plot[col_vermaz] / df_plot[col_vermaz].cummax() - 1) * 100
    df_plot['DD_BTC'] = (df_plot[col_btc] / df_plot[col_btc].cummax() - 1) * 100        
    fig_dd = px.area(df_plot, x='Date', y=['DD_Portfolio', 'DD_BTC'],
                        title="Profondeur des baisses (Drawdown)",
                        labels={"value": "Perte depuis le sommet (%)", "variable": "Actif"},
                        color_discrete_map={'DD_Portfolio': '#00CC96', 'DD_BTC': '#EF553B'}) # Vert pour vous, Rouge pour BTC
                
    fig_dd.update_yaxes(ticksuffix="%")
    fig_dd.update_layout(hovermode="x unified", showlegend=True, yaxis_title="% Drawdown")
                
    st.plotly_chart(fig_dd, use_container_width=True)
    
    st.divider()

    st.header("📅 Performance Mensuelle")
    
    # 1. Calcul des 3 tableaux
    monthly_df_vermaz = calculate_monthly_performance(df_evo, col_vermaz)
    monthly_df_hold = calculate_monthly_performance(df_evo, col_hold) 
    monthly_df_btc = calculate_monthly_performance(df_evo, col_btc)
    
    # 2. Création des 3 onglets
    # J'ai ajouté l'onglet du milieu "🐢 Sans Arbitrage"
    tab_portfolio, tab_hold, tab_btc = st.tabs(["🚀 - Portefeuille", "🐢 - Sans Gestion", "₿ - 100% Bitcoin"])
    
    # --- Onglet 1 : Ton Portefeuille ---
    with tab_portfolio:
        st.markdown("##### Historique avec Arbitrages")
        st.dataframe(
            monthly_df_vermaz.style
            .background_gradient(cmap='RdYlGn', axis=None, vmin=-0.15, vmax=0.15)
            .format("{:+.1%}", na_rep="-")
            .highlight_null(color='transparent'),
            use_container_width=True
        )

    # --- Onglet 2 : Sans Arbitrage (HODL) ---
    with tab_hold:
        st.markdown("##### Historique Passif (Hold)")
        st.dataframe(
            monthly_df_hold.style
            .background_gradient(cmap='RdYlGn', axis=None, vmin=-0.15, vmax=0.15)
            .format("{:+.1%}", na_rep="-")
            .highlight_null(color='transparent'),
            use_container_width=True
        )
    
    # --- Onglet 3 : Bitcoin ---
    with tab_btc:
        st.markdown("##### Historique du Bitcoin")
        st.dataframe(
            monthly_df_btc.style
            .background_gradient(cmap='RdYlGn', axis=None, vmin=-0.15, vmax=0.15)
            .format("{:+.1%}", na_rep="-")
            .highlight_null(color='transparent'),
            use_container_width=True
        )
    
    st.caption("Performances nettes calculées en fin de mois.")
    
    st.divider()

    st.header("⚡ Historique des Arbitrages")

    # 1. Initialisation de la mémoire
    if 'nb_lignes' not in st.session_state:
        st.session_state.nb_lignes = 10

    # 2. Préparation des données (MODIFIÉ)
    # On inverse l'ordre pour avoir les récents en premier
    df_arb_sorted = df_arb.iloc[::-1].copy() 
    
    # --- LA MODIFICATION EST ICI ---
    # On s'assure que la colonne est bien comprise comme une date
    col_date_arb = df_arb_sorted.columns[0] # On suppose que la date est en 1ère colonne
    df_arb_sorted[col_date_arb] = pd.to_datetime(df_arb_sorted[col_date_arb])
    
    # On force le formatage en Jour/Mois/Année (String)
    df_arb_sorted[col_date_arb] = df_arb_sorted[col_date_arb].dt.strftime('%d/%m/%Y')
    # -------------------------------

    # 3. Affichage du tableau
    st.dataframe(
        df_arb_sorted.head(st.session_state.nb_lignes), 
        use_container_width=True, 
        hide_index=True
    )

    # 4. Bouton "Voir plus"
    col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 2, 1])
    
    with col_btn_2:
        if st.session_state.nb_lignes < len(df_arb):
            if st.button("➕ Charger les 10 suivants", use_container_width=True):
                st.session_state.nb_lignes += 10
                st.rerun()
        else:
            st.info("Tout l'historique est affiché.")