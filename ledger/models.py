from datetime import date

from django.core.exceptions import ValidationError
from django.db import models


class Status(models.Model):
    """
    Модель для хранения статусов записей (например, "Бизнес", "Личное", "Налог").

    Используется для группировки записей.
    Каждый статус уникален по названию.

    Attributes:
        name (CharField): Название статуса (уникальное значение, макс 100 символов).

    Related:
        - CashflowRecord.status: Запись может иметь один из статусов.

    Example:
        >>> status = Status.objects.create(name="Бизнес")
        >>> str(status)
        'Бизнес'
    """

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class OperationType(models.Model):
    """
    Модель для хранения типов операций (например, "Пополнение", "Списание").

    Используется как корневая категория для всех категорий и подкатегорий.
    Каждый тип операции уникален по названию.

    Attributes:
        name (CharField): Название типа операции (уникальное значение, макс 100 символов).

    Related:
        - Category.operation_type: Категория относится к типу операции (обратная связь "categories").
        - CashflowRecord.operation_type: Запись содержит тип операции.

    Example:
        >>> op_type = OperationType.objects.create(name="Списание")
        >>> str(op_type)
        'Списание'
    """

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Тип операции"
        verbose_name_plural = "Типы операций"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    """
    Модель для хранения категорий операций (например, "Инфраструктура", "Маркетинг").

    Категория связана с типом операции.
    Комбинация (operation_type, name) должна быть уникальна.

    Attributes:
        operation_type (ForeignKey): Связь с типом операции (RESTRICT при удалении).
        name (CharField): Название категории (макс 100 символов).

    Related:
        - Subcategory.category: Подкатегория относится к категории (обратная связь "subcategories").
        - CashflowRecord.category: Запись содержит категорию.

    Constraints:
        - UniqueConstraint: (operation_type, name) — комбинация типа и названия должна быть уникальна.

    Example:
        >>> op_type = OperationType.objects.get(name="Списание")
        >>> category = Category.objects.create(operation_type=op_type, name="Инфраструктура")
        >>> str(category)
        'Инфраструктура (Списание)'
    """

    operation_type = models.ForeignKey(
        OperationType,
        on_delete=models.RESTRICT,
        related_name="categories",
    )
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["operation_type", "name"],
                name="uq_category_type_name",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.operation_type.name})"


class Subcategory(models.Model):
    """
        Модель для хранения подкатегорий (например, "VPS", "Proxy" для "Инфраструктуры").
    .
        Подкатегория связана с категорией.
        Комбинация (category, name) должна быть уникальна.

        Attributes:
            category (ForeignKey): Связь с категорией (RESTRICT при удалении).
            name (CharField): Название подкатегории (макс 100 символов).

        Related:
            - CashflowRecord.subcategory: Запись содержит подкатегорию.

        Constraints:
            - UniqueConstraint: (category, name) — комбинация категории и названия должна быть уникальна.

        Example:
            >>> category = Category.objects.get(name="Инфраструктура")
            >>> subcategory = Subcategory.objects.create(category=category, name="VPS")
            >>> str(subcategory)
            'VPS (Инфраструктура)'
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        related_name="subcategories",
    )
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"],
                name="uq_subcategory_category_name",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.category.name})"


class CashflowRecord(models.Model):
    """
    Модель для хранения записей о ДДС (Движение Денежных Средств).

    Каждая запись отслеживает финансовую операцию с указанием даты, суммы, типа, категории
    и подкатегории. Записи индексируются по дате для быстрого поиска.

    Attributes:
        record_date (DateField): Дата операции (по умолчанию — сегодняшняя дата).

        status (ForeignKey): Статус операции (опционально, SET_NULL при удалении статуса).

        operation_type (ForeignKey): Тип операции (RESTRICT при удалении).
            - Обязательное поле.
            - Должно соответствовать типу категории (проверяется в clean()).

        category (ForeignKey): Категория операции (RESTRICT при удалении).
            - Обязательное поле.
            - Должна принадлежать выбранному типу операции (проверяется в clean()).

        subcategory (ForeignKey): Подкатегория операции (RESTRICT при удалении).
            - Обязательное поле.
            - Должна принадлежать выбранной категории (проверяется в clean()).

        amount (DecimalField): Сумма операции в рублях (макс 12 цифр, 2 знака после запятой).
            - Обязательное поле

        comment (TextField): Комментарий к операции (опционально).

        created_at (DateTimeField): Дата и время создания записи (автоматически устанавливается).

        updated_at (DateTimeField): Дата и время последнего обновления (автоматически обновляется).

    Related:
        - Status.cashflow_records: Статус имеет множество записей.
        - OperationType.cashflow_records: Тип операции имеет множество записей.
        - Category.cashflow_records: Категория имеет множество записей.
        - Subcategory.cashflow_records: Подкатегория имеет множество записей.

    Validation (в методе clean()):
        - category.operation_type должна соответствовать выбранному operation_type.
        - subcategory.category должна соответствовать выбранной category.

    Ordering:
        - По умолчанию сортируется по дате (-record_date), потом по времени создания (-created_at).
        - Новые записи отображаются первыми.

    Indexes:
        - idx_cashflow_record_date: Индекс на поле record_date для быстрого поиска по датам.

    Example:
        >>> from datetime import date
        >>> status = Status.objects.create(name="Бизнес")
        >>> op_type = OperationType.objects.create(name="Списание")
        >>> category = Category.objects.create(operation_type=op_type, name="Инфраструктура")
        >>> subcategory = Subcategory.objects.create(category=category, name="VPS")
        >>> record = CashflowRecord.objects.create(
        ...     record_date=date.today(),
        ...     status=status,
        ...     operation_type=op_type,
        ...     category=category,
        ...     subcategory=subcategory,
        ...     amount=150.50,
        ...     comment="Оплата за VPS сервер"
        ... )
        >>> record.full_clean()
        >>> record.save()
        >>> str(record)
        '2026-04-08 150.50 ₽'
    """

    record_date = models.DateField(default=date.today)

    status = models.ForeignKey(
        Status,
        on_delete=models.SET_NULL,
        related_name="cashflow_records",
        null=True,
        blank=True,
    )
    operation_type = models.ForeignKey(
        OperationType,
        on_delete=models.RESTRICT,
        related_name="cashflow_records",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        related_name="cashflow_records",
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.RESTRICT,
        related_name="cashflow_records",
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Запись ДДС"
        verbose_name_plural = "Записи ДДС"
        ordering = ["-record_date", "-created_at"]
        indexes = [
            models.Index(
                fields=["record_date"],
                name="idx_cashflow_record_date",
            ),
        ]

    def clean(self):
        """
        Проверяет логическую согласованность выбранных категорий и типа операции.

        Validates:
            1. Категория должна принадлежать выбранному типу операции.
            2. Подкатегория должна принадлежать выбранной категории.

        Raises:
            ValidationError: Если категория или подкатегория не соответствуют выбранным полям.
        """
        errors = {}

        if self.category_id is not None and self.operation_type_id is not None:
            if self.category.operation_type_id != self.operation_type_id:
                errors["category"] = (
                    "Выбранная категория не относится к выбранному типу операции."
                )

        if self.subcategory_id is not None and self.category_id is not None:
            if self.subcategory.category_id != self.category_id:
                errors["subcategory"] = (
                    "Выбранная подкатегория не относится к выбранной категории."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.record_date} {self.amount:.2f} ₽"
