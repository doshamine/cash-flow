from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from ledger.models import CashflowRecord, Category, OperationType, Status, Subcategory


def _messages(response):
    """Вспомогательная функция: возвращает список текстов сообщений из response."""
    return [m.message for m in get_messages(response.wsgi_request)]


def _post_follow(client, url_name, data=None, pk=None):
    """Вспомогательная функция: отправляет POST и следует за редиректами."""
    kwargs = {"pk": pk} if pk is not None else None
    url = reverse(url_name, kwargs=kwargs)
    return client.post(url, data=data or {}, follow=True)


@pytest.mark.django_db
class TestReferenceUpdateViews:
    """Тесты для update-view справочников."""

    @pytest.mark.parametrize(
        "fixture_name,url_name,new_name,payload_builder,success_message",
        [
            (
                "status",
                "status_update",
                "Обновленный статус",
                lambda obj, name: {"name": name},
                "Статус успешно обновлен.",
            ),
            (
                "operation_type",
                "operation_type_update",
                "Переименованный тип операции",
                lambda obj, name: {"name": name},
                "Тип операции успешно обновлен.",
            ),
            (
                "category",
                "category_update",
                "Переименованная категория",
                lambda obj, name: {
                    "operation_type": obj.operation_type_id,
                    "name": name,
                },
                "Категория успешно обновлена.",
            ),
            (
                "subcategory",
                "subcategory_update",
                "Переименованная подкатегория",
                lambda obj, name: {
                    "category": obj.category_id,
                    "name": name,
                },
                "Подкатегория успешно обновлена.",
            ),
        ],
        ids=[
            "status_update",
            "operation_type_update",
            "category_update",
            "subcategory_update",
        ],
    )
    def test_update_views(
        self,
        client,
        request,
        fixture_name,
        url_name,
        new_name,
        payload_builder,
        success_message,
    ):
        """Тест на то, что update-view обновляет name и показывает сообщение об успехе."""
        obj = request.getfixturevalue(fixture_name)
        payload = payload_builder(obj, new_name)

        response = _post_follow(client, url_name, data=payload, pk=obj.pk)
        obj.refresh_from_db()

        assert response.status_code == 200
        assert obj.name == new_name
        assert success_message in _messages(response)


@pytest.mark.django_db
class TestReferenceDeleteViews:
    """Тесты для delete-view справочников и записей о ДДС."""

    @pytest.mark.parametrize(
        "fixture_name,url_name,model_class,success_message",
        [
            ("status", "status_delete", Status, "Статус успешно удален."),
            (
                "operation_type",
                "operation_type_delete",
                OperationType,
                "Тип операции успешно удален.",
            ),
            ("category", "category_delete", Category, "Категория успешно удалена."),
            (
                "subcategory",
                "subcategory_delete",
                Subcategory,
                "Подкатегория успешно удалена.",
            ),
            (
                "cashflow_record",
                "cashflow_delete",
                CashflowRecord,
                "Запись успешно удалена.",
            ),
        ],
        ids=[
            "status_delete",
            "operation_type_delete",
            "category_delete",
            "subcategory_delete",
            "record_delete",
        ],
    )
    def test_delete_views(
        self,
        client,
        request,
        fixture_name,
        url_name,
        model_class,
        success_message,
    ):
        """Тест на то, что delete-view удаляет объект и показывает сообщение об успехе."""
        obj = request.getfixturevalue(fixture_name)

        response = _post_follow(client, url_name, pk=obj.pk)

        assert response.status_code == 200
        assert not model_class.objects.filter(pk=obj.pk).exists()
        assert success_message in _messages(response)


