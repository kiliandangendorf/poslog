######################
# TagComparison
######################
from dataclasses import dataclass

@dataclass
class TagComparison:
    majority:   list[str]
    confidence: list[float]
    minority:   list[dict[str, str]]

from collections import Counter

def _correct_tagset_mapping_inability(c:Counter, tagset)->Counter:
    if tagset=='upos':
        #TODO make manual adjustments for some tags

        # if there is only one X, then it is not a tag, so we remove it
        if 'X' in c and len(c)>=2:
            majority_tag=c.most_common(2)[1][0] if c.most_common(1)[0][0] == 'X' else c.most_common(1)[0][0]
            c[majority_tag]=c[majority_tag]+c['X']
            del c['X']

        # if AUX and VERB: AUX
        # PTB has no tag for "auxiliary verb" (AUX), it collects it under "verb" and maps it to VERB.
        # So if there are only AUX and VERB, then we repair it to AUX.
        if 'AUX' in c and 'VERB' in c and len(c)==2:
            c['AUX']=c['AUX']+c['VERB']
            del c['VERB']

        # if SCONJ and ADP: SCONJ
        # PTB has no tag for "subordinating conjunction" (SCONJ), it collects it under "IN" (preposition or subordinating conjunction) and maps it to ADP.
        # So if there are only SCONJ and ADP, then we repair it to SCONJ.
        if 'SCONJ' in c and 'ADP' in c and len(c)==2:
            c['SCONJ']=c['SCONJ']+c['ADP']
            del c['ADP']

        # if SYM and NUM: SYM
        if 'SYM' in c and 'NUM' in c and len(c)==2:
            c['SYM']=c['SYM']+c['NUM']
            del c['NUM']

        # remove NIL
        # NIL should never occur but if it does, then move it to majority
        if 'NIL' in c:
            majority_tag=c.most_common(1)[0][0]
            c[majority_tag]=c[majority_tag]+c['NIL']
            del c['NIL']

    return c

def make_tag_comparison(taggers_result:dict[str,list[str]], tagset='upos')->TagComparison:
    majority:list[str]=[]
    confidence:list[float]=[]
    minority:list[dict[str, str]]=[]    

    if not taggers_result:
        raise ValueError("No taggers results provided.")
        
    # length of first element in dict
    num_tokens=len(next(iter(taggers_result.values())))

    # compare tags for each word
    for t_i in range(num_tokens):
        c:Counter=Counter([v[t_i] for v in taggers_result.values()])
        # examples:
        # clear majority: Counter({'NUM': 5})
        # majority:  Counter({'NOUN': 3, 'VERB': 2}) or Counter({'NOUN': 4, 'VERB': 1}) or even Counter({'ADJ': 2, 'NOUN': 1, 'NUM': 1, 'X': 1})
        # parity:  Counter({'ADJ': 2, 'NOUN': 2, 'X': 1}) or Counter({'ADJ': 1, 'NOUN': 1, 'PUNCT': 1, 'NUM': 1, 'X': 1})

        # Make manual adjustments for some tags such as if two tagger say SCONJ and the other say ADP,
        # then the underlaying tagset had no SCONJ and the tagger mapped it to ADP, so we repair it to SCONJ
        c=_correct_tagset_mapping_inability(c, tagset)

        # case: clear majority
        if len(c)==1:
            majority.append(list(c.keys())[0])
            confidence.append(1.0)
            minority.append({})
        else:
            # note to sort descending for parity cases
            vals=sorted(c.values(), reverse=True)
            # if most common are the same => parity
            if vals[0]==vals[1]:
                majority.append(None)
                confidence.append(.0)
            else:
                majority.append(c.most_common(1)[0][0])
                #confidence.append(c.most_common(1)[0][1]/sum(c.values()))
                confidence.append(c.most_common(1)[0][1]/len(taggers_result))
            min_dict={}
            for tag in c.keys():
                if tag==majority[-1]:
                    continue
                min_dict.update({k:v[t_i] for k,v in taggers_result.items() if v[t_i]==tag})
            minority.append(min_dict)

    return TagComparison(majority, confidence, minority)

import numpy as np
def print_stats_on_tag_comparison(tag_comparisons:list[TagComparison])->None:
    clear_majority=0
    eighty_percent_majority=0
    absolute_majority=0
    diff_length=0
    none_in_majority=0
    none_times_in_words=0
    total_words=0
    clear_majority_words=0
    eighty_percent_majority_words=0
    absolute_majority_words=0
    for tag_comparison in tag_comparisons:
        if len(tag_comparison.majority)>0 and np.min(tag_comparison.confidence)==1:
            clear_majority+=1
        if min(tag_comparison.confidence)>=0.8:
            eighty_percent_majority+=1
        if min(tag_comparison.confidence)>0.5:
            absolute_majority+=1
        if len(tag_comparison.majority)==0:
            diff_length+=1
        if None in tag_comparison.majority:
            none_in_majority+=1
            none_times_in_words+=tag_comparison.majority.count(None)
        total_words+=len(tag_comparison.majority)
        clear_majority_words+=tag_comparison.confidence.count(1.0)+tag_comparison.confidence.count(1.1)
        eighty_percent_majority_words+=len([c for c in tag_comparison.confidence if c>=0.8])
        absolute_majority_words+=len([c for c in tag_comparison.confidence if c>0.5])
        
        
    #print(f"Different length: {diff_length} times ({diff_length/len(tag_comparisons)*100:.2f}%)")
    print(f'For whole log lines ({len(tag_comparisons)} in total):')
    print(f"Majority found: {len(tag_comparisons)-none_in_majority} times ({(len(tag_comparisons)-none_in_majority)/len(tag_comparisons)*100:.2f}%)")
    print(f"- Clear majority: {clear_majority} times ({clear_majority/len(tag_comparisons)*100:.2f}%)")
    print(f"- Eighty percent: {eighty_percent_majority} times ({eighty_percent_majority/len(tag_comparisons)*100:.2f}%)")
    print(f"- Absolute majority: {absolute_majority} times ({absolute_majority/len(tag_comparisons)*100:.2f}%)")
    print(f"Parity (None in majority): {none_in_majority} times ({none_in_majority/len(tag_comparisons)*100:.2f}%)")
    print()
    print(f'For words ({total_words} in total):')
    print(f"Majority found: {total_words-none_times_in_words} times ({(total_words-none_times_in_words)/total_words*100:.2f}%)")
    print(f"- Clear majority: {clear_majority_words} times ({clear_majority_words/total_words*100:.2f}%)")
    print(f"- Eighty percent: {eighty_percent_majority_words} times ({eighty_percent_majority_words/total_words*100:.2f}%)")
    print(f"- Absolute majority: {absolute_majority_words} times ({absolute_majority_words/total_words*100:.2f}%)")
    print(f"Parity (None in words): {none_times_in_words} times ({none_times_in_words/total_words*100:.2f}%)")
