/**
 * Socket Store - Zustand
 * Real-time WebSocket connection management
 */
import { create } from 'zustand';
import { io } from 'socket.io-client';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const useSocketStore = create((set, get) => ({
  socket: null,
  isConnected: false,
  
  // Connect to socket
  connect: () => {
    const { socket } = get();
    if (socket?.connected) return;
    
    const newSocket = io(BACKEND_URL, {
      transports: ['websocket', 'polling'],
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });
    
    newSocket.on('connect', () => {
      console.log('Socket connected:', newSocket.id);
      set({ isConnected: true });
    });
    
    newSocket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
      set({ isConnected: false });
    });
    
    newSocket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      set({ isConnected: false });
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
  
  // Subscribe to match updates
  subscribeToMatch: (matchId) => {
    const { socket } = get();
    if (socket?.connected) {
      socket.emit('join_match', { match_id: matchId });
    }
  },
  
  // Unsubscribe from match
  unsubscribeFromMatch: (matchId) => {
    const { socket } = get();
    if (socket?.connected) {
      socket.emit('leave_match', { match_id: matchId });
    }
  },
  
  // Subscribe to contest leaderboard
  subscribeToContest: (contestId) => {
    const { socket } = get();
    if (socket?.connected) {
      socket.emit('join_contest', { contest_id: contestId });
    }
  },
  
  // Unsubscribe from contest
  unsubscribeFromContest: (contestId) => {
    const { socket } = get();
    if (socket?.connected) {
      socket.emit('leave_contest', { contest_id: contestId });
    }
  },
  
  // Emit event
  emit: (event, data) => {
    const { socket } = get();
    if (socket?.connected) {
      socket.emit(event, data);
    }
  },
  
  // Listen to event
  on: (event, callback) => {
    const { socket } = get();
    if (socket) {
      socket.on(event, callback);
    }
  },
  
  // Remove listener
  off: (event, callback) => {
    const { socket } = get();
    if (socket) {
      socket.off(event, callback);
    }
  },
}));
