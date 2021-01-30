"""
This file contains helper functions for text processing.
"""
import string

def create_suggestions_dict(in_string):
    """
    Creates suggestion dictionary

    Args:
        in_string (str): string to create suggestions for

    Returns:
        dict : dictionary containing Blooms and Complexity suggestion
    
    """
    sug_dict = {
        'blooms' : blooms_suggestion(in_string),
        'complex' : is_complex(in_string)
    }

    return(sug_dict)
        
def blooms_words(level):
    """
    Returns words indicative of certain level

    Args:
        level (str): Bloom's level to get words for
    Returns:
        dict : dictionary of words matching level
    """
    create_words = ['design', 'assemble', 'construct', 'conjecture', 'develop',
                    'formulate', 'author', 'investigate', 'create', 'adapt', 'plan',
                    'produce', 'build', 'solve', 'compose', 'think', 'theorize', 'modify',
                    'improve']
    evaluate_words = ['appraise', 'argue', 'defend', 'judge', 'select', 'support',
                      'value', 'critique', 'weigh', 'evaluate', 'assess', 'compare', 'conclude',
                      'debate', 'decide', 'measure', 'opinion', 'prove', 'support', 'test', 
                      'validate', 'interpret']
    analyze_words = ['differentiate', 'organize', 'relate', 'compare', 'contrast',
                     'distinguish', 'examine', 'experiment', 'question', 'test',
                     'analyze', 'arrange', 'breakdown', 'categorize', 'differences',
                     'dissect', 'inspect', 'research', 'highlight', 'find', 'question']
    apply_words = ['execute', 'implement', 'solve', 'use', 
                   'interpret', 'operate', 'schedule', 'sketch', 'apply',
                   'act', 'administer', 'build', 'choose', 'connect', 'construct', 'develop',
                   'teach', 'plan', 'employ', 'demonstrate', 'show']
    understand_words = ['describe', 'explain', 'identify', 'locate', 'recognize', 'report', 
                        'select', 'translate', 'understand', 'ask', 'cite', 'classify', 
                        'compare', 'contrast', 'discuss', 'rephrase', 'infer', 'summarize', 
                        'purpose', 'show', 'demonstrate', 'express', 'examples']
    remember_words = ['define', 'duplicate', 'list', 'memorize', 'repeat', 'state',
                      'remember', 'copy', 'recognize', 'tell', 'reproduce', 'retell',
                      'recite', 'read', 'knowledge']
    if(level=="KN"):
        return remember_words
    elif(level=="CO"):
        return understand_words
    elif(level=="AP"):
        return apply_words
    elif(level=="AN"):
        return analyze_words
    elif(level=="SN"):
        return create_words
    elif(level=="EV"):
        return evaluate_words


# Returns a string corresponding to a Bloom's taxonomy
def blooms_suggestion(in_string):
    """
    Creates suggestion of Bloom's taxonomy level

    Args:
        in_string (str) : input string to generate suggestions from

    Returns:
        str : suggested level
    """
    create_words = ['design', 'assembl', 'construct', 'conjectur', 'develop',
                    'formulat', 'author', 'investigat', 'creat', 'adapt', 'plan',
                    'produc', 'buil', 'solv', 'compos', 'think', 'thought' 'theoriz', 'modif',
                    'improv']
    evaluate_words = ['apprais', 'argu', 'defend', 'judg', 'select', 'support',
                      'valu', 'critiqu', 'weigh', 'evaluat', 'assess', 'compar', 'conclud',
                      'debat', 'decid', 'measur', 'opinion', 'prov', 'support', 'test', 
                      'validat', 'interpret']
    analyze_words = ['differentiat', 'organiz', 'relat', 'compar', 'contrast',
                     'distinguish', 'examin', 'experiment', 'question', 'test',
                     'analyz', 'arrang', 'breakdown', 'categoriz', 'differen',
                     'dissect', 'inspect', 'research', 'highlight', 'find', 'question']
    apply_words = ['execut', 'implement', 'solv', 'use', 'using' 
                   'interpret', 'operat', 'schedul', 'sketch', 'appl',
                   'act', 'administer', 'build', 'choos', 'connect', 'construct', 'develop',
                   'teach', 'plan', 'employ', 'demonstrat', 'show', 'analysis']
    understand_words = ['describ', 'explain', 'identif', 'locat', 'recogniz', 'report', 
                        'select', 'translat', 'understand', 'ask', 'cit', 'classif', 
                        'compar', 'contrast', 'discuss', 'rephrase', 'infer', 'summariz', 
                        'purpos', 'show', 'demonstrat', 'express', 'example','exemplif', 'comprehend']
    remember_words = ['defin', 'duplicat', 'list', 'memoriz', 'repeat', 'stat',
                      'remember', 'copy', 'recogniz', 'tell', 'retell', 'reproduc',
                      'recit', 'read', 'knowledge']
    score_dict = {
        'Evaluation' : 0,
        'Synthesis' : 0,
        'Analysis' : 0,
        'Application' : 0,
        'Comprehension' : 0,
        'Knowledge' : 0,
    }

    low_string = in_string.lower()

    score_dict["Evaluation"] = count_level_score(evaluate_words,low_string)
    score_dict["Synthesis"] = count_level_score(create_words,low_string)
    score_dict["Analysis"] = count_level_score(analyze_words,low_string)
    score_dict['Application'] = count_level_score(apply_words,low_string)
    score_dict['Comprehension'] = count_level_score(understand_words,low_string)
    score_dict["Knowledge"] = count_level_score(remember_words,low_string)
    suggestion = max(score_dict, key=score_dict.get)
    
    if score_dict[suggestion] == 0:
        suggestion = 'none'

    return(suggestion)

def count_level_score(rootSet,in_string):
    """
    Counts how many key-root words appear within the string

    Args:
        rootSet (str): set of root words to count
        in_string (str): string to count instances of
    Returns:
        int : the number of key roots
    """
    score = 0
    for word in rootSet:
        #since all roots are at the beginning, the substring found is at the beginning of the word
        #Since SLOs are supposed to be a sentence, assuming space is the only white space character
        #is not too strong of an assumption.
        score = score + in_string.count(" "+word)
        if in_string.startswith(word):
            score = score + 1
    return score

def is_complex(in_string):
    """
    Returns a boolean stating whether the given phrase is complex
    complexity is measured by having more than 3 words belonging to
    the following set: and, or, but

    Args:
        in_string (str): string to evaluate complexity of
    Returns:
        bool : whether the string should be considered complex
    """
    conjunctions = ['and', 'or', 'but']
    max_conjs = 3
    num_conjs = 0

    for word in in_string.split(" "):
        tword = word.translate(str.maketrans("","", string.punctuation))
        if tword in conjunctions:
            num_conjs += 1
    
    if num_conjs > max_conjs:
        return True
    return False