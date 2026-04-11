from django.urls import path

from .views import (
    CashflowRecordListView,
    CashflowRecordCreateView,
    CashflowRecordUpdateView,
    CashflowRecordDeleteView,
    StatusCreateView,
    StatusUpdateView,
    StatusDeleteView,
    OperationTypeCreateView,
    OperationTypeUpdateView,
    OperationTypeDeleteView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    SubcategoryCreateView,
    SubcategoryUpdateView,
    SubcategoryDeleteView,
    load_categories,
    load_subcategories,
    ReferencesListView,
)

urlpatterns = [
    path("", CashflowRecordListView.as_view(), name="cashflow_list"),
    path("references/", ReferencesListView.as_view(), name="references_list"),
    path(
        "cashflow/create/", CashflowRecordCreateView.as_view(), name="cashflow_create"
    ),
    path(
        "cashflow/<int:pk>/edit/",
        CashflowRecordUpdateView.as_view(),
        name="cashflow_update",
    ),
    path(
        "cashflow/<int:pk>/delete/",
        CashflowRecordDeleteView.as_view(),
        name="cashflow_delete",
    ),
    path("statuses/create/", StatusCreateView.as_view(), name="status_create"),
    path("statuses/<int:pk>/edit/", StatusUpdateView.as_view(), name="status_update"),
    path("statuses/<int:pk>/delete/", StatusDeleteView.as_view(), name="status_delete"),
    path(
        "operation-types/create/",
        OperationTypeCreateView.as_view(),
        name="operation_type_create",
    ),
    path(
        "operation-types/<int:pk>/edit/",
        OperationTypeUpdateView.as_view(),
        name="operation_type_update",
    ),
    path(
        "operation-types/<int:pk>/delete/",
        OperationTypeDeleteView.as_view(),
        name="operation_type_delete",
    ),
    path("categories/create/", CategoryCreateView.as_view(), name="category_create"),
    path(
        "categories/<int:pk>/edit/",
        CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "categories/<int:pk>/delete/",
        CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    path(
        "subcategories/create/",
        SubcategoryCreateView.as_view(),
        name="subcategory_create",
    ),
    path(
        "subcategories/<int:pk>/edit/",
        SubcategoryUpdateView.as_view(),
        name="subcategory_update",
    ),
    path(
        "subcategories/<int:pk>/delete/",
        SubcategoryDeleteView.as_view(),
        name="subcategory_delete",
    ),
    path("ajax/load-categories/", load_categories, name="ajax_load_categories"),
    path(
        "ajax/load-subcategories/", load_subcategories, name="ajax_load_subcategories"
    ),
]
