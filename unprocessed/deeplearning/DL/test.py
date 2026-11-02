text = 'You say goodby and I say hello.'

text = text.lower()
text = text.replace('.', ' .')
words = text.split(' ')
print(words)

# import re
# words = re.split(r'\s+', text)
# print(words)

word_to_id = {}
id_to_word = {}

for word in words:
    if word not in word_to_id:
        new_id = len(word_to_id)
        word_to_id[word] = new_id
        id_to_word[new_id] = word
        
print(id_to_word)
print(word_to_id)

import numpy as np
corpus = [word_to_id[w] for w in words]
corpus = np.array(corpus)
print(corpus)