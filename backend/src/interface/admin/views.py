from sqladmin import ModelView
from src.infrastructure.db.models.user_model import UserModel
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel
from src.infrastructure.db.models.student_profile_model import StudentProfileModel
from src.infrastructure.db.models.scheduling_model import SchedulingModel


class UserAdmin(ModelView, model=UserModel):
    name = "Usuário"
    name_plural = "Usuários"
    icon = "fa-solid fa-user"
    column_list = [
        UserModel.email,
        UserModel.full_name,
        UserModel.user_type,
        UserModel.is_active,
        UserModel.is_verified,
        UserModel.created_at,
    ]
    column_searchable_list = [UserModel.email, UserModel.full_name]
    column_sortable_list = [UserModel.created_at, UserModel.email]
    column_default_sort = ("created_at", True)
    export_types = ["csv", "json"]


class InstructorProfileAdmin(ModelView, model=InstructorProfileModel):
    name = "Perfil de Instrutor"
    name_plural = "Perfis de Instrutores"
    icon = "fa-solid fa-chalkboard-user"
    column_list = [
        "user.email",
        InstructorProfileModel.vehicle_type,
        InstructorProfileModel.license_category,
        InstructorProfileModel.hourly_rate,
        InstructorProfileModel.rating,
        InstructorProfileModel.is_available,
    ]
    column_searchable_list = ["user.email"]
    column_sortable_list = [InstructorProfileModel.rating, InstructorProfileModel.hourly_rate]
    export_types = ["csv", "json"]


class StudentProfileAdmin(ModelView, model=StudentProfileModel):
    name = "Perfil de Aluno"
    name_plural = "Perfis de Alunos"
    icon = "fa-solid fa-graduation-cap"
    column_list = [
        "user.email",
        StudentProfileModel.learning_stage,
        StudentProfileModel.license_category_goal,
        StudentProfileModel.total_lessons,
    ]
    column_searchable_list = ["user.email"]
    column_sortable_list = [StudentProfileModel.total_lessons]
    export_types = ["csv", "json"]


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
