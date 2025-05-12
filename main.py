from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

app = FastAPI()

engine = create_engine('postgresql://postgres:root@localhost:900/postgres')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()

class Author(Base):

    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))



class Post(Base):

    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    created = Column(DateTime)
    authorid = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'))
    author = relationship('Author')


Base.metadata.create_all(bind=engine)


@app.post("/authors")
def create_author(name: str):

    if not name:
        return JSONResponse(content={'error': 'Name is required'}, status_code=400)
    
    try:
        author = Author(name=name)
        session.add(author)
        session.commit()
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

    return JSONResponse(content={'id': author.id, 'name': author.name}, status_code=201)

@app.put("/authors")
def put_author(id: int, name: str):
    if not id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    if not name:
        return JSONResponse(content={'error': 'Name is required'}, status_code=400)
    
    try:
        author = session.query(Author).filter_by(id=id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        author.name = name
        session.commit()
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

    return JSONResponse(content={'id': author.id, 'name': author.name}, status_code=200)


@app.delete("/authors")
def delete_author(id: int):
    if not id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    
    try:
        author = session.query(Author).filter_by(id=id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        session.delete(author)
        session.commit()
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
    return JSONResponse(content={'message': 'Author deleted successfully'}, status_code=200)

@app.get('authors/{author_id}')
def get_author(author_id: int):
    if not author_id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    
    try:
        author = session.query(Author).filter_by(id=author_id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
    return JSONResponse(content={'id': author.id, 'name': author.name}, status_code=200)


@app.get('/authors/all')
def get_all_authors():
    try:
        author_list = session.query(Author).all()
        if not author_list:
            return JSONResponse(content={'error': 'No authors found'}, status_code=404)
        authors = []
        for author in author_list:
            authors.append({'id':author.id, 'name': author.name})
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
    return JSONResponse(content=authors, status_code=200)