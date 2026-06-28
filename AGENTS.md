# Agent-demo

AI 对话助手，基于 LangGraph + FastAPI，支持工具调用（天气查询）。

## 启动

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL_NAME
python main.py         # http://localhost:8000
```

## 架构

```
main.py → uvicorn → web.server:app
                       ├─ /api/* 路由
                       ├─ / (返回 web/static/index.html)
                       └─ POST /api/chat → agent.graph.build_graph()
                                              ├─ agent (call_model → LLM)
                                              ├─ tools (execute_tools → 工具)
                                              └─ 循环直到无 tool_calls
```

- **状态**: `agent/state.py` — `AgentState(messages, session_id)`
- **LLM**: `agent/nodes/call_model.py` — ChatOpenAI + `SYSTEM_PROMPT`
- **工具注册**: `agent/tools/registry.py` — 模块级列表 `_tools`，新工具需 import 并调用 `register_tool()`
- **天气工具**: `wttr.in`（免费，无需 API Key）
- **持久化**: SQLite `data/agent.db`，表 `sessions` + `messages`

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/chat` | SSE 流式对话（`astream_events version="v2"`） |
| GET | `/api/sessions` | 会话列表 |
| POST | `/api/sessions` | 新建会话 |
| DELETE | `/api/sessions/{id}` | 删除会话 |
| PUT | `/api/sessions/{id}` | 重命名会话 |
| GET | `/api/sessions/{id}/messages` | 历史消息 |
| DELETE | `/api/sessions/{id}/messages/last` | 删除最后一条 assistant 消息（重新生成用） |

## SSE 事件

| event | data | 触发时机 |
|---|---|---|
| `token` | `{"token": "你好"}` | LLM 流式输出 |
| `tool_start` | `{"type":"tool_start","tool":"get_weather"}` | 工具开始执行 |
| `tool_end` | `{"type":"tool_end","tool":"get_weather"}` | 工具执行完毕 |
| `error` | `{"message":"..."}` | 异常 |
| `done` | `{"content":"..."}` | 回复完成（立即返回，不等待标题生成） |
| `message` | `{"title":"北京天气"}` | 标题生成后单独推送 |

## 关键约定

- 前端为单 HTML 文件 `web/static/index.html`（inline CSS/JS），修改需同步后端 SSE 事件格式
- 前端使用 `fetch` + `ReadableStream` 解析 POST SSE，非标准 `EventSource`
- `.env` 已 gitignore，改动配置需同步 `.env.example`
- 新增工具步骤: ①创建 `agent/tools/xxx.py` ②在 `agent/tools/registry.py` 中 import 并 `register_tool()`
- 系统提示词在 `agent/nodes/call_model.py` 的 `SYSTEM_PROMPT`
- 标题生成在 `web/server.py` 的 `generate_title()`，首次对话后触发
- 无测试、无 lint、无 CI 配置