@pytest.mark.django_db
class TestReferenceCreateViews:
    """Тесты для create-view справочников и записей о ДДС."""

    @pytest.mark.parametrize(
        "url_name,payload_builder,model_class,lookup,success_message",
        [
            (
                "status_create",
                lambda request: {"name": "Новый статус"},
                Status,
                {"name": "Новый статус"},
                "Статус успешно создан.",
            ),
            (
                "operation_type_create",
                lambda request: {"name": "Новый тип операции"},
                OperationType,
                {"name": "Новый тип операции"},
                "Тип операции успешно создан.",
            ),
            (
                "category_create",
                lambda request: {
                    "operation_type": request.getfixturevalue("operation_type").id,
                    "name": "Новая категория",
                },
                Category,
                {"name": "Новая категория"},
                "Категория успешно создана.",
            ),
            (
                "subcategory_create",
                lambda request: {
                    "category": request.getfixturevalue("category").id,
                    "name": "Новая подкатегория",
                },
                Subcategory,
                {"name": "Новая подкатегория"},
                "Подкатегория успешно создана.",
            ),
            (
                "cashflow_create",
                lambda request: {
                    "record_date": str(date.today()),
                    "status": request.getfixturevalue("status").id,
                    "operation_type": request.getfixturevalue("operation_type").id,
                    "category": request.getfixturevalue("category").id,
                    "subcategory": request.getfixturevalue("subcategory").id,
                    "amount": "150.50",
                    "comment": "Новая запись",
                },
                CashflowRecord,
                {"comment": "Новая запись"},
                "Запись успешно создана.",
            ),
        ],
        ids=[
            "status_create",
            "operation_type_create",
            "category_create",
            "subcategory_create",
            "record_create",
        ],
    )
    def test_create_views(
        self,
        client,
        request,
        url_name,
        payload_builder,
        model_class,
        lookup,
        success_message,
    ):
        """Тест на то, что create-view создает объект и показывает сообщение об успехе."""
        payload = payload_builder(request)

        response = _post_follow(client, url_name, data=payload)

        assert response.status_code == 200
        assert model_class.objects.filter(**lookup).exists()
        assert success_message in _messages(response)


