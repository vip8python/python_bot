import datetime
from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey, Float, Table
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


project_specialization_association = Table(
    'project_specialization', Base.metadata,
    Column('project_id', ForeignKey('projects.id'), primary_key=True),
    Column('specialization_id', ForeignKey('specializations.id'), primary_key=True)
)

project_contact_association = Table(
    'project_contact', Base.metadata,
    Column('project_id', ForeignKey('projects.id'), primary_key=True),
    Column('contact_method_id', ForeignKey('contact_methods.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    contacts = Column(String(100))
    description = Column(Text)
    telegram_id = Column(String(100))
    registered = Column(Date, default=datetime.date.today)

    projects = relationship("Project", back_populates="creator")
    reviews_given = relationship("UserReview", back_populates="reviewer", foreign_keys="[UserReview.reviewer_id]")
    reviews_received = relationship("UserReview", back_populates="reviewed", foreign_keys="[UserReview.reviewed_id]")


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))

    projects = relationship("Project", back_populates="category")


class Specialization(Base):
    __tablename__ = 'specializations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))

    projects = relationship("Project", secondary=project_specialization_association, back_populates="specializations")


class ContactMethod(Base):
    __tablename__ = 'contact_methods'

    id = Column(Integer, primary_key=True, autoincrement=True)
    method = Column(String(100))

    projects = relationship("Project", secondary=project_contact_association, back_populates="contact_methods")


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))
    description = Column(Text)
    start_time = Column(Date)
    end_time = Column(Date)
    hourly_rate = Column(Float)
    participants_needed = Column(Integer)
    repository_url = Column(String(100))
    creator_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))

    creator = relationship("User", back_populates="projects")
    category = relationship("Category", back_populates="projects")
    specializations = relationship("Specialization", secondary=project_specialization_association,
                                   back_populates="projects")
    contact_methods = relationship("ContactMethod", secondary=project_contact_association, back_populates="projects")
    reviews = relationship("ProjectReview", back_populates="project")
    participants = relationship("UserProject", back_populates="project", cascade="all, delete-orphan")

    def add_participant(self, user):
        if len(self.participants) < self.participants_needed:
            new_participant = UserProject(user_id=user.id, project_id=self.id)
            self.participants.append(new_participant)
        else:
            raise ValueError("Cannot add more participants, the project is full.")

    def remove_participant(self, user):
        for participant in self.participants:
            if participant.user_id == user.id:
                self.participants.remove(participant)
                return
        raise ValueError("User is not a participant of this project.")


class UserProject(Base):
    __tablename__ = 'user_projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))

    user = relationship("User")
    project = relationship("Project")


class UserReview(Base):
    __tablename__ = 'user_reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    reviewer_id = Column(Integer, ForeignKey('users.id'))
    reviewed_id = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))
    rating = Column(Integer)
    comment = Column(Text)

    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewed = relationship("User", foreign_keys=[reviewed_id], back_populates="reviews_received")
    project = relationship("Project")


class ProjectReview(Base):
    __tablename__ = 'project_reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    reviewer_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer)
    comment = Column(Text)

    project = relationship("Project", back_populates="reviews")
    reviewer = relationship("User")


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    telegram_id = Column(String(100))
