from stop_words.utils import save_stop_words

def extract():
    """Extract stop words from Fox's stop list (1989).
    
    Reference:
    Fox, C. (1989). A stop list for general text. ACM SIGIR Forum, 24(1-2), 19-35.
    DOI: 10.1145/378881.378888
    
    This list is in the public domain and was originally published in 1989.
    """
    # Fox's stop list (1989)
    stop_words = {
        'a', 'about', 'above', 'according', 'across', 'actually', 'after', 'afterwards',
        'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also',
        'although', 'always', 'among', 'amongst', 'an', 'and', 'another', 'any',
        'anybody', 'anyhow', 'anymore', 'anyone', 'anything', 'anyway', 'anywhere',
        'are', 'aren\'t', 'around', 'as', 'at', 'back', 'be', 'became', 'because',
        'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'begin',
        'beginning', 'begins', 'behind', 'being', 'believe', 'below', 'beside',
        'besides', 'between', 'beyond', 'both', 'but', 'by', 'came', 'can', 'cannot',
        'can\'t', 'certain', 'certainly', 'clearly', 'come', 'comes', 'could',
        'couldn\'t', 'did', 'didn\'t', 'different', 'do', 'does', 'doesn\'t', 'doing',
        'done', 'don\'t', 'down', 'downwards', 'during', 'each', 'either', 'else',
        'elsewhere', 'enough', 'entirely', 'especially', 'etc', 'even', 'ever',
        'every', 'everybody', 'everyone', 'everything', 'everywhere', 'except',
        'few', 'fifth', 'first', 'five', 'followed', 'following', 'follows', 'for',
        'former', 'formerly', 'forth', 'four', 'from', 'further', 'furthermore',
        'get', 'gets', 'getting', 'given', 'gives', 'go', 'goes', 'going', 'gone',
        'got', 'gotten', 'had', 'hadn\'t', 'happens', 'hardly', 'has', 'hasn\'t',
        'have', 'haven\'t', 'having', 'he', 'hence', 'her', 'here', 'hereafter',
        'hereby', 'herein', 'here\'s', 'hereupon', 'hers', 'herself', 'him',
        'himself', 'his', 'how', 'however', 'i', 'if', 'immediate', 'in', 'inasmuch',
        'inc', 'indeed', 'indicate', 'indicated', 'indicates', 'inner', 'inside',
        'insofar', 'instead', 'into', 'inward', 'is', 'isn\'t', 'it', 'its',
        'itself', 'just', 'keep', 'keeps', 'kept', 'know', 'known', 'knows',
        'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'let',
        'let\'s', 'like', 'liked', 'likely', 'little', 'look', 'looking', 'looks',
        'made', 'mainly', 'make', 'makes', 'many', 'may', 'maybe', 'me', 'mean',
        'means', 'meantime', 'meanwhile', 'merely', 'might', 'more', 'moreover',
        'most', 'mostly', 'much', 'must', 'my', 'myself', 'name', 'namely',
        'neither', 'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none',
        'noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often',
        'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise',
        'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall', 'however',
        'i', 'if', 'immediate', 'in', 'inasmuch', 'inc', 'indeed', 'indicate',
        'indicated', 'indicates', 'inner', 'inside', 'insofar', 'instead', 'into',
        'inward', 'is', 'isn\'t', 'it', 'its', 'itself', 'just', 'keep', 'keeps',
        'kept', 'know', 'known', 'knows', 'last', 'lately', 'later', 'latter',
        'latterly', 'least', 'less', 'let', 'let\'s', 'like', 'liked', 'likely',
        'little', 'look', 'looking', 'looks', 'made', 'mainly', 'make', 'makes',
        'many', 'may', 'maybe', 'me', 'mean', 'means', 'meantime', 'meanwhile',
        'merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 'must',
        'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless',
        'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing',
        'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only',
        'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves',
        'out', 'outside', 'over', 'overall', 'own', 'particular', 'particularly',
        'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 'presumably',
        'probably', 'provides', 'que', 'quite', 'rather', 'really', 'reasonably',
        'regarding', 'regardless', 'regards', 'relatively', 'respectively',
        'right', 'said', 'same', 'say', 'says', 'second', 'secondly', 'see',
        'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves',
        'sensible', 'sent', 'serious', 'seriously', 'seven', 'several', 'shall',
        'she', 'should', 'shouldn\'t', 'since', 'six', 'so', 'some', 'somebody',
        'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhat',
        'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'still',
        'sub', 'such', 'sup', 'sure', 't', 'take', 'taken', 'tell', 'tends',
        'than', 'that', 'that\'s', 'the', 'their', 'theirs', 'them', 'themselves',
        'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein',
        'there\'s', 'thereupon', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re',
        'they\'ve', 'think', 'third', 'this', 'thorough', 'thoroughly', 'those',
        'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to',
        'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'true',
        'try', 'trying', 'twice', 'two', 'un', 'under', 'unfortunately', 'unless',
        'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use', 'used', 'useful',
        'uses', 'using', 'usually', 'value', 'various', 'very', 'via', 'viz',
        'vs', 'want', 'wants', 'was', 'wasn\'t', 'way', 'we', 'we\'d', 'we\'ll',
        'we\'re', 'we\'ve', 'welcome', 'well', 'went', 'were', 'weren\'t', 'what',
        'what\'s', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter',
        'whereas', 'whereby', 'wherein', 'where\'s', 'whereupon', 'wherever',
        'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom',
        'who\'s', 'whose', 'why', 'will', 'willing', 'wish', 'with', 'within',
        'without', 'won\'t', 'wonder', 'would', 'wouldn\'t', 'yes', 'yet', 'you',
        'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself',
        'yourselves', 'zero'
    }
    
    save_stop_words(
        list(stop_words),
        'fox',
        description='Fox\'s stop list (1989) - A classical stop word list for general text',
        source='Christopher Fox (1989)',
        license='Public Domain',
        version='1.0',
        url='https://dl.acm.org/doi/10.1145/378881.378888'
    ) 