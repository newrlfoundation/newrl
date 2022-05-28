
git pull
# python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# python -m app.migrations.init
# scripts/migrate_db.sh
python -m app.main
