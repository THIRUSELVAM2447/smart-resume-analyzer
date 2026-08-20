from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.portfolio import PortfolioGenerate, PortfolioResponse, PortfolioUpdate, PublicPortfolioResponse
from app.services.portfolio_service import PortfolioService


router = APIRouter(prefix="/api/portfolios", tags=["Portfolio"])
portfolio_service = PortfolioService()


@router.get("/public/{slug}", response_model=PublicPortfolioResponse)
def get_public_portfolio(slug: str, db: Session = Depends(get_db)) -> Portfolio:
    portfolio = portfolio_service.get_public_portfolio(db, slug)
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Published portfolio not found.")
    return portfolio


@router.get("", response_model=PortfolioResponse)
def get_my_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Portfolio:
    portfolio = portfolio_service.get_user_portfolio(db, current_user)
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found. Generate one from a processed resume.")
    return portfolio


@router.post("/generate", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def generate_portfolio(data: PortfolioGenerate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Portfolio:
    portfolio = portfolio_service.generate_from_resume_version(db, current_user, data.resume_version_id)
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processed resume version not found.")
    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(portfolio_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Portfolio:
    portfolio = portfolio_service.get_portfolio(db, current_user, portfolio_id)
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found.")
    return portfolio


@router.patch("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(portfolio_id: int, data: PortfolioUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Portfolio:
    portfolio = portfolio_service.update_portfolio(db, current_user, portfolio_id, data)
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found.")
    return portfolio
