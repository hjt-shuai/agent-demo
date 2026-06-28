import json
import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from langchain_core.messages import HumanMessage, AIMessage

from agent.graph import build_graph
from agent.memory.store import (
    init_db,
    create_session,
    list_sessions,
    delete_session,
    rename_session,
    save_message,
    get_messages,
)

app = FastAPI(title="Agent Demo")

static_dir = os.path.join(os.path.dirname(__file__), "static")
init_db()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class CreateSessionRequest(BaseModel):
    name: str = "新对话"


class RenameSessionRequest(BaseModel):
    name: str


@app.get("/")
async def root():
    index_path = os.path.join(static_dir, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/api/chat")
async def chat(req: ChatRequest):
    agent = build_graph()

    async def event_generator():
        save_message(req.session_id, "user", req.message)

        history = get_messages(req.session_id)
        messages = []
        for h in history:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            elif h["role"] == "assistant":
                messages.append(AIMessage(content=h.get("content", "")))

        collected_content = ""

        try:
            async for event in agent.astream_events(
                {"messages": messages, "session_id": req.session_id},
                version="v2",
            ):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and chunk.content:
                        collected_content += chunk.content
                        yield {
                            "event": "token",
                            "data": json.dumps({"token": chunk.content}, ensure_ascii=False),
                        }

                elif kind == "on_tool_start":
                    yield {
                        "event": "tool_start",
                        "data": json.dumps({"type": "tool_start", "tool": event["name"]}, ensure_ascii=False),
                    }

                elif kind == "on_tool_end":
                    yield {
                        "event": "tool_end",
                        "data": json.dumps({"type": "tool_end", "tool": event["name"]}, ensure_ascii=False),
                    }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}, ensure_ascii=False),
            }
            return

        if collected_content:
            save_message(req.session_id, "assistant", collected_content)

            if len(history) <= 1:
                name = req.message[:30] + ("..." if len(req.message) > 30 else "")
                rename_session(req.session_id, name)

        yield {
            "event": "done",
            "data": json.dumps({"content": collected_content}, ensure_ascii=False),
        }

    return EventSourceResponse(event_generator())


@app.get("/api/sessions")
async def get_sessions():
    return list_sessions()


@app.post("/api/sessions")
async def new_session(req: CreateSessionRequest):
    return create_session(req.name)


@app.delete("/api/sessions/{session_id}")
async def remove_session(session_id: str):
    delete_session(session_id)
    return {"ok": True}


@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, req: RenameSessionRequest):
    rename_session(session_id, req.name)
    return {"ok": True}


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    return get_messages(session_id)
