from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from database import SessionLocal
from security import personel_token_dogrula


router = APIRouter()