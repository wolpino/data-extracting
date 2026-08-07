from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from data_extracting_backend.activity import log_activity
from data_extracting_backend.db import get_db
from data_extracting_backend.models import Order
from data_extracting_backend.schemas import OrderCreate, OrderPatch, OrderRead, OrderUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


def _touch(order: Order) -> None:
    order.updated_at = datetime.now(timezone.utc)


@router.get("", response_model=list[OrderRead])
def list_orders(request: Request, db: Session = Depends(get_db)) -> list[Order]:
    orders = list(db.scalars(select(Order).order_by(Order.id)).all())
    log_activity(
        db,
        action="list",
        entity_type="order",
        method=request.method,
        path=str(request.url.path),
        detail=f"count={len(orders)}",
    )
    db.commit()
    return orders


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate, request: Request, db: Session = Depends(get_db)
) -> Order:
    order = Order(
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=payload.date_of_birth,
        source_filename=payload.source_filename,
    )
    db.add(order)
    db.flush()
    log_activity(
        db,
        action="create",
        entity_type="order",
        entity_id=order.id,
        method=request.method,
        path=str(request.url.path),
    )
    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int, request: Request, db: Session = Depends(get_db)
) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    log_activity(
        db,
        action="get",
        entity_type="order",
        entity_id=order.id,
        method=request.method,
        path=str(request.url.path),
    )
    db.commit()
    return order


@router.put("/{order_id}", response_model=OrderRead)
def replace_order(
    order_id: int,
    payload: OrderUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order.first_name = payload.first_name
    order.last_name = payload.last_name
    order.date_of_birth = payload.date_of_birth
    order.source_filename = payload.source_filename
    _touch(order)
    log_activity(
        db,
        action="update",
        entity_type="order",
        entity_id=order.id,
        method=request.method,
        path=str(request.url.path),
        detail="put",
    )
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}", response_model=OrderRead)
def patch_order(
    order_id: int,
    payload: OrderPatch,
    request: Request,
    db: Session = Depends(get_db),
) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field is required",
        )

    for key, value in data.items():
        setattr(order, key, value)
    _touch(order)

    log_activity(
        db,
        action="update",
        entity_type="order",
        entity_id=order.id,
        method=request.method,
        path=str(request.url.path),
        detail="patch",
    )
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int, request: Request, db: Session = Depends(get_db)
) -> None:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    log_activity(
        db,
        action="delete",
        entity_type="order",
        entity_id=order.id,
        method=request.method,
        path=str(request.url.path),
    )
    db.delete(order)
    db.commit()
