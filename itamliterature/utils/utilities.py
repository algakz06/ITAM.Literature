from collections import Counter
from itamliterature.models.models import Vote

def data_for_shulze(votes: list[Vote]) -> list[tuple[Vote, int]]:
    temp_dict = Counter([(
        vote.first_vote,
        vote.second_vote,
        vote.third_vote
    ) for vote in votes])
    
    result = []
    

    for vote, counter in temp_dict.items():
        print(type(vote), type(counter))
        vote = list(map(lambda vote: [vote], vote))
        result.append((vote, counter))
    
    return result
    