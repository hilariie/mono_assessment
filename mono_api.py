import uvicorn
from fastapi import FastAPI
from mono import transaction_grouping
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Transaction(BaseModel):
    narration: str
    amount: int
    type: str
    date: str


@app.post("/")
def grouptransactions(transactions: List[Transaction]):
    transactions = [transaction.dict() for transaction in transactions]
    data = transaction_grouping(transactions)
    return {
        "status": "success",
        "data": data
    }


# specify a different port
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5049)