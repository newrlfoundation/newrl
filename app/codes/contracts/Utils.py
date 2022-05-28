import math

#Min Yes Votes Voting Scheme
#ProposalAccepted - if min_yes yes votes is met
#ProposalRejected - if min_yes-1 no votes is met
def voting_scheme_one(self,callparams):

    min_yes_proportion = callparams['voting_scheme_params']['min_yes_votes']
    total_votes = callparams['total_votes']
    current_yes_votes = callparams['current_yes_votes']
    current_no_votes = callparams['current_no_votes']

    min_yes_votes = math.ceil((total_votes*min_yes_proportion)/100)
    if(current_yes_votes >= min_yes_votes):
        return 1
    elif(current_no_votes>= min_yes_votes-1):
        return -1
    else:
        return 0        
    # row = cur.execute(f'''select yes_votes as yes_votes,no_votes as no_votes,abstain_votes as abstain_votes,max_votes as max_votes from proposal where proposal_id=?''', callparams['proposal_id'])
    # #maxNo votes and minYes votes
    # #change min yes and no votes to dao params
    # data = row.fetchone()
    #check if min votes are met  
def voting_scheme_two(self,cur,callparams):

    pass
def voting_scheme_three(self,cur,callparams):
    pass

def voting_scheme_token(self,cur,callparams):
    '''
    TODO 
    params : 
    function
    '''
    pass