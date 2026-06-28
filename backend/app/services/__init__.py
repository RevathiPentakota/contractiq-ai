"""Services package.

Business-logic services sit between route handlers and repositories.
Each service is a plain Python class (or set of functions) with no
direct dependency on FastAPI or SQLAlchemy sessions — those are
injected via ``Depends()``.
"""
