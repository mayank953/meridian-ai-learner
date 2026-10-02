import json, random
emb = [random.gauss(0, 1) for _ in range(768)]
data = {'id': 'init_0001', 'embedding': emb}
with open('init_embeddings.json', 'w') as f:
    f.write(json.dumps(data))
