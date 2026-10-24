
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from services.text_to_sql import generate_sql
from services.analytics import execute_query

app = FastAPI(title="Mini AI Business Intelligence Assistant")


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Mini AI BI Assistant API is running"}



@app.post("/api/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        print("1. Received question:", question, flush=True)

        print("2. Calling Gemini...", flush=True)
        sql = generate_sql(question)
        print("3. Gemini generated SQL:", sql, flush=True)

        print("4. Executing SQL...", flush=True)
        result = execute_query(sql)
        print("5. Query completed.", flush=True)

        return {
            "question": question,
            "sql": sql,
            "columns": result["columns"],
            "rows": result["rows"],
            "row_count": result["row_count"]
        }

    except ValueError as exc:
        print("Validation error:", exc, flush=True)
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        print("Backend error:", repr(exc), flush=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process the question. Check server logs."
        ) from exc

