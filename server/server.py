import grpc
from concurrent import futures
import sqlite3
from proto import glossary_pb2, glossary_pb2_grpc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Term, create_tables

DATABASE_URL = "sqlite:///glossary.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

create_tables(engine)

class GlossaryServiceServicer(glossary_pb2_grpc.GlossaryServiceServicer):

    def AddTerm(self, request, context):
        db_session = SessionLocal()

        try:
            new_term = Term(keyword=request.keyword, description=request.description)
            db_session.add(new_term)
            db_session.commit()
            return glossary_pb2.TermResponse(message=f"Term '{request.keyword}' added successfully!")
        except Exception as e:
            db_session.rollback()
            context.set_details(f"Error adding term: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return glossary_pb2.TermResponse(message="Failed to add term.")
        finally:
            db_session.close()

    def GetTerm(self, request, context):
        db_session = SessionLocal()
        try:
            term = db_session.query(Term).filter(Term.keyword == request.keyword).first()
            if term:
                return glossary_pb2.Term(keyword=term.keyword, description=term.description)
            context.set_details("Term not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return glossary_pb2.Term()
        except Exception as e:
            context.set_details(f"Error fetching term: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return glossary_pb2.Term()
        finally:
            db_session.close()

    def GetAllTerms(self, request, context):
        db_session = SessionLocal()
        try:
            terms = db_session.query(Term).all()
            terms_list = [glossary_pb2.Term(keyword=term.keyword, description=term.description) for term in terms]
            return glossary_pb2.TermsList(terms=terms_list)
        except Exception as e:
            context.set_details(f"Error fetching all terms: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return glossary_pb2.TermsList()
        finally:
            db_session.close()

    def UpdateTerm(self, request, context):
        db_session = SessionLocal()
        try:
            term = db_session.query(Term).filter(Term.keyword == request.keyword).first()
            if term:
                term.description = request.description
                db_session.commit()
                return glossary_pb2.TermResponse(message=f"Term '{request.keyword}' updated successfully!")
            context.set_details("Term not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return glossary_pb2.TermResponse(message="Term not found.")
        except Exception as e:
            db_session.rollback()
            context.set_details(f"Error updating term: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return glossary_pb2.TermResponse(message="Failed to update term.")
        finally:
            db_session.close()

    def DeleteTerm(self, request, context):
        db_session = SessionLocal()
        try:
            term = db_session.query(Term).filter(Term.keyword == request.keyword).first()
            if term:
                db_session.delete(term)
                db_session.commit()
                return glossary_pb2.TermResponse(message=f"Term '{request.keyword}' deleted successfully!")

            context.set_details("Term not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return glossary_pb2.TermResponse(message="Term not found.")
        except Exception as e:
            db_session.rollback()
            context.set_details(f"Error deleting term: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return glossary_pb2.TermResponse(message="Failed to delete term.")
        finally:
            db_session.close()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    glossary_pb2_grpc.add_GlossaryServiceServicer_to_server(GlossaryServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Server started at [::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()