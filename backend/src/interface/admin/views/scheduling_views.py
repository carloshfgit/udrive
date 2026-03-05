from sqladmin import ModelView
from src.infrastructure.db.models.scheduling_model import SchedulingModel


class SchedulingAdmin(ModelView, model=SchedulingModel):
    name = "Agendamento"
    name_plural = "Agendamentos"
    icon = "fa-solid fa-calendar-check"
    column_list = [
        SchedulingModel.id,
        SchedulingModel.scheduled_datetime,
        SchedulingModel.status,
        "student.email",
        "instructor.email",
        SchedulingModel.price,
    ]
    column_searchable_list = ["student.email", "instructor.email"]
    column_sortable_list = [SchedulingModel.scheduled_datetime, SchedulingModel.status]
    column_default_sort = ("scheduled_datetime", True)
    export_types = ["csv", "json"]
