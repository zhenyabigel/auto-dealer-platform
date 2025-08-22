from autodealer_backend.dealers.permissions.dealer_permissions import (
    IsAdminOrDealerOwner,
)
from autodealer_backend.dealers.permissions.dealer_stock_permissions import (
    IsDealerStockOwner,
)

__all__ = ["IsAdminOrDealerOwner", "IsDealerStockOwner"]
