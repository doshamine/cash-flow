from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import (
    CashflowRecordForm,
    StatusForm,
    OperationTypeForm,
    CategoryForm,
    SubcategoryForm,
)
from .models import (
    CashflowRecord,
    Status,
    OperationType,
    Category,
    Subcategory,
)


class CashflowRecordListView(ListView):
    """
    Представление списка записей о ДДС с фильтрацией по параметрам запроса.

    Отображает список `CashflowRecord` и поддерживает фильтры по периоду дат,
    статусу, типу операции, категории и подкатегории.

    Attributes:
        model (CashflowRecord): Модель записей о ДДС.
        template_name (str): Шаблон страницы списка.
        context_object_name (str): Имя списка записей в контексте шаблона.

    Related:
        - Status: Используется для фильтрации по статусу.
        - OperationType: Используется для фильтрации по типу операции.
        - Category: Используется для фильтрации по категории.
        - Subcategory: Используется для фильтрации по подкатегории.

    Example:
        /?date_from=2026-01-01&date_to=2026-01-31&operation_type=1&category=3
    """

    model = CashflowRecord
    template_name = "ledger/cashflow_records/list.html"
    context_object_name = "records"

    def get_queryset(self):
        """
        Возвращает queryset записей с примененными фильтрами из `request.GET`.

        Behavior:
            - Использует `select_related` для связанных справочников.
            - Применяет фильтры только при наличии значений в query-параметрах.
            - Поддерживает фильтрацию по полям `record_date`, `status_id`,
              `operation_type_id`, `category_id`, `subcategory_id`.

        Returns:
            QuerySet[CashflowRecord]: Отфильтрованный список записей.
        """
        queryset = CashflowRecord.objects.select_related(
            "status", "operation_type", "category", "subcategory"
        ).all()

        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        status_id = self.request.GET.get("status")
        operation_type_id = self.request.GET.get("operation_type")
        category_id = self.request.GET.get("category")
        subcategory_id = self.request.GET.get("subcategory")

        if date_from:
            queryset = queryset.filter(record_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(record_date__lte=date_to)
        if status_id:
            queryset = queryset.filter(status_id=status_id)
        if operation_type_id:
            queryset = queryset.filter(operation_type_id=operation_type_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Формирует контекст для страницы списка и формы фильтров.

        Behavior:
            - Подготавливает справочники для селектов фильтров.
            - Ограничивает категории выбранным типом операции.
            - Ограничивает подкатегории выбранной категорией.
            - Сохраняет текущие значения фильтров в `context["filters"]`.

        Returns:
            dict: Контекст шаблона со списками справочников и текущими фильтрами.
        """
        context = super().get_context_data(**kwargs)

        operation_type_id = self.request.GET.get("operation_type")
        category_id = self.request.GET.get("category")

        categories = Category.objects.all().order_by("name")
        subcategories = Subcategory.objects.all().order_by("name")

        if operation_type_id:
            categories = categories.filter(operation_type_id=operation_type_id)

        if category_id:
            subcategories = subcategories.filter(category_id=category_id)

        context["statuses"] = Status.objects.all()
        context["operation_types"] = OperationType.objects.all()
        context["categories"] = categories
        context["subcategories"] = subcategories
        context["filters"] = {
            "date_from": self.request.GET.get("date_from", ""),
            "date_to": self.request.GET.get("date_to", ""),
            "status": self.request.GET.get("status", ""),
            "operation_type": operation_type_id or "",
            "category": category_id or "",
            "subcategory": self.request.GET.get("subcategory", ""),
        }
        return context


class CashflowRecordCreateView(CreateView):
    """
    Представление создания записи о ДДС.

    Использует `CashflowRecordForm` и после успешного сохранения
    перенаправляет пользователя на страницу списка записей.

    Attributes:
        model (CashflowRecord): Модель записи о ДДС.
        form_class (CashflowRecordForm): Форма создания записи.
        template_name (str): Шаблон формы.
        success_url (str): URL редиректа после успешного сохранения.

    Example:
        Пользователь заполняет форму и получает сообщение об успешном создании.
    """

    model = CashflowRecord
    form_class = CashflowRecordForm
    template_name = "ledger/cashflow_records/form.html"
    success_url = reverse_lazy("cashflow_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создать запись о ДДС"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Запись успешно создана.")
        return super().form_valid(form)


class CashflowRecordUpdateView(UpdateView):
    """
    Представление редактирования существующей записи о ДДС.

    Attributes:
        model (CashflowRecord): Модель записи о ДДС.
        form_class (CashflowRecordForm): Форма редактирования записи.
        template_name (str): Шаблон формы.
        success_url (str): URL редиректа после успешного обновления.

    Example:
        Пользователь изменяет данные записи и получает сообщение
        об успешном обновлении.
    """

    model = CashflowRecord
    form_class = CashflowRecordForm
    template_name = "ledger/cashflow_records/form.html"
    success_url = reverse_lazy("cashflow_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактировать запись"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Запись успешно обновлена.")
        return super().form_valid(form)


class CashflowRecordDeleteView(DeleteView):
    """
    Представление удаления записи о ДДС с подтверждением.

    Attributes:
        model (CashflowRecord): Модель записи о ДДС.
        template_name (str): Шаблон подтверждения удаления.
        success_url (str): URL редиректа после удаления.
        context_object_name (str): Имя объекта в контексте шаблона.

    Example:
        После подтверждения удаления отображается сообщение об успехе.
    """

    model = CashflowRecord
    template_name = "ledger/cashflow_records/confirm_delete.html"
    success_url = reverse_lazy("cashflow_list")
    context_object_name = "record"

    def form_valid(self, form):
        messages.success(self.request, "Запись успешно удалена.")
        return super().form_valid(form)


class StatusCreateView(CreateView):
    """
    Представление создания статуса.

    Attributes:
        model (Status): Модель статусов.
        form_class (StatusForm): Форма создания статуса.
        template_name (str): Шаблон формы.
        success_url (str): URL редиректа после сохранения.
    """

    model = Status
    form_class = StatusForm
    template_name = "ledger/statuses/form.html"
    success_url = reverse_lazy("cashflow_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить статус"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно создан.")
        return super().form_valid(form)


class StatusUpdateView(UpdateView):
    """
    Представление редактирования статуса.

    Attributes:
        model (Status): Модель статусов.
        form_class (StatusForm): Форма редактирования статуса.
        template_name (str): Шаблон формы.
        success_url (str): URL редиректа после обновления.
    """

    model = Status
    form_class = StatusForm
    template_name = "ledger/statuses/form.html"
    success_url = reverse_lazy("cashflow_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактировать статус"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно обновлен.")
        return super().form_valid(form)


class StatusDeleteView(DeleteView):
    """
    Представление удаления статуса.

    Attributes:
        model (Status): Модель статусов.
        template_name (str): Шаблон подтверждения удаления.
        success_url (str): URL редиректа после удаления.
        context_object_name (str): Имя удаляемого объекта в контексте.
    """

    model = Status
    template_name = "ledger/statuses/confirm_delete.html"
    success_url = reverse_lazy("cashflow_list")
    context_object_name = "status"

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно удален.")
        return super().form_valid(form)


class OperationTypeCreateView(CreateView):
    """
    Представление создания типа операции.

    Attributes:
        model (OperationType): Модель типов операций.
        form_class (OperationTypeForm): Форма создания.
        template_name (str): Шаблон формы.
        success_url (str): URL редиректа после сохранения.
    """

    model = OperationType
    form_class = OperationTypeForm
    template_name = "ledger/operation_types/form.html"
    success_url = reverse_lazy("cashflow_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить тип операции"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Тип операции успешно создан.")
        return super().form_valid(form)


class OperationTypeUpdateView(UpdateView):
    """
    Представление редактирования типа операции.

    Attributes:
        model (OperationType): Модель типов операций.
        form_class (OperationTypeForm): Форма редактирования.
        template_name (str): Шаблон формы.
        success_url (str): URL редиректа после обновления.
    """

    model = OperationType
    form_class = OperationTypeForm
    template_name = "ledger/operation_types/form.html"
    success_url = reverse_lazy("cashflow_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактировать тип операции"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Тип операции успешно обновлен.")
        return super().form_valid(form)


class OperationTypeDeleteView(DeleteView):
    """
    Представление удаления типа операции.

    Attributes:
        model (OperationType): Модель типов операций.
        template_name (str): Шаблон подтверждения удаления.
        success_url (str): URL редиректа после удаления.
        context_object_name (str): Имя удаляемого объекта в контексте.
    """

    model = OperationType
    template_name = "ledger/operation_types/confirm_delete.html"
    success_url = reverse_lazy("cashflow_list")
    context_object_name = "operation_type"

    def form_valid(self, form):
        messages.success(self.request, "Тип операции успешно удален.")
        return super().form_valid(form)


class CategoryCreateView(CreateView):
    """
    Представление создания категории.

    Attributes:
        model (Category): Модель категорий.
        form_class (CategoryForm): Форма создания.
        template_name (str): Шаблон формы.
        success_url (str): URL редиректа после сохранения.
    """

    model = Category
    form_class = CategoryForm
    template_name = "ledger/categories/form.html"
    success_url = reverse_lazy("cashflow_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить категорию"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Категория успешно создана.")
        return super().form_valid(form)


class CategoryUpdateView(UpdateView):
    """
    Представление редактирования категории.

    Attributes:
        model (Category): Модель категорий.
        form_class (CategoryForm): Форма редактирования.
        template_name (str): Шаблон формы.
        success_url (str): URL редиректа после обновления.
    """

    model = Category
    form_class = CategoryForm
    template_name = "ledger/categories/form.html"
    success_url = reverse_lazy("cashflow_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактировать категорию"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Категория успешно обновлена.")
        return super().form_valid(form)


class CategoryDeleteView(DeleteView):
    """
    Представление удаления категории.

    Attributes:
        model (Category): Модель категорий.
        template_name (str): Шаблон подтверждения удаления.
        success_url (str): URL редиректа после удаления.
        context_object_name (str): Имя удаляемого объекта в контексте.
    """

    model = Category
    template_name = "ledger/categories/confirm_delete.html"
    success_url = reverse_lazy("cashflow_list")
    context_object_name = "category"

    def form_valid(self, form):
        messages.success(self.request, "Категория успешно удалена.")
        return super().form_valid(form)


class SubcategoryCreateView(CreateView):
    """
    Представление создания подкатегории.

    Attributes:
        model (Subcategory): Модель подкатегорий.
        form_class (SubcategoryForm): Форма создания.
        template_name (str): Шаблон формы.
        success_url (str): URL редиректа после сохранения.
    """

    model = Subcategory
    form_class = SubcategoryForm
    template_name = "ledger/subcategories/form.html"
    success_url = reverse_lazy("cashflow_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить подкатегорию"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Подкатегория успешно создана.")
        return super().form_valid(form)


class SubcategoryUpdateView(UpdateView):
    """
    Представление редактирования подкатегории.

    Attributes:
        model (Subcategory): Модель подкатегорий.
        form_class (SubcategoryForm): Форма редактирования.
        template_name (str): Шаблон формы.
        success_url (str): URL редиректа после обновления.
    """

    model = Subcategory
    form_class = SubcategoryForm
    template_name = "ledger/subcategories/form.html"
    success_url = reverse_lazy("cashflow_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактировать подкатегорию"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Подкатегория успешно обновлена.")
        return super().form_valid(form)


class SubcategoryDeleteView(DeleteView):
    """
    Представление удаления подкатегории.

    Attributes:
        model (Subcategory): Модель подкатегорий.
        template_name (str): Шаблон подтверждения удаления.
        success_url (str): URL редиректа после удаления.
        context_object_name (str): Имя удаляемого объекта в контексте.
    """

    model = Subcategory
    template_name = "ledger/subcategories/confirm_delete.html"
    success_url = reverse_lazy("cashflow_list")
    context_object_name = "subcategory"

    def form_valid(self, form):
        messages.success(self.request, "Подкатегория успешно удалена.")
        return super().form_valid(form)
