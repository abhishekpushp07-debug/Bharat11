/**
 * Bharat 11 — Real-Time Socket Store
 * Connects to Socket.IO backend for live updates
 */
import { create } from 'zustand';
import { io } from 'socket.io-client';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const useSocketStore = create((set, get) => ({
  socket: null,
  isConnected: false,
  lastEvent: null,

  // Connect to Socket.IO backend
  connect: () => {
    const { socket } = get();
    if (socket?.connected) return;

    // Disconnect any stale socket
    if (socket) {
      socket.disconnect();
    }

    const newSocket = io(BACKEND_URL, {
      path: '/api/socket.io/',
      transports: ['websocket', 'polling'],
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 2000,
      reconnectionDelayMax: 10000,
      timeout: 20000,
    });

    newSocket.on('connect', () => {
      console.log('[Socket] Connected:', newSocket.id);
      set({ isConnected: true });
      // Auto-join home room for global broadcasts
      newSocket.emit('join_home');
    });

    newSocket.on('disconnect', (reason) => {
      console.log('[Socket] Disconnected:', reason);
      set({ isConnected: false });
    });

    newSocket.on('connect_error', (error) => {
      console.warn('[Socket] Connection error:', error.message);
      set({ isConnected: false });
    });

    newSocket.on('room_joined', (data) => {
      console.log('[Socket] Joined room:', data.room);
    });

    set({ socket: newSocket });
  },

  // Disconnect socket
  disconnect: () => {
    const { socket } = get();
    if (socket) {
      socket.disconnect();
      set({ socket: null, isConnected: false });
    }
  },

  // Join a match room (for live_score, template_locked events)
  joinMatch: (matchId) => {
    const { socket } = get();
    if (socket?.connected && matchId) {
      socket.emit('join_match', { match_id: matchId });
    }
  },

  // Leave match room
  leaveMatch: (matchId) => {
    const { socket } = get();
    if (socket?.connected && matchId) {
      socket.emit('leave_match', { match_id: matchId });
    }
  },

  // Join a contest room (for leaderboard_update, question_resolved events)
  joinContest: (contestId) => {
    const { socket } = get();
    if (socket?.connected && contestId) {
      socket.emit('join_contest', { contest_id: contestId });
    }
  },

  // Leave contest room
  leaveContest: (contestId) => {
    const { socket } = get();
    if (socket?.connected && contestId) {
      socket.emit('leave_contest', { contest_id: contestId });
    }
  },

  // Subscribe to a specific event
  on: (event, callback) => {
    const { socket } = get();
    if (socket) {
      socket.on(event, callback);
    }
  },

  // Unsubscribe from event
  off: (event, callback) => {
    const { socket } = get();
    if (socket) {
      socket.off(event, callback);
    }
  },

  // Emit custom event
  emit: (event, data) => {
    const { socket } = get();
    if (socket?.connected) {
      socket.emit(event, data);
    }
  },
}));
