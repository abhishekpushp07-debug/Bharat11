"""
Bharat 11 — Real-Time Socket.IO Manager
Handles WebSocket connections for live updates.

Events emitted:
- live_score: Live match score updates (to match room)
- question_resolved: When auto-settlement resolves a question (to contest room)
- leaderboard_update: When leaderboard rankings change (to contest room)
- template_locked: When a template deadline passes (to match room)
- contest_created: When auto-contest goes live (broadcast)
- contest_finalized: When a contest is finalized with results (to contest room)
"""
import logging
import socketio

logger = logging.getLogger(__name__)

# Create AsyncServer — will be wrapped as ASGI app in server.py
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25,
)

# Track connected clients
_connected_count = 0


# ==================== CONNECTION EVENTS ====================

@sio.event
async def connect(sid, environ):
    global _connected_count
    _connected_count += 1
    logger.info(f"Socket connected: {sid} (total: {_connected_count})")


@sio.event
async def disconnect(sid):
    global _connected_count
    _connected_count = max(0, _connected_count - 1)
    logger.info(f"Socket disconnected: {sid} (total: {_connected_count})")


# ==================== ROOM MANAGEMENT ====================

@sio.event
async def join_match(sid, data):
    """Client joins a match room to receive live score + template lock events."""
    match_id = data.get('match_id') if isinstance(data, dict) else None
    if match_id:
        room = f'match_{match_id}'
        await sio.enter_room(sid, room)
        logger.debug(f"{sid} joined room {room}")
        await sio.emit('room_joined', {'room': room, 'type': 'match'}, to=sid)


@sio.event
async def leave_match(sid, data):
    """Client leaves a match room."""
    match_id = data.get('match_id') if isinstance(data, dict) else None
    if match_id:
        room = f'match_{match_id}'
        await sio.leave_room(sid, room)
        logger.debug(f"{sid} left room {room}")


@sio.event
async def join_contest(sid, data):
    """Client joins a contest room to receive leaderboard + resolution events."""
    contest_id = data.get('contest_id') if isinstance(data, dict) else None
    if contest_id:
        room = f'contest_{contest_id}'
        await sio.enter_room(sid, room)
        logger.debug(f"{sid} joined room {room}")
        await sio.emit('room_joined', {'room': room, 'type': 'contest'}, to=sid)


@sio.event
async def leave_contest(sid, data):
    """Client leaves a contest room."""
    contest_id = data.get('contest_id') if isinstance(data, dict) else None
    if contest_id:
        room = f'contest_{contest_id}'
        await sio.leave_room(sid, room)
        logger.debug(f"{sid} left room {room}")


@sio.event
async def join_home(sid, data=None):
    """Client joins the home room for global broadcasts (contest_created, etc.)."""
    await sio.enter_room(sid, 'home')
    logger.debug(f"{sid} joined home room")


@sio.event
async def leave_home(sid, data=None):
    """Client leaves the home room."""
    await sio.leave_room(sid, 'home')
    logger.debug(f"{sid} left home room")


# ==================== BROADCAST HELPERS ====================

async def emit_live_score(match_id: str, score_data: dict):
    """Push live score update to everyone watching this match + home."""
    payload = {
        'match_id': match_id,
        'scores': score_data.get('scores', []),
        'status_text': score_data.get('status_text', ''),
        'match_winner': score_data.get('match_winner', ''),
        'updated_at': score_data.get('updated_at', ''),
    }
    await sio.emit('live_score', payload, room=f'match_{match_id}')
    await sio.emit('live_score', payload, room='home')


async def emit_question_resolved(contest_id: str, match_id: str, question_id: str, correct_option: str, entries_scored: int):
    """Push question resolution event to contest room."""
    payload = {
        'contest_id': contest_id,
        'match_id': match_id,
        'question_id': question_id,
        'correct_option': correct_option,
        'entries_scored': entries_scored,
    }
    await sio.emit('question_resolved', payload, room=f'contest_{contest_id}')
    await sio.emit('question_resolved', payload, room=f'match_{match_id}')


async def emit_leaderboard_update(contest_id: str, match_id: str = ''):
    """Push leaderboard refresh signal to contest room."""
    payload = {
        'contest_id': contest_id,
        'match_id': match_id,
        'action': 'refresh',
    }
    await sio.emit('leaderboard_update', payload, room=f'contest_{contest_id}')


async def emit_contest_created(contest_data: dict):
    """Broadcast new contest to all home room listeners."""
    payload = {
        'contest_id': contest_data.get('id', ''),
        'match_id': contest_data.get('match_id', ''),
        'name': contest_data.get('name', ''),
        'entry_fee': contest_data.get('entry_fee', 0),
        'auto_created': contest_data.get('auto_created', False),
    }
    await sio.emit('contest_created', payload, room='home')


async def emit_contest_finalized(contest_id: str, match_id: str, top_3: list):
    """Push finalization results to contest + match rooms."""
    payload = {
        'contest_id': contest_id,
        'match_id': match_id,
        'action': 'finalized',
        'top_3': top_3,
    }
    await sio.emit('contest_finalized', payload, room=f'contest_{contest_id}')
    await sio.emit('contest_finalized', payload, room=f'match_{match_id}')
    await sio.emit('contest_finalized', payload, room='home')


async def emit_template_locked(match_id: str, template_id: str, template_name: str = ''):
    """Push template lock event when deadline passes."""
    payload = {
        'match_id': match_id,
        'template_id': template_id,
        'template_name': template_name,
        'action': 'locked',
    }
    await sio.emit('template_locked', payload, room=f'match_{match_id}')


def get_socket_status() -> dict:
    """Return current socket connection stats."""
    return {
        'connected_clients': _connected_count,
        'server_active': True,
    }
