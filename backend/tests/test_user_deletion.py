import asyncio
import uuid
from datetime import datetime, time, timedelta
from sqlalchemy import select, delete
from src.infrastructure.db.database import get_db, AsyncSessionLocal
from src.infrastructure.db.models.user_model import UserModel
from src.infrastructure.db.models.availability_model import AvailabilityModel
from src.infrastructure.db.models.scheduling_model import SchedulingModel
from src.infrastructure.db.models.message_model import MessageModel
from src.infrastructure.db.models.review_model import ReviewModel
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel
from src.domain.entities.user_type import UserType
from src.domain.entities.scheduling_status import SchedulingStatus

async def test_user_deletion():
    print("Iniciando teste de deleção de usuário...")
    
    async with AsyncSessionLocal() as session:
        # 1. Criar um instrutor de teste
        test_email = f"test_instructor_{uuid.uuid4().hex[:8]}@example.com"
        instructor = UserModel(
            id=uuid.uuid4(),
            email=test_email,
            hashed_password="hashed_password",
            full_name="Test Instructor",
            user_type=UserType.INSTRUCTOR.value,
            is_active=True
        )
        session.add(instructor)
        
        # 2. Criar perfil de instrutor
        profile = InstructorProfileModel(
            user_id=instructor.id,
            bio="Test Bio",
            vehicle_type="Car",
            license_category="B",
            hourly_rate=80.00
        )
        session.add(profile)
        
        # 3. Criar disponibilidade
        availability = AvailabilityModel(
            instructor_id=instructor.id,
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_active=True
        )
        session.add(availability)
        
        # 4. Criar um estudante de teste
        student_email = f"test_student_{uuid.uuid4().hex[:8]}@example.com"
        student = UserModel(
            id=uuid.uuid4(),
            email=student_email,
            hashed_password="hashed_password",
            full_name="Test Student",
            user_type=UserType.STUDENT.value,
            is_active=True
        )
        session.add(student)
        
        # 5. Criar agendamento
        scheduling = SchedulingModel(
            id=uuid.uuid4(),
            student_id=student.id,
            instructor_id=instructor.id,
            scheduled_datetime=datetime.now() + timedelta(days=1),
            duration_minutes=60,
            price=80.00,
            status=SchedulingStatus.PENDING
        )
        session.add(scheduling)
        
        # 6. Criar mensagem
        message = MessageModel(
            sender_id=student.id,
            receiver_id=instructor.id,
            content="Hello instructor",
            timestamp=datetime.now()
        )
        session.add(message)
        
        await session.commit()
        print(f"Dados de teste criados. Instrutor ID: {instructor.id}")

        # 7. Tentar deletar o instrutor
        print("Tentando deletar o instrutor...")
        await session.delete(instructor)
        try:
            await session.commit()
            print("Usuário deletado com sucesso!")
        except Exception as e:
            await session.rollback()
            print(f"ERRO AO DELETAR USUÁRIO: {e}")
            return False

        # 8. Verificar se os dados relacionados sumiram
        print("Verificando se os dados relacionados foram removidos...")
        
        # Tentar buscar registros órfãos
        q_avail = await session.execute(select(AvailabilityModel).where(AvailabilityModel.instructor_id == instructor.id))
        if q_avail.scalars().first():
            print("ERRO: Disponibilidade não foi removida!")
            return False
            
        q_sched = await session.execute(select(SchedulingModel).where(SchedulingModel.instructor_id == instructor.id))
        if q_sched.scalars().first():
            print("ERRO: Agendamento não foi removido!")
            return False

        q_msg = await session.execute(select(MessageModel).where(MessageModel.receiver_id == instructor.id))
        if q_msg.scalars().first():
            print("ERRO: Mensagem recebida não foi removida!")
            return False

        # Limpar estudante de teste
        await session.delete(student)
        await session.commit()
        
        print("Teste concluído com SUCESSO! Todos os registros dependentes foram removidos.")
        return True

if __name__ == "__main__":
    asyncio.run(test_user_deletion())
