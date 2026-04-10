import pytest
from datetime import date
from django import forms

from ledger.forms import (
    StatusForm,
    OperationTypeForm,
    CategoryForm,
    SubcategoryForm,
    CashflowRecordForm,
)
from ledger.models import Status, OperationType, Category, Subcategory, CashflowRecord


@pytest.mark.django_db
class TestStatusForm:
    """Тесты для формы StatusForm."""

    def test_form_valid(self):
        """Тест валидной формы со всеми обязательными полями."""
        form = StatusForm(data={"name": "Личное"})
        assert form.is_valid(), form.errors

    def test_form_invalid_empty_name(self):
        """Тест формы с пустым именем."""
        form = StatusForm(data={"name": ""})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_saves_status(self):
        """Тест сохранения статуса через форму."""
        form = StatusForm(data={"name": "Налог"})
        assert form.is_valid()
        status = form.save()
        assert status.name == "Налог"
        assert Status.objects.filter(name="Налог").exists()

    def test_widget_placeholder(self):
        """Тест наличия placeholder в виджете."""
        form = StatusForm()
        widget = form.fields["name"].widget
        assert "placeholder" in widget.attrs
        assert widget.attrs["placeholder"] == "Например, Бизнес"

    def test_form_fields(self):
        """Тест наличия всех необходимых полей."""
        form = StatusForm()
        assert "name" in form.fields

    def test_form_duplicate_name(self, status):
        """Тест что форма не позволит создать дубликат имени."""
        form = StatusForm(data={"name": "Бизнес"})
        assert not form.is_valid()


@pytest.mark.django_db
class TestOperationTypeForm:
    """Тесты для формы OperationTypeForm."""

    def test_form_valid(self):
        """Тест валидной формы со всеми обязательными полями."""
        form = OperationTypeForm(data={"name": "Списание"})
        assert form.is_valid(), form.errors

    def test_form_invalid_empty_name(self):
        """Тест формы с пустым именем."""
        form = OperationTypeForm(data={"name": ""})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_saves_operation_type(self):
        """Тест сохранения типа операции через форму."""
        form = OperationTypeForm(data={"name": "Перевод"})
        assert form.is_valid()
        op_type = form.save()
        assert op_type.name == "Перевод"
        assert OperationType.objects.filter(name="Перевод").exists()

    def test_widget_placeholder(self):
        """Тест наличия placeholder в виджете."""
        form = OperationTypeForm()
        widget = form.fields["name"].widget
        assert "placeholder" in widget.attrs
        assert widget.attrs["placeholder"] == "Например, Списание"

    def test_form_fields(self):
        """Тест наличия всех необходимых полей."""
        form = OperationTypeForm()
        assert "name" in form.fields

    def test_form_duplicate_name(self, operation_type):
        """Тест что форма не позволит создать дубликат имени."""
        form = OperationTypeForm(data={"name": "Списание"})
        assert not form.is_valid()


