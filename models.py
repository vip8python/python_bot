import datetime
from sqlalchemy import String, Text, Date, Integer, ForeignKey, Float, Table, Column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


project_specialization_association = Table(
    'project_specialization', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('specialization_id', Integer, ForeignKey('specializations.id'), primary_key=True)
)

project_contact_association = Table(
    'project_contact', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('contact_method_id', Integer, ForeignKey('contact_methods.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    contacts: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    telegram_id: Mapped[str] = mapped_column(String(100))
    registered: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)

    projects = relationship("Project", back_populates="creator")
    reviews_given = relationship("UserReview", back_populates="reviewer", foreign_keys="[UserReview.reviewer_id]")
    reviews_received = relationship("UserReview", back_populates="reviewed", foreign_keys="[UserReview.reviewed_id]")


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))

    projects = relationship("Project", back_populates="category")


class Specialization(Base):
    __tablename__ = 'specializations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))

    projects = relationship("Project", secondary=project_specialization_association, back_populates="specializations")


class ContactMethod(Base):
    __tablename__ = 'contact_methods'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    method: Mapped[str] = mapped_column(String(100))

    projects = relationship("Project", secondary=project_contact_association, back_populates="contact_methods")


class Project(Base):
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    start_time: Mapped[datetime.date] = mapped_column(Date)
    end_time: Mapped[datetime.date] = mapped_column(Date)
    salary: Mapped[int] = mapped_column(Integer)
    participants_needed: Mapped[int] = mapped_column(Integer)
    repository_url: Mapped[str] = mapped_column(String(100))
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'))

    creator = relationship("User", back_populates="projects")
    category = relationship("Category", back_populates="projects")
    specializations = relationship("Specialization", secondary=project_specialization_association,
                                   back_populates="projects")
    contact_methods = relationship("ContactMethod", secondary=project_contact_association, back_populates="projects")
    reviews = relationship("ProjectReview", back_populates="project")
    participants = relationship("UserProject", back_populates="project", cascade="all, delete-orphan")
    qualifications = relationship("ProjectQualificationEmployee", back_populates="project")


class ProjectQualificationEmployee(Base):
    __tablename__ = 'project_qualification_employee'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'))
    qualification_id: Mapped[int] = mapped_column(Integer, ForeignKey('qualifications.id'))
    employees_count: Mapped[int] = mapped_column(Integer, nullable=False)
    salary_types_id: Mapped[int] = mapped_column(Integer, ForeignKey('salary_types.id'))
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default='EUR')

    project = relationship("Project", back_populates="qualifications")
    qualification = relationship("Qualification")
    salary_type = relationship("SalaryType", back_populates='types')


class UserProject(Base):
    __tablename__ = 'user_projects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'))

    user = relationship("User")
    project = relationship("Project")


class UserReview(Base):
    __tablename__ = 'user_reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    reviewed_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text)

    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewed = relationship("User", foreign_keys=[reviewed_id], back_populates="reviews_received")
    project = relationship("Project")


class ProjectReview(Base):
    __tablename__ = 'project_reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'))
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text)

    project = relationship("Project", back_populates="reviews")
    reviewer = relationship("User")


class Qualification(Base):
    __tablename__ = 'qualifications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))


class SalaryType(Base):
    __tablename__ = 'salary_types'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    types = relationship("ProjectQualificationEmployee", back_populates='salary_type')


class Admin(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    telegram_id: Mapped[str] = mapped_column(String(100))
