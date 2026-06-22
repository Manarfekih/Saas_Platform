import logging

from sqlalchemy.orm import Session


from app.services.retrieval_service import retrieve_chunks
from app.services.llm_service import ask_llm

from app.services.chat_memory_service import (
    save_message,
    get_history,
)


logger = logging.getLogger("saas-ia-platform")


MAX_CONTEXT_CHARS = 12000



def build_context(results):

    context_parts = []

    current_size = 0


    for chunk in results:

        text = chunk.content.strip()

        if not text:
            continue


        block = (
            f"[DOCUMENT CHUNK {chunk.chunk_index}]\n"
            f"{text}\n"
        )


        if current_size + len(block) > MAX_CONTEXT_CHARS:
            break


        context_parts.append(block)

        current_size += len(block)



    return "\n\n".join(context_parts)




def build_history(history):

    if not history:
        return "No previous conversation."


    messages = []


    for msg in history:

        messages.append(
            f"{msg.role.upper()}: {msg.content}"
        )


    return "\n".join(messages)





def generate_rag_prompt(
    question: str,
    context: str,
    history: str,
):


    return f"""

You are an AI document assistant.

You answer questions about the document.

Use ONLY the document context.

Conversation history is only for understanding previous questions.

Rules:
- Do not invent information.
- If the answer is not in the document say:
"I could not find that information in the document."
- Answer clearly and directly.


CHAT HISTORY:

{history}



DOCUMENT CONTEXT:

{context}



CURRENT QUESTION:

{question}



ANSWER:

""".strip()






def answer_question(
    db: Session,
    document_id: int,
    session_id: int,
    question: str,
    limit: int = 8
):


    logger.info(
        f"""
        RAG document={document_id}
        session={session_id}
        question={question}
        """
    )



    # =================================
    # 1. Save user message
    # =================================

    save_message(
        db=db,
        session_id=session_id,
        role="user",
        content=question
    )



    # =================================
    # 2. Load previous conversation
    # =================================


    history_messages = get_history(
        db=db,
        session_id=session_id,
        limit=10
    )


    history = build_history(
        history_messages
    )



    # =================================
    # 3. Retrieve document chunks
    # =================================


    chunks = retrieve_chunks(
        db=db,
        document_id=document_id,
        query=question,
        limit=limit,
    )



    if not chunks:


        answer = (
            "I could not find relevant information "
            "in this document."
        )


        save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=answer
        )


        return {

            "document_id": document_id,

            "answer": answer,

            "sources": []

        }




    # =================================
    # 4. Build context
    # =================================


    context = build_context(
        chunks
    )




    # =================================
    # 5. Build final prompt
    # =================================


    prompt = generate_rag_prompt(

        question=question,

        context=context,

        history=history

    )





    # =================================
    # 6. Ask Qwen
    # =================================


    response = ask_llm(
        prompt
    )


    answer = (

        response.content

        if hasattr(response,"content")

        else str(response)

    )



    answer = answer.strip()




    # =================================
    # 7. Save assistant answer
    # =================================


    save_message(

        db=db,

        session_id=session_id,

        role="assistant",

        content=answer

    )




    return {


        "document_id": document_id,


        "session_id": session_id,


        "answer": answer,


        "sources":[


            {

                "chunk_id": c.chunk_id,

                "chunk_index": c.chunk_index,

                "distance": float(c.distance)

            }

            for c in chunks

        ]

    }