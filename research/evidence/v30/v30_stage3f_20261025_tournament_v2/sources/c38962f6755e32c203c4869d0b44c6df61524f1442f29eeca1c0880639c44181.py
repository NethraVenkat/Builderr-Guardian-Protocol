done=False
def decide(m,p,c):
 global done
 if done: return []
 done=True
 return [{'ticker':'SPY','side':'buy','quantity':1000}]
