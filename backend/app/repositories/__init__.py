"""Repositories package.

Repository classes abstract all database access.  Each repository
operates on a single ORM model and receives an ``AsyncSession`` via
dependency injection.  Services call repositories; routes never touch
the database directly.
"""