@pytest.mark.django_db
class TestCashflowRecordViews:
    """Тесты для view записей о ДДС: CRUD, фильтрация и контекст."""

    def test_list_view_ok(self, client, cashflow_record):
        """Тест на то, что list-view возвращает 200 и содержит запись в контексте."""
        response = client.get(reverse("cashflow_list"))

        assert response.status_code == 200
        assert cashflow_record in list(response.context["records"])

    def test_create_view_creates_record_and_shows_message(
        self, client, status, operation_type, category, subcategory
    ):
        """Тест на то, что create-view создает запись и показывает сообщение об успехе."""
        payload = {
            "record_date": str(date.today()),
            "status": status.id,
            "operation_type": operation_type.id,
            "category": category.id,
            "subcategory": subcategory.id,
            "amount": "150.50",
            "comment": "Новая запись",
        }

        response = _post_follow(client, "cashflow_create", data=payload)

        assert response.status_code == 200
        assert CashflowRecord.objects.filter(comment="Новая запись").exists()
        assert "Запись успешно создана." in _messages(response)

    def test_delete_view_deletes_record_and_shows_message(self, client, cashflow_record):
        """Тест на то, что delete-view удаляет запись и показывает сообщение об успехе."""
        response = _post_follow(client, "cashflow_delete", pk=cashflow_record.pk)

        assert response.status_code == 200
        assert not CashflowRecord.objects.filter(pk=cashflow_record.pk).exists()
        assert "Запись успешно удалена." in _messages(response)

    @pytest.mark.parametrize(
        "filter_param,related_fixture_name,related_model,create_kwargs",
        [
            ("status", "status", Status, lambda obj: {"status": obj}),
            (
                "operation_type",
                "operation_type",
                OperationType,
                lambda obj: {"operation_type": obj},
            ),
            ("category", "category", Category, lambda obj: {"category": obj}),
            ("subcategory", "subcategory", Subcategory, lambda obj: {"subcategory": obj}),
        ],
        ids=["by_status", "by_operation_type", "by_category", "by_subcategory"],
    )
    def test_list_view_fk_filters(
        self,
        client,
        request,
        filter_param,
        related_fixture_name,
        related_model,
        create_kwargs,
        status,
        operation_type,
        category,
        subcategory,
    ):
        """Тест на то, что list-view фильтрует записи по каждому внешнему ключу."""
        base_kwargs = {
            "record_date": date.today(),
            "status": status,
            "operation_type": operation_type,
            "category": category,
            "subcategory": subcategory,
            "amount": Decimal("100.00"),
        }

        target_rel = request.getfixturevalue(related_fixture_name)
        other_rel = related_model.objects.exclude(pk=target_rel.pk).first()
        if other_rel is None:
            if related_model is Status:
                other_rel = Status.objects.create(name="Другой статус")
            elif related_model is OperationType:
                other_rel = OperationType.objects.create(name="Другой тип")
            elif related_model is Category:
                op = request.getfixturevalue("operation_type")
                other_rel = Category.objects.create(
                    operation_type=op, name="Другая категория"
                )
            else:
                cat = request.getfixturevalue("category")
                other_rel = Subcategory.objects.create(
                    category=cat, name="Другая подкатегория"
                )

        target = CashflowRecord.objects.create(**{**base_kwargs, **create_kwargs(target_rel)})
        CashflowRecord.objects.create(**{**base_kwargs, **create_kwargs(other_rel)})

        response = client.get(reverse("cashflow_list"), {filter_param: target_rel.id})
        ids = {obj.id for obj in response.context["records"]}
        assert ids == {target.id}

    def test_list_view_filters_by_date_range(
        self, client, status, operation_type, category, subcategory
    ):
        """Тест на то, что list-view фильтрует записи по диапазону дат."""
        today = date.today()
        old_date = today - timedelta(days=10)

        CashflowRecord.objects.create(
            record_date=old_date,
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=Decimal("10.00"),
        )
        in_range = CashflowRecord.objects.create(
            record_date=today,
            status=status,
            operation_type=operation_type,
            category=category,
            subcategory=subcategory,
            amount=Decimal("20.00"),
        )

        response = client.get(
            reverse("cashflow_list"),
            {
                "date_from": str(today - timedelta(days=1)),
                "date_to": str(today + timedelta(days=1)),
            },
        )
        ids = {obj.id for obj in response.context["records"]}
        assert ids == {in_range.id}

    def test_list_view_context_dependent_categories_and_subcategories(
        self, client, operation_type, category, subcategory
    ):
        """Тест на то, что контекст содержит только связанные категории и подкатегории."""
        op2 = OperationType.objects.create(name="Пополнение")
        category2 = Category.objects.create(operation_type=op2, name="Инвестиции")
        subcategory2 = Subcategory.objects.create(category=category2, name="ETF")

        response = client.get(
            reverse("cashflow_list"),
            {
                "operation_type": operation_type.id,
                "category": category.id,
            },
        )

        assert category in list(response.context["categories"])
        assert category2 not in list(response.context["categories"])
        assert subcategory in list(response.context["subcategories"])
        assert subcategory2 not in list(response.context["subcategories"])

    def test_update_view_post_updates_record(
        self, client, cashflow_record, status, operation_type, category, subcategory
    ):
        """Тест на то, что POST update-view обновляет запись и показывает сообщение."""
        payload = {
            "record_date": str(cashflow_record.record_date),
            "status": status.id,
            "operation_type": operation_type.id,
            "category": category.id,
            "subcategory": subcategory.id,
            "amount": "999.99",
            "comment": "Обновлено",
        }

        response = _post_follow(
            client,
            "cashflow_update",
            data=payload,
            pk=cashflow_record.pk,
        )

        cashflow_record.refresh_from_db()
        assert response.status_code == 200
        assert cashflow_record.amount == Decimal("999.99")
        assert cashflow_record.comment == "Обновлено"
        assert "Запись успешно обновлена." in _messages(response)