# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import base64
import json
import logging
import os
from typing import Annotated, List, cast
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from langchain_core.messages import AIMessageChunk, ToolMessage, BaseMessage
from langgraph.types import Command

from src.config.tools import SELECTED_RAG_PROVIDER
from src.rag.retriever import Resource
from src.server.chat_request import (
    ChatMessage,
    ChatRequest,
    GeneratePodcastRequest,
    GeneratePPTRequest,
    GenerateProseRequest,
    TTSRequest,
)
from src.server.mcp_request import MCPServerMetadataRequest, MCPServerMetadataResponse
from src.server.mcp_utils import load_mcp_tools
from src.server.rag_request import (
    RAGConfigResponse,
    RAGResourceRequest,
    RAGResourcesResponse,
)
from src.tools import VolcengineTTS

logger = logging.getLogger(__name__)

app = FastAPI(
    title="PrivateSearch API",
    description="Privacy-focused AI research platform API",
    version="0.1.0",
)

# Add CORS middleware
# Configure allowed origins based on environment
allowed_origins = ["*"]  # Default for development
if os.getenv("APP_ENV") == "production":
    # In production, restrict to specific domains
    allowed_origins = [
        "https://*.vercel.app",
        "https://deerflow.tech",
        "https://www.deerflow.tech",
        os.getenv("FRONTEND_URL", "https://your-app.vercel.app")
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize graph with error handling
graph = None
graph_error = None

def initialize_graph():
    """Initialize the graph with error handling."""
    global graph, graph_error
    try:
        from src.graph.builder import build_graph_with_memory
        graph = build_graph_with_memory()
        logger.info("Graph initialized successfully")
    except Exception as e:
        graph_error = str(e)
        logger.error(f"Failed to initialize graph: {e}")
        logger.info("Application will start in limited mode")

# Try to initialize graph on startup
initialize_graph()

# Add startup event for debugging
@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI app startup event triggered")
    logger.info(f"Graph initialized: {graph is not None}")
    if graph_error:
        logger.warning(f"Graph initialization error: {graph_error}")
    logger.info("FastAPI app is ready to serve requests")


@app.get("/api/health")
async def health_check():
    """Health check endpoint for Railway deployment."""
    status = {
        "status": "healthy",
        "service": "PrivateSearch API",
        "graph_initialized": graph is not None,
    }
    if graph_error:
        status["graph_error"] = graph_error
        status["note"] = "Running in limited mode - some features may not be available"
    return status


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    if graph is None:
        raise HTTPException(
            status_code=503,
            detail=f"Service temporarily unavailable. Graph initialization failed: {graph_error}"
        )

    thread_id = request.thread_id
    if thread_id == "__default__":
        thread_id = str(uuid4())

    # Add timeout wrapper for the streaming response
    import asyncio

    async def timeout_wrapper():
        # Get timeout from environment or use default (30 minutes)
        timeout_seconds = int(os.getenv("STREAM_TIMEOUT_SECONDS", "1800"))  # 30 minutes default

        try:
            async with asyncio.timeout(timeout_seconds):
                async for chunk in _astream_workflow_generator(
                    request.model_dump()["messages"],
                    thread_id,
                    request.resources,
                    request.max_plan_iterations,
                    request.max_step_num,
                    request.max_search_results,
                    request.auto_accepted_plan,
                    request.interrupt_feedback,
                    request.mcp_settings,
                    request.enable_background_investigation,
                ):
                    yield chunk
        except asyncio.TimeoutError:
            logger.warning(f"Stream timeout for thread {thread_id} after {timeout_seconds} seconds")
            yield _make_event(
                "error",
                {
                    "thread_id": thread_id,
                    "error": f"Request timeout after {timeout_seconds} seconds",
                    "role": "assistant",
                },
            )
        except Exception as e:
            logger.exception(f"Error in timeout wrapper for thread {thread_id}: {e}")
            yield _make_event(
                "error",
                {
                    "thread_id": thread_id,
                    "error": f"Stream error: {str(e)}",
                    "role": "assistant",
                },
            )

    return StreamingResponse(
        timeout_wrapper(),
        media_type="text/event-stream",
    )


async def _astream_workflow_generator(
    messages: List[ChatMessage],
    thread_id: str,
    resources: List[Resource],
    max_plan_iterations: int,
    max_step_num: int,
    max_search_results: int,
    auto_accepted_plan: bool,
    interrupt_feedback: str,
    mcp_settings: dict,
    enable_background_investigation,
):
    import asyncio

    input_ = {
        "messages": messages,
        "plan_iterations": 0,
        "final_report": "",
        "current_plan": None,
        "observations": [],
        "auto_accepted_plan": auto_accepted_plan,
        "enable_background_investigation": enable_background_investigation,
    }
    if not auto_accepted_plan and interrupt_feedback:
        resume_msg = f"[{interrupt_feedback}]"
        # add the last message to the resume message
        if messages:
            resume_msg += f" {messages[-1]['content']}"
        input_ = Command(resume=resume_msg)

    try:
        async for agent, _, event_data in graph.astream(
            input_,
            config={
                "thread_id": thread_id,
                "resources": resources,
                "max_plan_iterations": max_plan_iterations,
                "max_step_num": max_step_num,
                "max_search_results": max_search_results,
                "mcp_settings": mcp_settings,
            },
            stream_mode=["messages", "updates"],
            subgraphs=True,
        ):
            try:
                if isinstance(event_data, dict):
                    if "__interrupt__" in event_data:
                        yield _make_event(
                            "interrupt",
                            {
                                "thread_id": thread_id,
                                "id": event_data["__interrupt__"][0].ns[0],
                                "role": "assistant",
                                "content": event_data["__interrupt__"][0].value,
                                "finish_reason": "interrupt",
                                "options": [
                                    {"text": "Edit plan", "value": "edit_plan"},
                                    {"text": "Start research", "value": "accepted"},
                                ],
                            },
                        )
                    continue
                message_chunk, message_metadata = cast(
                    tuple[BaseMessage, dict[str, any]], event_data
                )
                event_stream_message: dict[str, any] = {
                    "thread_id": thread_id,
                    "agent": agent[0].split(":")[0],
                    "id": message_chunk.id,
                    "role": "assistant",
                    "content": message_chunk.content,
                }
                if message_chunk.response_metadata.get("finish_reason"):
                    event_stream_message["finish_reason"] = message_chunk.response_metadata.get(
                        "finish_reason"
                    )
                if isinstance(message_chunk, ToolMessage):
                    # Tool Message - Return the result of the tool call
                    event_stream_message["tool_call_id"] = message_chunk.tool_call_id
                    yield _make_event("tool_call_result", event_stream_message)
                elif isinstance(message_chunk, AIMessageChunk):
                    # AI Message - Raw message tokens
                    if message_chunk.tool_calls:
                        # AI Message - Tool Call
                        event_stream_message["tool_calls"] = message_chunk.tool_calls
                        event_stream_message["tool_call_chunks"] = (
                            message_chunk.tool_call_chunks
                        )
                        yield _make_event("tool_calls", event_stream_message)
                    elif message_chunk.tool_call_chunks:
                        # AI Message - Tool Call Chunks
                        event_stream_message["tool_call_chunks"] = (
                            message_chunk.tool_call_chunks
                        )
                        yield _make_event("tool_call_chunks", event_stream_message)
                    else:
                        # AI Message - Raw message tokens
                        yield _make_event("message_chunk", event_stream_message)
            except asyncio.CancelledError:
                logger.info(f"Stream cancelled for thread {thread_id}")
                # Clean up and re-raise to properly handle cancellation
                raise
            except Exception as e:
                logger.error(f"Error processing event in stream for thread {thread_id}: {e}")
                # Send error event to client
                yield _make_event(
                    "error",
                    {
                        "thread_id": thread_id,
                        "error": str(e),
                        "role": "assistant",
                    },
                )
                break
    except asyncio.CancelledError:
        logger.info(f"Workflow stream cancelled for thread {thread_id}")
        # Don't re-raise here as it's expected when client disconnects
        return
    except Exception as e:
        logger.exception(f"Unexpected error in workflow stream for thread {thread_id}: {e}")
        # Send final error event
        try:
            yield _make_event(
                "error",
                {
                    "thread_id": thread_id,
                    "error": f"Workflow error: {str(e)}",
                    "role": "assistant",
                },
            )
        except Exception:
            # If we can't even send the error event, just log and return
            logger.error(f"Failed to send error event for thread {thread_id}")
            return


def _make_event(event_type: str, data: dict[str, any]):
    if data.get("content") == "":
        data.pop("content")
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using volcengine TTS API."""
    try:
        app_id = os.getenv("VOLCENGINE_TTS_APPID", "")
        if not app_id:
            raise HTTPException(
                status_code=400, detail="VOLCENGINE_TTS_APPID is not set"
            )
        access_token = os.getenv("VOLCENGINE_TTS_ACCESS_TOKEN", "")
        if not access_token:
            raise HTTPException(
                status_code=400, detail="VOLCENGINE_TTS_ACCESS_TOKEN is not set"
            )
        cluster = os.getenv("VOLCENGINE_TTS_CLUSTER", "volcano_tts")
        voice_type = os.getenv("VOLCENGINE_TTS_VOICE_TYPE", "BV700_V2_streaming")

        tts_client = VolcengineTTS(
            appid=app_id,
            access_token=access_token,
            cluster=cluster,
            voice_type=voice_type,
        )
        # Call the TTS API
        result = tts_client.text_to_speech(
            text=request.text[:1024],
            encoding=request.encoding,
            speed_ratio=request.speed_ratio,
            volume_ratio=request.volume_ratio,
            pitch_ratio=request.pitch_ratio,
            text_type=request.text_type,
            with_frontend=request.with_frontend,
            frontend_type=request.frontend_type,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=str(result["error"]))

        # Decode the base64 audio data
        audio_data = base64.b64decode(result["audio_data"])

        # Return the audio file
        return Response(
            content=audio_data,
            media_type=f"audio/{request.encoding}",
            headers={
                "Content-Disposition": (
                    f"attachment; filename=tts_output.{request.encoding}"
                )
            },
        )
    except Exception as e:
        logger.exception(f"Error in TTS endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/podcast/generate")
async def generate_podcast(request: GeneratePodcastRequest):
    try:
        from src.podcast.graph.builder import build_graph as build_podcast_graph
        report_content = request.content
        print(report_content)
        workflow = build_podcast_graph()
        final_state = workflow.invoke({"input": report_content})
        audio_bytes = final_state["output"]
        return Response(content=audio_bytes, media_type="audio/mp3")
    except Exception as e:
        logger.exception(f"Error occurred during podcast generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ppt/generate")
async def generate_ppt(request: GeneratePPTRequest):
    try:
        from src.ppt.graph.builder import build_graph as build_ppt_graph
        report_content = request.content
        print(report_content)
        workflow = build_ppt_graph()
        final_state = workflow.invoke({"input": report_content})
        generated_file_path = final_state["generated_file_path"]
        with open(generated_file_path, "rb") as f:
            ppt_bytes = f.read()
        return Response(
            content=ppt_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
    except Exception as e:
        logger.exception(f"Error occurred during ppt generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/prose/generate")
async def generate_prose(request: GenerateProseRequest):
    try:
        from src.prose.graph.builder import build_graph as build_prose_graph
        logger.info(f"Generating prose for prompt: {request.prompt}")
        workflow = build_prose_graph()
        events = workflow.astream(
            {
                "content": request.prompt,
                "option": request.option,
                "command": request.command,
            },
            stream_mode="messages",
            subgraphs=True,
        )

        async def prose_stream_generator():
            import asyncio
            try:
                async for _, event in events:
                    try:
                        yield f"data: {event[0].content}\n\n"
                    except asyncio.CancelledError:
                        logger.info("Prose generation stream cancelled")
                        return
                    except Exception as e:
                        logger.error(f"Error in prose stream event: {e}")
                        yield f"data: Error: {str(e)}\n\n"
                        break
            except asyncio.CancelledError:
                logger.info("Prose generation workflow cancelled")
                return
            except Exception as e:
                logger.exception(f"Error in prose generation workflow: {e}")
                yield f"data: Error: {str(e)}\n\n"

        return StreamingResponse(
            prose_stream_generator(),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.exception(f"Error occurred during prose generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mcp/server/metadata", response_model=MCPServerMetadataResponse)
async def mcp_server_metadata(request: MCPServerMetadataRequest):
    """Get information about an MCP server."""
    try:
        # Set default timeout with a longer value for this endpoint
        timeout = 300  # Default to 300 seconds for this endpoint

        # Use custom timeout from request if provided
        if request.timeout_seconds is not None:
            timeout = request.timeout_seconds

        # Load tools from the MCP server using the utility function
        tools = await load_mcp_tools(
            server_type=request.transport,
            command=request.command,
            args=request.args,
            url=request.url,
            env=request.env,
            timeout_seconds=timeout,
        )

        # Create the response with tools
        response = MCPServerMetadataResponse(
            transport=request.transport,
            command=request.command,
            args=request.args,
            url=request.url,
            env=request.env,
            tools=tools,
        )

        return response
    except Exception as e:
        if not isinstance(e, HTTPException):
            logger.exception(f"Error in MCP server metadata endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        raise


@app.get("/api/rag/config", response_model=RAGConfigResponse)
async def rag_config():
    """Get the config of the RAG."""
    return RAGConfigResponse(provider=SELECTED_RAG_PROVIDER)


@app.get("/api/rag/resources", response_model=RAGResourcesResponse)
async def rag_resources(request: Annotated[RAGResourceRequest, Query()]):
    """Get the resources of the RAG."""
    try:
        from src.rag.builder import build_retriever
        retriever = build_retriever()
        if retriever:
            return RAGResourcesResponse(resources=retriever.list_resources(request.query))
        return RAGResourcesResponse(resources=[])
    except Exception as e:
        logger.exception(f"Error in RAG resources endpoint: {str(e)}")
        return RAGResourcesResponse(resources=[])
