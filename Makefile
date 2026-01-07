download:
	python -m src.ingest.download_ppd


load:
	python -m src.ingest.load_duckdb

validate:
	python -m src.ingest.validate_duckdb

clean:
	python -m src.cleaning.cleaning_ppd

analysis:
	python -m src.analysis.descriptive

chart:
	python -m src.analysis.descriptive_charts

temporal:
	python -m src.temporal.temporal

temporal_chart:
	python -m src.temporal.temporal_charts

regional:
	python -m src.regional.regional_analysis

regional_chart:
	python -m src.regional.regional_chart

task6:
	python -m src.run_task6

build_model:
	python -m src.modeling.build_model
train:
	python -m src.modeling.train_price_model

linear :
	python -m src.modeling.explain_linear

shap :
	python -m src.modeling.explain_shap

residual: 
	python -m src.modeling.residual_district

cluster:
	python -m src.modeling.cluster

cluster_district:
	python -m src.modeling.cluster_district

forecast:
	python -m src.modeling.forecast

app:
	streamlit run streamlit/app.py

export :
	python -m src.export_table
