from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import analytics
from app.collector import collect_all
from app.db import get_db, init_db
from app.history import snapshot_prices, get_price_history

app = FastAPI(title="Price Scout", version="0.1.0")

scheduler = BackgroundScheduler()


@app.on_event("startup")
def on_startup():
    init_db()
    if not scheduler.running:
        scheduler.add_job(run_collection, "interval", hours=6, id="collect")
        scheduler.start()


def run_collection():
    from app.db import SessionLocal
    db = SessionLocal()
    try:
        report = collect_all(db)
        snapshot_prices(db)
        print("Collection report:", report)
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok", "service": "price-scout"}


@app.post("/collect")
def trigger_collect(db: Session = Depends(get_db)):
    report = collect_all(db)
    snapshot_prices(db)
    return {"report": report}


@app.get("/offers")
def offers(db: Session = Depends(get_db)):
    return analytics.get_best_offers(db)


@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    return analytics.get_price_stats(db)


@app.get("/categories")
def categories(db: Session = Depends(get_db)):
    return analytics.get_category_summary(db)


@app.get("/product/{product_id}")
def product_detail(product_id: int, db: Session = Depends(get_db)):
    detail = analytics.get_product_detail(db, product_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Product not found")
    return detail


@app.get("/product/{product_id}/history")
def product_history(product_id: int, db: Session = Depends(get_db)):
    return get_price_history(db, product_id)
