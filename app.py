import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import time

from modules.database import initialize_database, get_all_active_records, get_admin_audit_logs
from modules.NLP_engine import resolve_identity_by_name
from modules.GIS_engine import convert_dataframe_to_geodataframe, build_interactive_satellite_map
from modules.security import log_system_event
from modules.valuation_engine import forecast_property_valuation, get_live_world_bank_commodity_index

initialize_database()

st.set_page_config(page_title="AI Cadastral Multi-City Suite", layout="wide")

st.sidebar.title("🔐 Access Control Protocol")
mock_user = st.sidebar.text_input("Operator Identifier Code:", value="REV_STATE_AI_AUDITOR")
mock_role = st.sidebar.selectbox("Access Privilege Clearance Tier:", ["Standard Operator", "System Auditor / Admin"])

st.sidebar.markdown("---")
st.sidebar.title("🤖 Machine Learning Controls")
ai_threshold = st.sidebar.slider("🎯 AI Phonetic Match Threshold Sensitivity", min_value=30, max_value=100, value=55, step=5)

st.title("🗺️ AI Cadastral Multi-City Suite ")
st.caption("State-Wide Cross-District Real Estate Asset Aggregator Powered by Machine Learning Identity, Spatial Clustering, and Predictive Regression Modeling")

tab_engine, tab_logs = st.tabs(["🎯 Intelligent Property Engine", "📜 Governance Audit Logs"])

with tab_engine:
    name_input = st.text_input("Search Global Odisha Land Register by Name:", placeholder="Type name (e.g. Mohapatra)...")

    if name_input:
        active_dataset = get_all_active_records()
        matched_active = resolve_identity_by_name(name_input, active_dataset, threshold=ai_threshold)
        
        if not matched_active.empty:
            discovered_plots = matched_active['plot_no'].tolist()
            
            # --- MEASURE REST API LATENCY TELEMETRY ---
            start_time = time.perf_counter()
            # Explicit call to measure the live World Bank API connection speed
            _ = get_live_world_bank_commodity_index()
            end_time = time.perf_counter()
            
            computed_latency_ms = round((end_time - start_time) * 1000, 2)
            
            # AUTOMATED LOG EVENT: Pass measured latency values into the security system module
            log_system_event(
                user_id=mock_user,
                user_role=mock_role,
                action_type="AI_REGRESSION_SEARCH",
                search_string=name_input,
                accessed_plots_list=discovered_plots,
                api_latency_ms=computed_latency_ms
            )
            
            total_properties = len(matched_active)
            total_acreage = matched_active['area_acres'].sum()
            avg_ai_score = matched_active['ai_confidence_score'].mean()
            
            st.success(f"✔️ AI Engine Executed. Resolved {total_properties} assets. API Gateway Latency: {computed_latency_ms} ms.")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Aggregated State Holdings", f"{total_properties} Plots")
            c2.metric("Cumulative State Acreage", f"{total_acreage:.2f} Acres")
            c3.metric("AI Name Match Average Accuracy", f"{avg_ai_score:.1f}%")
            
            fused_spatial = convert_dataframe_to_geodataframe(matched_active)
            
            st.subheader("📋 AI-Resolved Land Asset Matrix")
            st.dataframe(fused_spatial[['ai_confidence_score', 'district', 'city', 'khatiyan_no', 'tenant_name_en', 'plot_no', 'area_acres']], use_container_width=True)
            
            # REGRESSION ANALYSIS FORECAST CHARTS
            st.subheader("📈 ML Predictive Land Valuation Forecasting (Horizon 2030)")
            target_city = str(matched_active.iloc[0]['city'])
            target_acres = float(matched_active.iloc[0]['area_acres'])
            target_plot_id = str(matched_active.iloc[0]['plot_no'])
            
            valuation_forecast_df = forecast_property_valuation(city=target_city, area_acres=target_acres)
            
            future_2030_val = valuation_forecast_df[valuation_forecast_df['Year'] == 2030]['Estimated_Valuation_INR_Lakhs'].values[0]
            current_2026_val = valuation_forecast_df[valuation_forecast_df['Year'] == 2026]['Estimated_Valuation_INR_Lakhs'].values[0]
            net_appreciation = future_2030_val - current_2026_val
            
            col_chart, col_val_metrics = st.columns(2)
            with col_chart:
                fig_forecast = px.line(
                    valuation_forecast_df, x='Year', y='Estimated_Valuation_INR_Lakhs', color='Data_Category', symbol='Data_Category',
                    title=f"Chronological Value Progression & Horizon Forecast for Plot {target_plot_id} ({target_city})"
                )
                fig_forecast.update_layout(height=320)
                st.plotly_chart(fig_forecast, use_container_width=True)
                
            with col_val_metrics:
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.metric(label="Estimated Value (Current 2026)", value=f"₹ {current_2026_val:.2f} Lakhs")
                st.metric(label="Predicted Forecast Valuation (2030)", value=f"₹ {future_2030_val:.2f} Lakhs")
                st.metric(label="Projected Equity Growth", value=f"₹ {net_appreciation:.2f} Lakhs", delta=f"{(net_appreciation/current_2026_val)*100:.1f}% Appr.")
            
            st.subheader("🌍 State-Wide Geospatial Asset Tracking Map Canvas")
            folium_map_obj = build_interactive_satellite_map(fused_spatial)
            st_folium(folium_map_obj, width=1300, height=500, returned_objects=[])
        else:
            st.error("❌ Identity Match Failure: Strings could not be resolved against system registers.")

with tab_logs:
    st.subheader("🛡️ Administrative Oversight Tracking & Performance Dashboard")
    if mock_role == "System Auditor / Admin":
        st.dataframe(get_admin_audit_logs(), use_container_width=True)
    else:
        st.warning("🔒 Access Denied: Admin role required.")