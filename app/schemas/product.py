from pydantic import BaseModel


class ProductCreate(BaseModel):
    product_name: str
    store_name: str
    product_url: str
    price: float | None = None


class ProductResponse(BaseModel):
    id: int
    product_name: str
    store_name: str
    product_url: str
    price: float | None
    in_stock: bool
    is_active: bool

    class Config:
        from_attributes = True
        

class ProductUpdate(BaseModel):
    product_name: str
    store_name: str
    product_url: str
    price: float
    in_stock: bool
    is_active: bool        