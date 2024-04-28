from fastapi import APIRouter, HTTPException, Depends
from src.logger import logger
from src.node.crud import (
    crud_create_node,
    crud_read_nodes,
    crud_read_node,
    crud_update_node,
    crud_delete_node
)
from src.node.schemas import NodeCreate, NodeUpdate
from src.user.models import User
from src.auth.utils import admin

router = APIRouter(prefix="/api/node", tags=["nodes"])


@router.post("/create")
async def create_node(data: NodeCreate, _: User = Depends(admin)):
    try:
        node_id = await crud_create_node(data)

        return {"id": node_id}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.get("/all")
async def read_nodes(_: User = Depends(admin)):
    try:
        nodes = await crud_read_nodes()

        return nodes
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.get("/{node_id}")
async def read_node(node_id: int, _: User = Depends(admin)):
    try:
        node = await crud_read_node(node_id)

        if node is None:
            raise ValueError(f"Node with id {node_id} doesn't exist")

        return node
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.patch("/{node_id}")
async def update_node(node_id: int, data: NodeUpdate, _: User = Depends(admin)):
    try:
        await crud_update_node(data, node_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.delete("/{node_id}")
async def delete_node(node_id: int, _: User = Depends(admin)):
    try:
        await crud_delete_node(node_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)
