from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, random, string

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MERCHANT_WALLET = "UQB0FWkSh3INjx13_XW6o4ZiET3HPVDIBSJxGi6iEemTaaub"
PRICE_TON = 10
TONCENTER_API =   c2c00ad475e8146b7fd29b88a3dbbad93b864a8b1c3831fec4881284753df48b# Получи на toncenter.com

orders = {}

@app.post("/create-payment")
async def create_payment(user_id: str):
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    orders[order_id] = {"user_id": user_id, "status": "pending"}
    return {"order_id": order_id, "address": MERCHANT_WALLET, "amount": PRICE_TON}

@app.post("/verify-payment")
async def verify_payment(order_id: str, tx_hash: str):
    if order_id not in orders:
        return {"status": "error", "message": "Заказ не найден"}
    
    url = f"https://toncenter.com/api/v2/getTransactions?address={MERCHANT_WALLET}&limit=20&api_key={TONCENTER_API}"
    response = requests.get(url).json()
    
    for tx in response.get("result", []):
        tx_hash_actual = tx["transaction_id"]["hash"]
        if tx_hash_actual == tx_hash:
            amount_nano = int(tx["in_msg"]["value"])
            amount_ton = amount_nano / 1_000_000_000
            if amount_ton >= PRICE_TON:
                orders[order_id]["status"] = "paid"
                return {"status": "success", "order_id": order_id}
            else:
                return {"status": "error", "message": "Недостаточная сумма"}
    
    return {"status": "pending", "message": "Транзакция еще не найдена"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)