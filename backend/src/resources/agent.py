from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_admin_user, get_current_user
from exceptions import (
    ApplicationException,
    BadRequestException,
    InternalServerException,
    NotFoundException,
    RecordIntegrityException,
    RecordNotFoundException,
)
from log import log
from models import get_db
from repositories import AgentRepository
from schemas import AgentDBInputSchema, AgentResponse, CreateAgentRequest, UpdateAgentRequest

router = APIRouter()


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(
    payload: CreateAgentRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Creating agent with name: '{payload.name}'")
        data = AgentDBInputSchema(
            **{**payload.dict(), "updated_by": current_user_id, "created_by": current_user_id}
        )
        agent = await AgentRepository(db).create(data)
        return AgentResponse(**agent.dict())
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="Agent name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        log.info("Listing agents")
        items = await AgentRepository(db).list()
        return [AgentResponse(**item.dict()) for item in items]
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Getting agent for agent_id: '{agent_id}'")
        item = await AgentRepository(db).get(id=agent_id)
        return AgentResponse(**item.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    payload: UpdateAgentRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Updating agent for agent_id: '{agent_id}'")
        agent = await AgentRepository(db).update(
            values={**{**payload.dict(exclude_none=True), "updated_by": current_user_id}},
            id=agent_id,
        )
        return AgentResponse(**agent.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="Agent name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Deleting agent for agent_id: '{agent_id}'")
        await AgentRepository(db).delete(id=agent_id, unique_fields=["name"])
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
