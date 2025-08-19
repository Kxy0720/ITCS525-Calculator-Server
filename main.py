import math
from collections import deque
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter

from calculator import expand_percent

HISTORY_MAX = 1000
history = deque(maxlen=HISTORY_MAX)

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Safe evaluator ----------
aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})


@app.post("/calculate")
def calculate(expr: str):
    """
    Performs a calculation and stores the result in history.
    """
    try:
        code = expand_percent(expr)
        result = aeval(code)
        
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            response = {"ok": False, "expr": expr, "result": "", "error": msg}
        else:
            response = {"ok": True, "expr": expr, "result": result, "error": ""}
            
        history_item = {
            "timestamp": datetime.now().isoformat(),
            "expression": expr,
            "result": response["result"],
            "ok": response["ok"],
            "error": response["error"]
        }
        history.append(history_item)
        return response
        
    except Exception as e:
        response = {"ok": False, "expr": expr, "error": str(e)}
        history_item = {
            "timestamp": datetime.now().isoformat(),
            "expression": expr,
            "result": None,
            "ok": False,
            "error": str(e)
        }
        history.append(history_item)
        return response

@app.get("/history")
def get_history(limit: int = Query(10, ge=1, le=HISTORY_MAX)):
    """
    Retrieves the calculation history.
    """
    return {"history": list(history)[-limit:]}

@app.delete("/history")
def clear_history():
    """
    Clears the entire calculation history.
    """
    history.clear()
    return {"message": "History cleared successfully."}