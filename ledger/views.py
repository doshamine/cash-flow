from django.contrib import messages
from django.db.models import RestrictedError
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

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


def load_categories(request):
    """Возвращает JSON-список категорий, отфильтрованных по типу операции."""
    operation_type_id = request.GET.get("operation_type")
    categories = Category.objects.none()

    if operation_type_id:
        categories = Category.objects.filter(
            operation_type_id=operation_type_id
        ).order_by("name")

    data = [
        {"id": category.id, "name": category.name}
        for category in categories
    ]
    return JsonResponse(data, safe=False)


def load_subcategories(request):
    """Возвращает JSON-список подкатегорий, отфильтрованных по категории."""
    category_id = request.GET.get("category")
    subcategories = Subcategory.objects.none()

    if category_id:
        subcategories = Subcategory.objects.filter(
            category_id=category_id
        ).order_by("name")

    data = [
        {"id": subcategory.id, "name": subcategory.name}
        for subcategory in subcategories
    ]
    return JsonResponse(data, safe=False)


class CashflowRecordListView(ListView):
    """Отображает список записей ДДС с фильтрацией по параметрам запроса."""

    model = CashflowRecord
    template_name = "ledger/cashflow_records/list.html"
    context_object_name = "records"

    def get_queryset(self):
        """Возвращает queryset записей с фильтрами из query-параметров."""
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
        """Формирует контекст страницы списка и текущих значений фильтров."""
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
    """Создает запись ДДС и показывает сообщение об успешном сохранении."""

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
    """Обновляет запись ДДС и показывает сообщение об успешном обновлении."""

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
    """Удаляет запись ДДС с подтверждением и показывает сообщение об успехе."""

    model = CashflowRecord
    template_name = "ledger/cashflow_records/confirm_delete.html"
    success_url = reverse_lazy("cashflow_list")
    context_object_name = "record"

    def form_valid(self, form):
        messages.success(self.request, "Запись успешно удалена.")
        return super().form_valid(form)


class ReferencesListView(TemplateView):
    """Отображает страницу управления справочниками."""

    template_name = "ledger/references/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_statuses"] = Status.objects.all().order_by("name")
        context["all_operation_types"] = OperationType.objects.all().order_by("name")
        context["all_categories"] = (
            Category.objects.select_related("operation_type").all().order_by("name")
        )
        context["all_subcategories"] = (
            Subcategory.objects.select_related("category").all().order_by("name")
        )
        return context


class StatusCreateView(CreateView):
    """Создает статус и показывает сообщение об успешном сохранении."""

    model = Status
    form_class = StatusForm
    template_name = "ledger/references/form.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить статус"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно создан.")
        return super().form_valid(form)


class StatusUpdateView(UpdateView):
    """Обновляет статус и показывает сообщение об успешном обновлении."""

    model = Status
    form_class = StatusForm
    template_name = "ledger/references/form.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактировать статус"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно обновлен.")
        return super().form_valid(form)


class StatusDeleteView(DeleteView):
    """Удаляет статус и показывает сообщение об успешном удалении."""

    model = Status
    template_name = "ledger/references/confirm_delete.html"
    success_url = reverse_lazy("references_list")
    context_object_name = "status"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Удалить статус"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно удален.")
        return super().form_valid(form)


class OperationTypeCreateView(CreateView):
    """Создает тип операции и показывает сообщение об успешном сохранении."""

    model = OperationType
    form_class = OperationTypeForm
    template_name = "ledger/references/form.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить тип операции"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Тип операции успешно создан.")
        return super().form_valid(form)


class OperationTypeUpdateView(UpdateView):
    """Обновляет тип операции и показывает сообщение об успешном обновлении."""

    model = OperationType
    form_class = OperationTypeForm
    template_name = "ledger/references/form.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактировать тип операции"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Тип операции успешно обновлен.")
        return super().form_valid(form)


class OperationTypeDeleteView(DeleteView):
    """Удаляет тип операции; при ограничениях показывает сообщение об ошибке."""

    model = OperationType
    template_name = "ledger/references/confirm_delete.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Удалить тип операции"
        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except RestrictedError:
            messages.error(
                self.request,
                "Нельзя удалить тип операции: есть связанные категории или записи.",
            )
            return redirect(self.request.path)
        messages.success(self.request, "Тип операции успешно удален.")
        return response


class CategoryCreateView(CreateView):
    """Создает категорию и показывает сообщение об успешном сохранении."""

    model = Category
    form_class = CategoryForm
    template_name = "ledger/references/form.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить категорию"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Категория успешно создана.")
        return super().form_valid(form)


class CategoryUpdateView(UpdateView):
    """Обновляет категорию и показывает сообщение об успешном обновлении."""

    model = Category
    form_class = CategoryForm
    template_name = "ledger/references/form.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактировать категорию"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Категория успешно обновлена.")
        return super().form_valid(form)


class CategoryDeleteView(DeleteView):
    """Удаляет категорию; при ограничениях показывает сообщение об ошибке."""

    model = Category
    template_name = "ledger/references/confirm_delete.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Удалить категорию"
        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except RestrictedError:
            messages.error(
                self.request,
                "Нельзя удалить категорию: есть связанные подкатегории или записи.",
            )
            return redirect(self.request.path)
        messages.success(self.request, "Категория успешно удалена.")
        return response


class SubcategoryCreateView(CreateView):
    """Создает подкатегорию и показывает сообщение об успешном сохранении."""

    model = Subcategory
    form_class = SubcategoryForm
    template_name = "ledger/references/form.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить подкатегорию"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Подкатегория успешно создана.")
        return super().form_valid(form)


class SubcategoryUpdateView(UpdateView):
    """Обновляет подкатегорию и показывает сообщение об успешном обновлении."""

    model = Subcategory
    form_class = SubcategoryForm
    template_name = "ledger/references/form.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактировать подкатегорию"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Подкатегория успешно обновлена.")
        return super().form_valid(form)


class SubcategoryDeleteView(DeleteView):
    """Удаляет подкатегорию; при ограничениях показывает сообщение об ошибке."""

    model = Subcategory
    template_name = "ledger/references/confirm_delete.html"
    success_url = reverse_lazy("references_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Удалить подкатегорию"
        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except RestrictedError:
            messages.error(
                self.request, "Нельзя удалить подкатегорию: есть связанные записи."
            )
            return redirect(self.request.path)
        messages.success(self.request, "Подкатегория успешно удалена.")
        return response
