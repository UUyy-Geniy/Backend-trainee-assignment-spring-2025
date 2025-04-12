from fastapi import APIRouter, Depends, status
from uuid import UUID
from schemas.product import ProductResponse, ProductRequest
from api.deps import get_product_service, get_current_employee
from services.products import ProductService

router = APIRouter(prefix="/products")

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductRequest,
    employee: dict = Depends(get_current_employee),
    service: ProductService = Depends(get_product_service)
):
    return await service.add_product(product.pvz_id, product.type)