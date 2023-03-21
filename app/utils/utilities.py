from collections import Counter

def data_for_shulze(votes: list[*]) -> list[tuple(list[*list], int)]:
    temp_dict = Counter([(
        vote.first_vote,
        vote.secondd_vote,
        vote.third_vote
    ) for vote in votes])
    
    result = []
    
    for vote, counter in zip(temp_dict.keys, temp_dict.values):
        vote = list(map(list, vote))
        result.append(tuple(vote, counter))
        
    return result
    