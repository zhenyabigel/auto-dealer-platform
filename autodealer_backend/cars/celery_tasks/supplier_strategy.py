# from django.db import models
# from django.utils import timezone
# from decimal import Decimal
# import logging
# from ..models import Supplier, Promotion
# from ..services.supplier_api import SupplierAPIService
#
# logger = logging.getLogger(__name__)
#
# class SupplierStrategy:
#     def __init__(self):
#         self.api_service = SupplierAPIService()
#
#     def update_supplier(self, supplier):
#         """
#         Обновляет данные поставщика через API
#         Возвращает словарь с изменениями или None
#         """
#         try:
#             api_data = self.api_service.get_supplier_data(supplier.id)
#             changes = {}
#
#             # Проверка скидки
#             new_discount = Decimal(api_data.get('discount', 0))
#             if new_discount != supplier.discount_for_dealers:
#                 changes['discount_for_dealers'] = new_discount
#
#             # Проверка активности
#             if 'is_active' in api_data and api_data['is_active'] != supplier.is_active:
#                 changes['is_active'] = api_data['is_active']
#
#             return changes if changes else None
#
#         except Exception as e:
#             logger.error(f"Error updating supplier {supplier.id}: {e}")
#             return None
#
#     def check_supplier_activity(self, supplier):
#         """
#         Проверяет активность поставщика на основе:
#         - Данных API
#         - Наличия актуальных предложений
#         - Последней активности
#         """
#         # Проверка через API
#         api_data = self.api_service.get_supplier_data(supplier.id)
#         if not api_data.get('is_active', True):
#             return False
#
#         # Проверка наличия актуальных автомобилей
#         has_active_cars = supplier.cars.filter(
#             is_active=True,
#             created_at__gte=timezone.now() - timezone.timedelta(days=30)
#         ).exists()
#
#         return has_active_cars
#
#     def get_best_suppliers_for_brand(self, brand, max_price=None):
#         """
#         Возвращает QuerySet поставщиков для конкретного бренда,
#         отсортированный по выгодности предложений
#         """
#         queryset = (
#             Supplier.objects
#             .filter(
#                 cars__brand=brand,
#                 cars__is_active=True,
#                 is_active=True
#             )
#             .annotate(
#                 min_price=models.Min('cars__price'),
#                 avg_rating=models.Avg('cars__rating'),
#                 discount_price=models.F('min_price') *
#                                 (100 - models.F('discount_for_dealers')) / 100
#             )
#             .order_by('discount_price', '-avg_rating')
#         )
#
#         if max_price:
#             queryset = queryset.filter(discount_price__lte=max_price)
#
#         return queryset
#
#     def update_all_suppliers(self):
#         """
#         Массовое обновление всех поставщиков
#         Возвращает статистику
#         """
#         updated = 0
#         deactivated = 0
#         suppliers = Supplier.objects.filter(is_active=True)
#
#         for supplier in suppliers:
#             changes = self.update_supplier(supplier)
#             if changes:
#                 Supplier.objects.filter(pk=supplier.pk).update(**changes)
#                 updated += 1
#
#             # Автоматическая деактивация неактивных
#             if not self.check_supplier_activity(supplier):
#                 Supplier.objects.filter(pk=supplier.pk).update(is_active=False)
#                 deactivated += 1
#
#         return {
#             'total': suppliers.count(),
#             'updated': updated,
#             'deactivated': deactivated
#         }
