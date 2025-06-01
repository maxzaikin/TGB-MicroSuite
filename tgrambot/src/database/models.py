from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    Integer
)

from sqlalchemy.orm import(
    Mapped,
    mapped_column,
    relationship
)

from .db_adapter import Model

class Client(Model):
    __tablename__='clients'

    id: Mapped[int]= mapped_column(primary_key=True)
    t_id: Mapped[int]= mapped_column(Integer, index=True, unique=True)
    name: Mapped[str]= mapped_column(String(255), index=True, nullable=False)
        
    photos: Mapped[list['Photo']]= relationship(cascade='all, delete-orphan',back_populates='client')

    def __repr__(self):
        return f'Client({self.id}, {self.t_id}, "{self.name}")'


class Photo(Model):
    __tablename__='photos'

    id: Mapped[int]= mapped_column(primary_key=True)
    client_id:Mapped[int]= mapped_column(ForeignKey('clients.id', ondelete='CASCADE'), index=True)
    path: Mapped[str]= mapped_column(String(255), nullable=False)
    
    client:Mapped['Client']=relationship(back_populates='photos')
    
    def __repr__(self):
        return f'Photo({self.id}, {self.client_id}, "{self.path}")'