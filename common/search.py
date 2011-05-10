def match_keywords_to_something(query, l):
    '''given a query and a list of tuples in the form
    ((K1,K2,...), something)
    where Kn are keywords and something is what you want returned,
    matches the query to the keywords and returns a list of tuples in
    the form
    (processed_query, something)
    where processed_query is the query without the matched keyword'''
    result=[]
    for keywords, v in l:
        splited_query= query.split(' ')
        for keyword in keywords:
            try:
                i= splited_query.index(keyword)
                processed_query_splitted= splited_query[:]
                processed_query_splitted.pop(i)
                processed_query= " ".join(processed_query_splitted)
                result.append( (processed_query, v) )
            except:
                pass    #no match
    return result
