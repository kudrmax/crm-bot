import asyncio
import datetime
import difflib
from typing import List, Dict, Tuple
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.contacts.models import MContact
from src.api.contacts.schemas import SContactCreate, SContactUpdate
from src.api.dao_base import DAO
from src.database import get_db


class DAOContact(DAO):
    model = MContact

    async def create(self, s_contact_create: SContactCreate) -> MContact:
        m_contact = MContact(**s_contact_create.model_dump(exclude_unset=True))
        try:
            self.db.add(m_contact)
            await self.db.flush()
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(status_code=409, detail=f'Конаткт с именем {s_contact_create.name} уже существует')
        else:
            await self.db.commit()
            return m_contact

    async def delete(self, id: UUID) -> MContact | None:
        m_contact = await self.get_one_or_none_by_id(id)
        if not m_contact:
            return None
        await self.db.delete(m_contact)
        await self.db.commit()
        return m_contact

    async def update(self, id: UUID, update_contact: SContactUpdate) -> MContact:
        if update_contact.name:
            if await self.get_one_or_none_with_filter(name=update_contact.name):
                raise HTTPException(status_code=409, detail=f'Конаткт с именем {update_contact.name} уже существует')
        m_contact = await self.get_one_by_id(id)
        for key, val in update_contact.model_dump(exclude_unset=True).items():
            setattr(m_contact, key, val)
        await self.db.commit()
        return m_contact

    async def search(self, name: str, name_count: int = 3) -> List[MContact]:
        # m_contact = await self.get_one_or_none_with_filter(name=name)
        # if m_contact:
        #     return [m_contact]
        m_contacts = await self.get_all()
        names = [contact.name.lower() for contact in m_contacts]
        close_names = difflib.get_close_matches(name.lower(), names, n=name_count)
        return [contact for contact in m_contacts if contact.name.lower() in close_names]
