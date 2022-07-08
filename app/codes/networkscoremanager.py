"""Helper functions for network trust score updates"""
from math import sqrt

from app.constants import MAX_NETWORK_TRUST_SCORE


def get_valid_block_creation_score(current_score):
    score_diff = sqrt(MAX_NETWORK_TRUST_SCORE - current_score)/2
    new_score = int(current_score + score_diff)
    return new_score


def get_invalid_block_creation_score(current_score):
    score_diff = 5 * MAX_NETWORK_TRUST_SCORE/100 + 0.01 * current_score
    new_score = int(current_score - score_diff)
    return new_score


def get_valid_receipt_score(current_score):
    score_diff = sqrt(MAX_NETWORK_TRUST_SCORE - current_score) / 20
    new_score = int(current_score + score_diff)
    return new_score


def get_invalid_receipt_score(current_score):
    score_diff = 0.5 * (MAX_NETWORK_TRUST_SCORE/100 + 0.01 * current_score)
    new_score = int(current_score - score_diff)
    return new_score


