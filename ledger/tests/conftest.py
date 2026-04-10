import pytest

from ledger.models import Status, OperationType, Category, Subcategory


@pytest.fixture
def status():
    """Фикстура для создания статуса."""
    return Status.objects.create(name="Бизнес")


@pytest.fixture
def operation_type():
    """Фикстура для создания типа операции."""
    return OperationType.objects.create(name="Списание")


@pytest.fixture
def category(operation_type):
    """Фикстура для создания категории."""
    return Category.objects.create(operation_type=operation_type, name="Инфраструктура")


@pytest.fixture
def subcategory(category):
    """Фикстура для создания подкатегории."""
    return Subcategory.objects.create(category=category, name="VPS")