@pytest.mark.django_db
class TestCategoryForm:
    """Тесты для формы CategoryForm."""

    def test_form_valid(self, operation_type):
        """Тест валидной формы со всеми обязательными полями."""
        form = CategoryForm(
            data={"operation_type": operation_type.id, "name": "Маркетинг"}
        )
        assert form.is_valid(), form.errors

    def test_form_invalid_empty_name(self, operation_type):
        """Тест формы с пустым именем."""
        form = CategoryForm(data={"operation_type": operation_type.id, "name": ""})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_invalid_missing_operation_type(self):
        """Тест формы без типа операции."""
        form = CategoryForm(data={"name": "Маркетинг"})
        assert not form.is_valid()
        assert "operation_type" in form.errors

    def test_form_saves_category(self, operation_type):
        """Тест сохранения категории через форму."""
        form = CategoryForm(
            data={"operation_type": operation_type.id, "name": "Маркетинг"}
        )
        assert form.is_valid()
        category = form.save()
        assert category.name == "Маркетинг"
        assert category.operation_type == operation_type
        assert Category.objects.filter(name="Маркетинг").exists()

    def test_widget_placeholder(self):
        """Тест наличия placeholder в виджете."""
        form = CategoryForm()
        widget = form.fields["name"].widget
        assert "placeholder" in widget.attrs
        assert widget.attrs["placeholder"] == "Например, Маркетинг"

    def test_form_fields(self):
        """Тест наличия всех необходимых полей."""
        form = CategoryForm()
        assert "operation_type" in form.fields
        assert "name" in form.fields

    def test_form_duplicate_category_same_operation_type(self, operation_type, category):
        """Тест что форма не позволит создать дубликат категории в рамках одного типа операции."""
        form = CategoryForm(
            data={"operation_type": operation_type.id, "name": "Инфраструктура"}
        )
        assert not form.is_valid()

    def test_form_allows_same_name_different_operation_type(
        self, operation_type
    ):
        """Тест что форма позволит создать категорию с одинаковым именем для разных типов операции."""
        operation_type_2 = OperationType.objects.create(name="Пополнение")
        form1 = CategoryForm(
            data={"operation_type": operation_type.id, "name": "Инфраструктура"}
        )
        assert form1.is_valid()
        form1.save()

        form2 = CategoryForm(
            data={"operation_type": operation_type_2.id, "name": "Инфраструктура"}
        )
        assert form2.is_valid()


@pytest.mark.django_db
class TestSubcategoryForm:
    """Тесты для формы SubcategoryForm."""

    def test_form_valid(self, category):
        """Тест валидной формы со всеми обязательными полями."""
        form = SubcategoryForm(data={"category": category.id, "name": "Proxy"})
        assert form.is_valid(), form.errors

    def test_form_invalid_empty_name(self, category):
        """Тест формы с пустым именем."""
        form = SubcategoryForm(data={"category": category.id, "name": ""})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_invalid_missing_category(self):
        """Тест формы без категории."""
        form = SubcategoryForm(data={"name": "Proxy"})
        assert not form.is_valid()
        assert "category" in form.errors

    def test_form_saves_subcategory(self, category):
        """Тест сохранения подкатегории через форму."""
        form = SubcategoryForm(data={"category": category.id, "name": "Proxy"})
        assert form.is_valid()
        subcategory = form.save()
        assert subcategory.name == "Proxy"
        assert subcategory.category == category
        assert Subcategory.objects.filter(name="Proxy").exists()

    def test_widget_placeholder(self):
        """Тест наличия placeholder в виджете."""
        form = SubcategoryForm()
        widget = form.fields["name"].widget
        assert "placeholder" in widget.attrs
        assert widget.attrs["placeholder"] == "Например, Avito"

    def test_form_fields(self):
        """Тест наличия всех необходимых полей."""
        form = SubcategoryForm()
        assert "category" in form.fields
        assert "name" in form.fields

    def test_form_duplicate_subcategory_same_category(self, category):
        """Тест что форма не позволит создать дубликат подкатегории в рамках одной категории."""
        Subcategory.objects.create(category=category, name="VPS")
        form = SubcategoryForm(data={"category": category.id, "name": "VPS"})
        assert not form.is_valid()

    def test_form_allows_same_name_different_category(self, category, operation_type):
        """Тест что форма позволит создать подкатегорию с одинаковым именем для разных категорий."""
        category2 = Category.objects.create(
            operation_type=operation_type, name="Маркетинг"
        )

        form1 = SubcategoryForm(data={"category": category.id, "name": "VPS"})
        assert form1.is_valid()
        form1.save()

        form2 = SubcategoryForm(data={"category": category2.id, "name": "VPS"})
        assert form2.is_valid()


