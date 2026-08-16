@echo off
python scripts/fetch_fpl_data.py
python scripts/build_features.py
python scripts/generate_recommendations.py
python scripts/evaluate_model.py
streamlit run app/FPL-EDGE.py