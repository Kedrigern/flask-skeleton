from typing import TypeVar, Generic
from sqlalchemy.exc import IntegrityError
from my_web.extensions import db

T = TypeVar("T", bound=db.Model)


class CRUDService(Generic[T]):
    """
    Generic CRUD operations for any SQLAlchemy Model.
    Inheriting services must define MODEL and can optionally override PK_NAME.
    """

    MODEL: type[T] = None
    PK_NAME: str = "id"
    FILTER_FIELD: str | None = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """
        Enforces that subclasses define the MODEL attribute.
        """
        super().__init_subclass__(**kwargs)
        if cls.MODEL is None:
            raise TypeError(
                f"Class {cls.__name__} must define the 'MODEL' attribute "
                "pointing to a SQLAlchemy model class."
            )

    def get(self, entity_id: int) -> T | None:
        """Retrieves a single entity by ID using modern session.get."""
        return db.session.get(self.MODEL, entity_id)

    def get_all(self) -> list[T]:
        """Retrieves all entities of the model."""
        return db.session.execute(db.select(self.MODEL)).scalars().all()

    def create(self, data: dict, commit: bool = True) -> T:
        """Creates a new entity from a data dictionary."""
        try:
            entity = self.MODEL(**data)
            db.session.add(entity)
            if commit:
                db.session.commit()
            else:
                db.session.flush()
            return entity
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Integrity error when creating {self.MODEL.__name__}")

    def update(self, entity_id: int, data: dict, commit: bool = True) -> T | None:
        """Updates an existing entity by ID. Ignores primary key from data."""
        entity = self.get(entity_id)
        if not entity:
            return None

        pk_name = self.PK_NAME

        # Update attributes dynamically from data dictionary
        for key, value in data.items():
            # CRITICAL SAFETY CHECK: Prevent overwriting the primary key
            if key == pk_name:
                continue

            # Check if the model has this attribute before setting it
            if hasattr(entity, key):
                setattr(entity, key, value)

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()
            return entity
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Integrity error when updating {self.MODEL.__name__}")

    def delete(self, entity_id: int, commit: bool = True) -> bool:
        """Deletes an entity by ID."""
        entity = self.get(entity_id)
        if not entity:
            return False

        db.session.delete(entity)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        return True

    def upsert(
        self, entity_id: int | None, data: dict, commit: bool = True
    ) -> tuple[T, bool]:
        """
        Creates or updates an entity based on the presence of entity_id.
        Returns: tuple of (Entity, is_newly_created: bool)
        """
        is_new = False
        entity = None

        if entity_id is not None:
            entity = self.get(entity_id)

        if entity:
            # UPDATE PATH
            is_new = False
            pk_name = self.PK_NAME

            # Apply data fields to existing entity (Update logic)
            for key, value in data.items():
                # CRITICAL SAFETY CHECK: Prevent overwriting the primary key
                if key == pk_name:
                    continue
                if hasattr(entity, key):
                    setattr(entity, key, value)
        else:
            is_new = True
            entity = self.MODEL(**data)
            db.session.add(entity)

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()
            return entity, is_new
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Integrity error during upsert of {self.MODEL.__name__}")

    def get_paginated(
        self,
        page: int = 1,
        per_page: int = 10,
        sort_field: str | None = None,
        sort_dir: str = "asc",
        filter_value: str | None = None,
    ) -> dict:
        """
        Retrieves a paginated list with optional sorting and filtering on the FILTER_FIELD.
        """
        stmt = db.select(self.MODEL)

        # 1. Simple Filtering
        if filter_value and self.FILTER_FIELD:
            col = getattr(self.MODEL, self.FILTER_FIELD, None)
            if col is not None:
                search_pattern = "%" + filter_value + "%"
                stmt = stmt.where(col.ilike(search_pattern))

        # 2. Simple Sorting
        sort_field = (
            sort_field
            if sort_field and hasattr(self.MODEL, sort_field)
            else self.PK_NAME
        )
        col = getattr(self.MODEL, sort_field, None)

        if col is not None:
            if sort_dir == "desc":
                stmt = stmt.order_by(col.desc())
            else:
                stmt = stmt.order_by(col.asc())

        pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

        return {
            "last_page": pagination.pages,
            "data": [entity.as_dict() for entity in pagination.items],
        }

    def get_by_name(self, name: str) -> T | None:
        """Retrieves a single entity by its name field."""
        if not hasattr(self.MODEL, self.FILTER_FIELD):
            raise AttributeError(
                f"{self.MODEL.__name__} does not have a 'name' attribute."
            )

        stmt = db.select(self.MODEL).where(self.FILTER_FIELD == name)
        return db.session.execute(stmt).scalars().first()
