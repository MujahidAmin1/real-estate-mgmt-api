import hashlib, hmac, json, uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from app.db.database import get_db
from app.modules.payments.model.payment_model import Payment, PaymentStatus
from app.modules.payments.paymenr_schema import PaymentInitializeResponse, PaymentRead
from app.modules.properties.property_models import Property
from app.modules.users.auth_models import User
from app.services.payments import initialize_transaction, verify_transaction
from app.utils.dependencies import get_current_user
from app.utils.exceptions import AppError
from sqlalchemy.orm import Session
from app.core.config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])
    
@router.post("/initialize", status_code=201, response_model=PaymentInitializeResponse)
async def initialize_payment(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise AppError(404, "Property not found")

    reference = f"RE-{uuid.uuid7()}"  # unique per transaction

    paystack_data = await initialize_transaction(
        email=current_user.email,
        amount_naira=property.price,
        reference=reference,
        metadata={"property_id": str(property_id), "user_id": str(current_user.id)},
    )

    db.add(Payment(
        user_id=current_user.id,
        property_id=property_id,
        reference=reference,
        amount=property.price,
        currency=property.currency,
    ))
    db.commit()

    # return access_code to mobile — this is what Flutter uses to open Paystack checkout
    return {"access_code": paystack_data["access_code"], "reference": reference}


@router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()

    # 1. verify the webhook is actually from Paystack
    signature = request.headers.get("x-paystack-signature")
    expected = hmac.new(
        settings.paystack_secret_key.encode(),
        body,
        hashlib.sha512
    ).hexdigest()

    if signature != expected:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event = json.loads(body)

    if event.get("event") != "charge.success":
        return {"status": "ignored"}  # only handle successful charges

    reference = event["data"]["reference"]

    payment = db.query(Payment).filter(Payment.reference == reference).first()
    if not payment or payment.status == PaymentStatus.success:
        return {"status": "ok"}  # already handled or doesn't exist

    # 2. verify with Paystack directly — never trust webhook data alone
    verified = await verify_transaction(reference)

    if verified["status"] == "success" and verified["amount"] == int(payment.amount * 100):
        payment.status = PaymentStatus.success
        payment.paystack_data = json.dumps(verified)
        db.commit()
        # here you can also trigger: send confirmation email, notify agent, etc.

    return {"status": "ok"}  # always return 200 to Paystack, even on failure


@router.get("/{reference}", response_model=PaymentRead)
async def get_payment_status(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = db.query(Payment).filter(
        Payment.reference == reference,
        Payment.user_id == current_user.id,
    ).first()
    if not payment:
        raise AppError(404, "Payment not found")
    return payment