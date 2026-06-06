from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models.offer import Offer
from ..schemas.offer import OfferCreate, OfferRead, OfferStatusUpdate

router = APIRouter(prefix="/offers", tags=["offers"])


@router.post("", response_model=OfferRead)
async def create_offer(payload: OfferCreate, session: AsyncSession = Depends(get_session)):
    offer = Offer(**payload.model_dump())
    session.add(offer)
    await session.commit()
    await session.refresh(offer)
    return offer


@router.get("", response_model=list[OfferRead])
async def list_offers(session: AsyncSession = Depends(get_session)):
    return list(await session.scalars(select(Offer).order_by(Offer.created_at.desc())))


@router.get("/{offer_id}", response_model=OfferRead)
async def get_offer(offer_id: UUID, session: AsyncSession = Depends(get_session)):
    offer = await session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


@router.patch("/{offer_id}/status", response_model=OfferRead)
async def update_offer_status(offer_id: UUID, payload: OfferStatusUpdate, session: AsyncSession = Depends(get_session)):
    offer = await session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    offer.status = payload.status
    await session.commit()
    await session.refresh(offer)
    return offer
