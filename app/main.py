from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import Term
from .schemas import TermSchema

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/terms")
def get_terms(db: Session = Depends(get_db)):
    return db.query(Term).all()

@app.get("/terms/{keyword}")
def get_term(keyword: str, db: Session = Depends(get_db)):
    term = db.query(Term).filter(Term.keyword == keyword).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    return term

@app.post("/terms")
def add_term(term: TermSchema, db: Session = Depends(get_db)):
    db_term = Term(keyword=term.keyword, description=term.description)
    db.add(db_term)
    db.commit()
    return {"message": "Term added"}

@app.put("/terms")
def update_term(term: TermSchema, db: Session = Depends(get_db)):
    db_term = db.query(Term).filter(Term.keyword == term.keyword).first()
    if not db_term:
        raise HTTPException(status_code=404, detail="Term not found")
    db_term.description = term.description
    db.commit()
    return {"message": "Term updated"}

@app.delete("/terms/{keyword}")
def delete_term(keyword: str, db: Session = Depends(get_db)):
    db_term = db.query(Term).filter(Term.keyword == keyword).first()
    if not db_term:
        raise HTTPException(status_code=404, detail="Term not found")
    db.delete(db_term)
    db.commit()
    return {"message": "Term deleted"}