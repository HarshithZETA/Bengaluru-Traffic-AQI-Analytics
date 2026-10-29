python -m venv venv
.\venv\Scripts\python -m pip install --upgrade pip
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\python src\data_generator.py
.\venv\Scripts\python src\data_cleaning.py
.\venv\Scripts\python src\db_manager.py
.\venv\Scripts\streamlit run app.py