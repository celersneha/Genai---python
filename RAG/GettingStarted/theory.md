RAG (Retrieval-Augmented Generation) improves LLM responses by letting the model access external knowledge sources before generating answers. This makes responses more accurate, relevant, and up-to-date without retraining the model.

### Disadvantages of not using RAG:

1. Hallucinations (incorrect/confident wrong answers)
2. Outdated information
3. Limited to training data
4. Less accurate domain-specific responses
5. Cannot access real-time knowledge
6. Higher chances of irrelevant answers
7. Requires expensive retraining for new data

### RAG is preferred over fine-tuning because it is:

- Cheaper and faster
- Easy to update with new data
- Can use real-time information
- Reduces hallucinations
- No retraining needed for every update

Fine-tuning is mainly used for changing model behavior, style, or specific tasks.

Traditional RAG (Retrieval-Augmented Generation) is the classic pipeline where external data is retrieved first and then given to the LLM as context before generating a response.

### Traditional RAG Flow 🔄

#### 1) Data Ingestion

Documents like:

- PDFs
- HTML
- Excel
- SQL DB data

are collected.

---

#### 2) Parsing & Chunking

Large documents are:

- parsed
- split into smaller chunks

Example:

```text
Chunk 1
Chunk 2
Chunk 3
```

This improves retrieval accuracy.

---

#### 3) Embedding Generation

Each chunk is converted into vectors using an embedding model.

```text
Text → Embedding Vector
```

---

#### 4) Store in Vector DB

These vectors are stored in:

- Pinecone
- Qdrant
- FAISS
- Weaviate

This becomes the knowledge base.

---

### Query Time ⚡

#### 5) User Sends Query

Example:

```text
"What is the leave policy?"
```

---

#### 6) Query Embedding

The query is also converted into a vector.

```text
Query → Vector
```

---

#### 7) Similarity Search

Vector DB finds the most similar chunks using cosine similarity or nearest-neighbor search.

```text
Top K relevant chunks retrieved
```

---

#### 8) Context Augmentation

Retrieved chunks are added to the prompt.

```text
Context:
[Retrieved Chunks]

Question:
What is the leave policy?
```

---

#### 9) LLM Generates Response

The LLM answers using:

- retrieved context
- user query

instead of relying only on training data.

---

### Why It’s Called “Retrieval-Augmented”

Because the generation is _augmented_ with retrieved external knowledge 📚

### Main Advantage 🚀

- More accurate
- Less hallucination
- Updatable knowledge
- No retraining needed
