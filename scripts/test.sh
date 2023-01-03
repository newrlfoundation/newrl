# mkdir data_test/
# rm data_test/mempool/*.json
# rm data_test/tmp/*.json
# rm data_test/newrl.db
# rm data_test/newrl_p2p.db
# cp data_test/template/newrl.db data_test/newrl.db
# cp data_test/template/newrl_p2p.db data_test/newrl_p2p.db
# source venv/bin/activate
export NEWRL_TEST='Y' && coverage run -m pytest app/tests/test_transfer.py
unset NEWRL_TEST
# rm data_test/mempool/*.json
# rm data_test/tmp/*.json