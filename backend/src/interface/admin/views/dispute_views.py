from sqladmin import ModelView
from src.infrastructure.db.models.dispute_model import DisputeModel


class DisputeAdmin(ModelView, model=DisputeModel):
    name = "Disputa"
    name_plural = "Disputas"
    icon = "fa-solid fa-handshake-slash"
    
    column_list = [
        DisputeModel.id,
        "scheduling.id",
        "opener.email",
        DisputeModel.reason,
        DisputeModel.status,
        DisputeModel.created_at,
    ]
    
    column_details_list = [
        DisputeModel.id,
        "scheduling.id",
        "opener.email",
        DisputeModel.reason,
        DisputeModel.description,
        DisputeModel.contact_phone,
        DisputeModel.contact_email,
        DisputeModel.status,
        DisputeModel.resolution,
        DisputeModel.resolution_notes,
        DisputeModel.refund_type,
        "resolver.email",
        DisputeModel.resolved_at,
        DisputeModel.created_at,
        DisputeModel.updated_at,
    ]
    
    column_searchable_list = ["opener.email", "scheduling.id"]
    column_sortable_list = [DisputeModel.created_at, DisputeModel.status]
    column_default_sort = ("created_at", True)
    column_labels = {
        "scheduling.id": "ID do Agendamento",
        "opener.email": "E-mail do Aluno",
        "resolver.email": "Administrador",
    }
    export_types = ["csv", "json"]
