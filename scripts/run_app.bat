@echo off
echo Starting Streamlit... > batch_log.txt
python -m streamlit run app.py --server.port 8502 --server.address 127.0.0.1 >> batch_log.txt 2>&1
echo Done. >> batch_log.txt
