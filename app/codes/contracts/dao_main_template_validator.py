from ..db_updater import *


def create_proposal(cur, callparams):
    # We can have special roles assigned to the person so that some of them can only.
    dao_pid = get_pid_from_wallet(cur, callparams['address'])
    is_not_valid_member = (dao_member_dup_check(cur, callparams['params'], dao_pid) == 0)
    if is_not_valid_member:
        return {"status": 406, "message": "Not a member of DAO."}


def vote_on_proposal( cur, callparams):
    dao_pid = get_pid_from_wallet(cur, callparams['address'])
    is_not_valid_member = (dao_member_dup_check(cur, callparams['params'], dao_pid) == 0)
    if is_not_valid_member:
        return {"status": 406, "message": "Not a member of DAO."}


def add_member( cur, callparamsip):
    callparams = input_to_dict(callparamsip)
    dao_pid = get_pid_from_wallet(cur, callparams['address'])
    is_dao_exist = dao_member_dup_check(cur, callparams['params'], dao_pid)
    if pid_check(callparams, cur) == 0:
        return {"status": 406, "message": "Personid doesn't exists."}
    if is_dao_exist[0] != 0:
        return {"status": 406, "message": "Member already added."}


def delete_member( cur, callparamsip):
    callparams = input_to_dict(callparamsip)
    dao_pid = get_pid_from_wallet(cur, callparams['address'])
    is_dao_exist = dao_member_dup_check(cur, callparams['params'], dao_pid)
    if pid_check(callparams, cur) == 0:
        return {"status": 406, "message": "Personid doesn't exists."}
    if is_dao_exist[0] == 0:
        return {"status": 406, "message": "Person is not a DAO member."}


def dao_member_dup_check(cur, callparams, dao_pid):
    is_dao_exist = cur.execute(
        '''SELECT COUNT(*) FROM dao_membership WHERE dao_person_id LIKE ? AND member_person_id LIKE ?''',
        (dao_pid, callparams['member_person_id']))
    return is_dao_exist.fetchone()[0]


def pid_check(cur, callparams):
    is_pid_exists = cur.execute(
        f'''SELECT COUNT(*) FROM PERSON WHERE person_id=?'''
        , (callparams['member_person_id']))
    return is_pid_exists.fetchone()[0]
