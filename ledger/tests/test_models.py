import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from ledger.models import Status, OperationType, Category, Subcategory, CashflowRecord


@pytest.mark.django_db
class TestStatus:
    """Тесты для модели Status."""

    def test_create_status(self):
        """Тест создания статуса."""
        status = Status.objects.create(name="Личное")
        assert status.name == "Личное"
        assert str(status) == "Личное"

    def test_unique_name(self):
        """Тест уникальности имени статуса."""
        Status.objects.create(name="Бизнес")
        with pytest.raises(IntegrityError):
            Status.objects.create(name="Бизнес")

    def test_ordering(self):
        """Тест сортировки по имени."""
        status1 = Status.objects.create(name="Бизнес")
        status2 = Status.objects.create(name="Личное")
        statuses = list(Status.objects.all())
        assert statuses == [status1, status2]


@pytest.mark.django_db
class TestOperationType:
    """Тесты для модели OperationType."""

    def test_create_operation_type(self):
        """Тест создания типа операции."""
        op_type = OperationType.objects.create(name="Пополнение")
        assert op_type.name == "Пополнение"
        assert str(op_type) == "Пополнение"

    def test_unique_name(self):
        """Тест уникальности имени типа операции."""
        OperationType.objects.create(name="Списание")
        with pytest.raises(IntegrityError):
            OperationType.objects.create(name="Списание")

    def test_ordering(self):
        """Тест сортировки по имени."""
        op_type1 = OperationType.objects.create(name="Пополнение")
        op_type2 = OperationType.objects.create(name="Списание")
        op_types = list(OperationType.objects.all())
        assert op_types == [op_type1, op_type2]


@pytest.mark.django_db
class TestCategory:
    """Тесты для модели Category."""

    def test_create_category(self, operation_type):
        """Тест создания категории."""
        category = Category.objects.create(
            operation_type=operation_type, name="Маркетинг"
        )
        assert category.name == "Маркетинг"
        assert category.operation_type == operation_type
        assert str(category) == "Маркетинг (Списание)"

    def test_unique_constraint(self, operation_type):
        """Тест уникальности комбинации (operation_type, name)."""
        Category.objects.create(operation_type=operation_type, name="Инфраструктура")
        with pytest.raises(IntegrityError):
            Category.objects.create(
                operation_type=operation_type, name="Инфраструктура"
            )

    def test_ordering(self, operation_type):
        """Тест сортировки по имени."""
        category1 = Category.objects.create(
            operation_type=operation_type, name="Инфраструктура"
        )
        category2 = Category.objects.create(
            operation_type=operation_type, name="Маркетинг"
        )
        categories = list(Category.objects.all())
        assert categories == [category1, category2]


@pytest.mark.django_db
class TestSubcategory:
    """Тесты для модели Subcategory."""

    def test_create_subcategory(self, category):
        """Тест создания подкатегории."""
        subcategory = Subcategory.objects.create(category=category, name="Proxy")
        assert subcategory.name == "Proxy"
        assert subcategory.category == category
        assert str(subcategory) == "Proxy (Инфраструктура)"

    def test_unique_constraint(self, category):
        """Тест уникальности комбинации (category, name)."""
        Subcategory.objects.create(category=category, name="VPS")
        with pytest.raises(IntegrityError):
            Subcategory.objects.create(category=category, name="VPS")

    def test_ordering(self, category):
        """Тест сортировки по имени."""
        subcategory1 = Subcategory.objects.create(category=category, name="Proxy")
        subcategory2 = Subcategory.objects.create(category=category, name="VPS")
        subcategories = list(Subcategory.objects.all())
        assert subcategories == [subcategory1, subcategory2]


@pytest.mark.django_db
class TestCashflowRecord:
    """Тесты для модели CashflowRecord."""

    def test_create_cashflow_record(
        self, status, operation_type, category, subcategory
    ):
        """Тест создания записи ДДС."""
        record = CashflowRecord.objects.create(
            record_date=date.today(),
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=150.50,
            comment="Оплата за VPS сервер",
        )
        assert record.amount == 150.50
        assert record.status == status
        assert record.operation_type == operation_type
        assert record.category == category
        assert record.subcategory == subcategory
        assert str(record) == f"{date.today()} 150.50 ₽"

    def test_clean_valid(self, status, operation_type, category, subcategory):
        """Тест валидации при корректных данных."""
        record = CashflowRecord(
            record_date=date.today(),
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=100.00,
        )
        record.full_clean()

    def test_clean_invalid_category_operation_type(
        self, status, operation_type, category, subcategory
    ):
        """Тест валидации: категория не соответствует типу операции."""
        op_type2 = OperationType.objects.create(name="Пополнение")
        category_wrong = Category.objects.create(
            operation_type=op_type2, name="Инфраструктура"
        )
        record = CashflowRecord(
            record_date=date.today(),
            status=status,
            operation_type=operation_type,
            category=category_wrong,
            subcategory=subcategory,
            amount=100.00,
        )
        with pytest.raises(ValidationError) as exc_info:
            record.full_clean()
        assert "category" in exc_info.value.message_dict

    def test_clean_invalid_subcategory_category(
        self, status, operation_type, category, subcategory
    ):
        """Тест валидации: подкатегория не соответствует категории."""
        category2 = Category.objects.create(
            operation_type=operation_type, name="Маркетинг"
        )
        subcategory_wrong = Subcategory.objects.create(category=category2, name="VPS")
        record = CashflowRecord(
            record_date=date.today(),
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory_wrong,
            amount=100.00,
        )
        with pytest.raises(ValidationError) as exc_info:
            record.full_clean()
        assert "subcategory" in exc_info.value.message_dict

    def test_optional_status(self, operation_type, category, subcategory):
        """Тест создания записи без статуса."""
        record = CashflowRecord.objects.create(
            record_date=date.today(),
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=200.00,
        )
        assert record.status is None

    def test_ordering_by_record_date(
        self, status, operation_type, category, subcategory
    ):
        """Тест сортировки по record_date (новые даты первыми)."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        record_old = CashflowRecord.objects.create(
            record_date=yesterday,
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=100.00,
        )
        record_new = CashflowRecord.objects.create(
            record_date=today,
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=200.00,
        )

        records = list(CashflowRecord.objects.all())
        assert records[0] == record_new
        assert records[1] == record_old

    def test_ordering_by_created_at(
        self, status, operation_type, category, subcategory
    ):
        """Тест сортировки по created_at (новые записи первыми при одинаковой дате)."""
        today = date.today()

        record_old = CashflowRecord.objects.create(
            record_date=today,
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=100.00,
        )
        record_new = CashflowRecord.objects.create(
            record_date=today,
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=200.00,
        )

        records = list(CashflowRecord.objects.all())
        assert records[0] == record_new
        assert records[1] == record_old

    def test_ordering_priority_record_date_over_created_at(self, status, operation_type, category, subcategory):
        """Тест приоритетности сортировки: record_date имеет приоритет над created_at."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        record_today = CashflowRecord.objects.create(
            record_date=today,
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=200.00,
        )

        record_yesterday = CashflowRecord.objects.create(
            record_date=yesterday,
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=100.00,
        )

        records = list(CashflowRecord.objects.all())
        assert records[0] == record_today
        assert records[1] == record_yesterday
