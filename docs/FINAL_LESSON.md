# Introduction to RAG

## 1. What is RAG?

RAG stands for **Retrieval-Augmented Generation**.

It is a way to help an AI answer questions by first finding useful information and then giving that information to the AI before it writes the answer.

Think of it like an open-book test.

A student does not have to remember every fact. The student can first look at the correct page and then answer the question.

RAG follows a similar idea:

**Question → Find useful information → Give it to the AI → Write the answer**

## 2. Why do we need RAG?

An AI model may not know your private or newly updated information.

For example, imagine a college has a document called `Student_Handbook.pdf`. It contains rules about attendance, exams, and holidays.

A student asks:

> "How many days of attendance do I need?"

Instead of asking the AI to answer only from what it already knows, a RAG system can first find the attendance rule from the handbook.

Then the AI uses that information to write the answer.

This can make answers more connected to the information you provide.

## 3. How does RAG work?

A simple RAG system has these steps:

### Step 1: The user asks a question

Example:

> "What is the attendance requirement?"

### Step 2: The system searches for useful information

The system looks through stored documents and finds the part that talks about attendance.

This search step is called **retrieval**. Retrieval simply means finding useful information.

### Step 3: The useful information is given to the AI

The selected text is added to the information sent to the AI model.

The AI now has the question plus useful context from the document.

**Context** means information that helps the AI understand what it should answer.

### Step 4: The AI writes the answer

The AI reads the question and the retrieved information and creates a natural-language answer.

## 4. A simple example

Suppose the college handbook says:

> "Students must have at least 75% attendance to appear for the final examination."

The student asks:

> "What attendance do I need for the final exam?"

The RAG system retrieves the sentence about 75% attendance.

The AI can then answer:

> "You need at least 75% attendance to appear for the final examination."

The important idea is that the answer is based on information retrieved from the handbook.

## 5. What happens inside the search?

Large document collections can contain many pages.

A RAG system often breaks documents into smaller pieces called **chunks**.

A chunk is simply a small section of a document.

The system can then compare the user's question with these chunks and select the ones that look most useful.

Some RAG systems use **embeddings** for this comparison. An embedding is a numerical representation of text that helps a computer compare the meaning of pieces of text.

For a beginner, the main idea is enough:

**Question → compare with document pieces → select useful pieces**

## 6. RAG vs normal AI answering

Without RAG:

**Question → AI → Answer**

With RAG:

**Question → Search information → AI + found information → Answer**

RAG is useful when the answer depends on a specific collection of information.

## 7. Limitations of RAG

RAG does not automatically make every answer correct.

If the search finds the wrong information, the AI may receive poor context.

If the documents contain incorrect information, the generated answer can also be wrong.

The system therefore needs good document processing, good retrieval, and evaluation.

## 8. Quick recap

Remember these four ideas:

1. **RAG means Retrieval-Augmented Generation.**
2. It first **retrieves useful information**.
3. It gives that information to an **AI model as context**.
4. The AI then **generates an answer** using the question and retrieved information.

In one line:

**RAG = find useful information first, then use AI to answer.**
