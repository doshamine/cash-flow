from django import forms

from .models import (
    Status,
    OperationType,
    Category,
    Subcategory,
    CashflowRecord,
)


class StatusForm(forms.ModelForm):
    """
    Форма для создания и редактирования статусов записей о ДДС.

    Используется для управления справочником статусов.

    Attributes:
        name (CharField): Название статуса.

    Related:
        - CashflowRecord.status: Запись ДДС может иметь выбранный статус.

    Example:
        >>> form = StatusForm(data={"name": "Бизнес"})
        >>> form.is_valid()
        True
    """

    class Meta:
        model = Status
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например, Бизнес"}),
        }


class OperationTypeForm(forms.ModelForm):
    """
    Форма для создания и редактирования типов операций.

    Используется для управления справочником типов операций
    (например, "Пополнение", "Списание").

    Attributes:
        name (CharField): Название типа операции.

    Related:
        - Category.operation_type: Категория привязана к типу операции.
        - CashflowRecord.operation_type: Запись о ДДС содержит тип операции.

    Example:
        >>> form = OperationTypeForm(data={"name": "Списание"})
        >>> form.is_valid()
        True
    """

    class Meta:
        model = OperationType
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например, Списание"}),
        }


class CategoryForm(forms.ModelForm):
    """
    Форма для создания и редактирования категорий операций.

    Категория привязана к выбранному типу операции.

    Attributes:
        operation_type (ModelChoiceField): Тип операции для категории.
        name (CharField): Название категории.

    Related:
        - Subcategory.category: Подкатегория привязана к категории.
        - CashflowRecord.category: Запись о ДДС содержит категорию.

    Example:
        >>> form = CategoryForm(data={"operation_type": 1, "name": "Маркетинг"})
        >>> form.is_valid()
        True
    """

    class Meta:
        model = Category
        fields = ["operation_type", "name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например, Маркетинг"}),
        }


class SubcategoryForm(forms.ModelForm):
    """
    Форма для создания и редактирования подкатегорий операций.

    Подкатегория привязана к выбранной категории.

    Attributes:
        category (ModelChoiceField): Категория для подкатегории.
        name (CharField): Название подкатегории.

    Related:
        - CashflowRecord.subcategory: Запись о ДДС содержит подкатегорию.

    Example:
        >>> form = SubcategoryForm(data={"category": 1, "name": "Avito"})
        >>> form.is_valid()
        True
    """

    class Meta:
        model = Subcategory
        fields = ["category", "name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например, Avito"}),
        }


class CashflowRecordForm(forms.ModelForm):
    """
    Форма для создания и редактирования записей о ДДС.

    Форма обеспечивает каскадный выбор справочников с выполнением следующих условий:
    - категории фильтруются по выбранному типу операции;
    - подкатегории фильтруются по выбранной категории.

    Attributes:
        record_date (DateField): Дата операции.
        status (ModelChoiceField): Статус операции (опционально).
        operation_type (ModelChoiceField): Тип операции.
        category (ModelChoiceField): Категория операции.
        subcategory (ModelChoiceField): Подкатегория операции.
        amount (DecimalField): Сумма операции.
        comment (CharField): Комментарий к операции (опционально).

    Related:
        - Status.cashflow_records: Статус связан с записями о ДДС.
        - OperationType.cashflow_records: Тип операции связан с записями о ДДС.
        - Category.cashflow_records: Категория связана с записями о ДДС.
        - Subcategory.cashflow_records: Подкатегория связана с записями о ДДС.

    Behavior:
        - Поле `status` необязательное и имеет пустую подпись "Без статуса".
        - До выбора родительских полей `category` и `subcategory` имеют пустые queryset.
        - При редактировании записи queryset строятся из значений `self.instance`.
        - При отправке формы queryset фильтруются по `self.data`.

    Example:
        >>> form = CashflowRecordForm(data={
        ...     "record_date": "2026-04-10",
        ...     "operation_type": 1,
        ...     "category": 2,
        ...     "subcategory": 3,
        ...     "amount": "1500.00",
        ... })
        >>> form.is_valid()
        True
    """

    class Meta:
        model = CashflowRecord
        fields = [
            "record_date",
            "status",
            "operation_type",
            "category",
            "subcategory",
            "amount",
            "comment",
        ]
        widgets = {
            "record_date": forms.DateInput(attrs={"type": "date"}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        """
        Настраивает обязательность полей и зависимые queryset при инициализации формы.

        Behavior:
            - Делает поле `status` необязательным.
            - Устанавливает стартовые пустые queryset для `category` и `subcategory`.
            - В режиме редактирования (`instance.pk`) загружает категории по
              `instance.operation_type` и подкатегории по `instance.category`.
            - В привязанной форме (`self.data`) фильтрует категории по `operation_type`,
              а подкатегории по `category`.
            - Невалидные идентификаторы в `self.data` (нечисловые значения) игнорируются.

        Example:
            >>> form = CashflowRecordForm(data={"operation_type": "1", "category": "2"})
            >>> list(form.fields["category"].queryset)
            [...]
        """
        super().__init__(*args, **kwargs)

        self.fields["status"].required = False
        self.fields["status"].empty_label = "Без статуса"
        self.fields["category"].queryset = Category.objects.none()
        self.fields["subcategory"].queryset = Subcategory.objects.none()

        if self.instance.pk:
            self.fields["category"].queryset = Category.objects.filter(
                operation_type=self.instance.operation_type
            ).order_by("name")
            self.fields["subcategory"].queryset = Subcategory.objects.filter(
                category=self.instance.category
            ).order_by("name")

        if "operation_type" in self.data:
            try:
                operation_type_id = int(self.data.get("operation_type"))
                self.fields["category"].queryset = Category.objects.filter(
                    operation_type_id=operation_type_id
                ).order_by("name")
            except (TypeError, ValueError):
                pass

        if "category" in self.data:
            try:
                category_id = int(self.data.get("category"))
                self.fields["subcategory"].queryset = Subcategory.objects.filter(
                    category_id=category_id
                ).order_by("name")
            except (TypeError, ValueError):
                pass