@pytest.mark.django_db
class TestCashflowRecordForm:
    """Тесты для формы CashflowRecordForm."""

    def test_form_valid(self, status, operation_type, category, subcategory):
        """Тест валидной формы со всеми обязательными полями."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "status": status.id,
                "operation_type": operation_type.id,
                "category": category.id,
                "subcategory": subcategory.id,
                "amount": "150.50",
                "comment": "Тестовый комментарий",
            }
        )
        assert form.is_valid(), form.errors

    def test_form_valid_without_status(self, operation_type, category, subcategory):
        """Тест валидной формы без статуса (поле опционально)."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "status": "",
                "operation_type": operation_type.id,
                "category": category.id,
                "subcategory": subcategory.id,
                "amount": "100.00",
                "comment": "",
            }
        )
        assert form.is_valid(), form.errors

    def test_form_valid_without_comment(
        self, status, operation_type, category, subcategory
    ):
        """Тест валидной формы без комментария (поле опционально)."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "status": status.id,
                "operation_type": operation_type.id,
                "category": category.id,
                "subcategory": subcategory.id,
                "amount": "100.00",
                "comment": "",
            }
        )
        assert form.is_valid(), form.errors

    def test_form_invalid_missing_operation_type(self, status, category, subcategory):
        """Тест формы без типа операции."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "status": status.id,
                "category": category.id,
                "subcategory": subcategory.id,
                "amount": "100.00",
            }
        )
        assert not form.is_valid()
        assert "operation_type" in form.errors

    def test_form_invalid_missing_category(self, status, operation_type, subcategory):
        """Тест формы без категории."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "status": status.id,
                "operation_type": operation_type.id,
                "subcategory": subcategory.id,
                "amount": "100.00",
            }
        )
        assert not form.is_valid()
        assert "category" in form.errors

    def test_form_invalid_missing_subcategory(self, status, operation_type, category):
        """Тест формы без подкатегории."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "status": status.id,
                "operation_type": operation_type.id,
                "category": category.id,
                "amount": "100.00",
            }
        )
        assert not form.is_valid()
        assert "subcategory" in form.errors

    def test_form_invalid_missing_amount(
        self, status, operation_type, category, subcategory
    ):
        """Тест формы без суммы."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "status": status.id,
                "operation_type": operation_type.id,
                "category": category.id,
                "subcategory": subcategory.id,
                "comment": "Тест",
            }
        )
        assert not form.is_valid()
        assert "amount" in form.errors

    def test_form_invalid_missing_record_date(
        self, status, operation_type, category, subcategory
    ):
        """Тест формы без даты записи."""
        form = CashflowRecordForm(
            data={
                "record_date": "",
                "status": status.id,
                "operation_type": operation_type.id,
                "category": category.id,
                "subcategory": subcategory.id,
                "amount": "100.00",
            }
        )
        assert not form.is_valid()
        assert "record_date" in form.errors

    def test_form_saves_cashflow_record(
        self, status, operation_type, category, subcategory
    ):
        """Тест сохранения записи ДДС через форму."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "status": status.id,
                "operation_type": operation_type.id,
                "category": category.id,
                "subcategory": subcategory.id,
                "amount": "150.50",
                "comment": "Тестовая запись",
            }
        )
        assert form.is_valid()
        record = form.save()
        assert record.amount == 150.50
        assert record.status == status
        assert record.operation_type == operation_type
        assert record.category == category
        assert record.subcategory == subcategory
        assert record.comment == "Тестовая запись"

    def test_category_queryset_empty_on_creation(self):
        """Тест на то, что queryset категории пуст при создании новой записи."""
        form = CashflowRecordForm()
        assert form.fields["category"].queryset.count() == 0
        assert form.fields["subcategory"].queryset.count() == 0

    def test_category_queryset_filtered_on_edit(
        self, status, operation_type, category, subcategory
    ):
        """Тест фильтрации категорий при редактировании существующей записи."""
        record = CashflowRecord.objects.create(
            record_date=date.today(),
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=100.00,
        )

        form = CashflowRecordForm(instance=record)

        assert form.fields["category"].queryset.filter(id=category.id).exists()
        assert form.fields["subcategory"].queryset.filter(id=subcategory.id).exists()

    def test_category_queryset_filtered_by_operation_type_on_form_data(
        self, operation_type, category
    ):
        """Тест фильтрации категорий по типу операции из POST данных."""
        operation_type_2 = OperationType.objects.create(name="Пополнение")
        category2 = Category.objects.create(
            operation_type=operation_type_2, name="Маркетинг"
        )

        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "operation_type": operation_type.id,
            }
        )

        queryset_categories = list(form.fields["category"].queryset)
        assert category in queryset_categories
        assert category2 not in queryset_categories

    def test_subcategory_queryset_filtered_by_category_on_form_data(self, category, subcategory):
        """Тест фильтрации подкатегорий по категории из POST данных."""

        operation_type2 = OperationType.objects.create(name="Другой тип")
        category2 = Category.objects.create(
            operation_type=operation_type2, name="Другая категория"
        )
        subcategory2 = Subcategory.objects.create(
            category=category2, name="Другая подкатегория"
        )

        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "category": category.id,
            }
        )

        queryset_subcategories = list(form.fields["subcategory"].queryset)
        assert subcategory in queryset_subcategories
        assert subcategory2 not in queryset_subcategories

    def test_status_field_not_required(self):
        """Тест на то, что поле статуса не является обязательным."""
        form = CashflowRecordForm()
        assert not form.fields["status"].required

    def test_status_field_empty_label(self):
        """Тест наличия пустой подписи для статуса."""
        form = CashflowRecordForm()
        assert form.fields["status"].empty_label == "Без статуса"

    def test_date_widget_type(self):
        """Тест на то, что для даты используется date input."""
        form = CashflowRecordForm()
        widget = form.fields["record_date"].widget
        assert widget.input_type == "date"

    def test_comment_widget_textarea(self):
        """Тест на то, что для комментария используется textarea с 3 строками."""
        form = CashflowRecordForm()
        widget = form.fields["comment"].widget
        assert isinstance(widget, forms.Textarea)
        assert widget.attrs.get("rows") == 3

    def test_form_fields(self):
        """Тест наличия всех необходимых полей."""
        form = CashflowRecordForm()
        expected_fields = [
            "record_date",
            "status",
            "operation_type",
            "category",
            "subcategory",
            "amount",
            "comment",
        ]
        for field_name in expected_fields:
            assert field_name in form.fields

    def test_form_invalid_malformed_amount(
        self, status, operation_type, category, subcategory
    ):
        """Тест валидации некорректной суммы."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "status": status.id,
                "operation_type": operation_type.id,
                "category": category.id,
                "subcategory": subcategory.id,
                "amount": "не число",
                "comment": "Некорректная сумма",
            }
        )
        assert not form.is_valid()
        assert "amount" in form.errors

    def test_form_handles_invalid_operation_type_id(self):
        """Тест обработки некорректного ID типа операции в POST данных."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "operation_type": "invalid_id",
            }
        )

        assert not form.is_valid()

    def test_form_handles_invalid_category_id(self):
        """Тест обработки некорректного ID категории в POST данных."""
        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "category": "invalid_id",
            }
        )

        assert not form.is_valid()

    def test_category_queryset_ordered_by_name(self, operation_type):
        """Тест на то, что категории сортируются по имени."""
        category_b = Category.objects.create(
            operation_type=operation_type, name="Б Категория"
        )
        category_a = Category.objects.create(
            operation_type=operation_type, name="А Категория"
        )
        category_c = Category.objects.create(
            operation_type=operation_type, name="В Категория"
        )

        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "operation_type": operation_type.id,
            }
        )

        queryset_list = list(form.fields["category"].queryset)
        assert queryset_list == [category_a, category_b, category_c]

    def test_subcategory_queryset_ordered_by_name(self, category):
        """Тест на то, что подкатегории сортируются по имени."""
        subcategory_b = Subcategory.objects.create(
            category=category, name="Б Подкатегория"
        )
        subcategory_a = Subcategory.objects.create(
            category=category, name="А Подкатегория"
        )
        subcategory_c = Subcategory.objects.create(
            category=category, name="В Подкатегория"
        )

        form = CashflowRecordForm(
            data={
                "record_date": str(date.today()),
                "category": category.id,
            }
        )

        queryset_list = list(form.fields["subcategory"].queryset)
        assert queryset_list == [subcategory_a, subcategory_b, subcategory_c]
