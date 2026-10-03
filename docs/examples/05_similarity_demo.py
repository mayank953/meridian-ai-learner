"""The idea behind a vector database, with tiny made-up vectors. No cloud account needed.

Run:    python 05_similarity_demo.py

Real embeddings have 768 numbers. Here we use 3 so you can see the maths.
Texts with a similar meaning get vectors that point in a similar direction.
A vector database finds the stored vector closest to the question's vector.
"""
import math

# Pretend embeddings (invented for illustration)
documents = {
    "Servo motors are paid on Net-45 terms":      [0.9, 0.1, 0.0],
    "Filling line equipment is depreciated over 10 years": [0.1, 0.9, 0.1],
    "Revenue in FY2024 was EUR 2.84 billion":     [0.0, 0.2, 0.9],
}
question = ("When do we pay servo motor suppliers?", [0.8, 0.2, 0.1])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cosine(a, b):
    return dot(a, b) / (math.sqrt(dot(a, a)) * math.sqrt(dot(b, b)))


print("Question:", question[0], "\n")
scores = [(cosine(question[1], vec), text) for text, vec in documents.items()]
for score, text in sorted(scores, reverse=True):
    print(f"{score:5.2f}  {text}")

print("\nThe top result is what RAG would hand to the model as context.")
print("(Meridian's index uses DOT_PRODUCT_DISTANCE, a close relative of cosine similarity.)")
