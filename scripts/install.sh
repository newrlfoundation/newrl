git pull
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
export NEWRL_ENV=$1
python -m app.migrations.init
# python -m app.migrations.migrate_db
python -m app.codes.auth.make_auth --createnewwallet
