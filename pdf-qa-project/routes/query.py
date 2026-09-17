from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.embedding_service import get_embedding
from services.vector_store import collection, search_similar_chunks
from services.llm_service import ask_llm

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: QueryRequest):
    if collection.count() == 0:
        raise HTTPException(status_code=400, detail="Upload and index a PDF before asking a question.")
    q_embedding = get_embedding(request.question)
    relevant_chunks = search_similar_chunks(q_embedding, top_k=3)
    try:
        answer = ask_llm(request.question, relevant_chunks)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="The answer service is unavailable. Check the GROQ_API_KEY and Render logs.") from exc

    return {"answer": answer}