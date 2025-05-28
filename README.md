# PAKKET

**PAKKET** is an experimental educational project focused on building a low-level network protocol library from scratch.

The goal is to explore and implement the core layers of network communication—starting at the **transport layer** (TCP & UDP) and moving up to **application protocols** like **HTTP** and **WebSocket**.

## ✨ Goals

- Understand and implement TCP & UDP handling
- Build reusable socket-based transmission layers
- Layer application protocols (HTTP, WebSocket) on top
- Explore routing, parsing, and service composition

## 🧱 Structure

- `transmission/` – low-level TCP and UDP servers with thread-pool task dispatching
- `protocol/` – application-layer protocols (HTTP, WebSocket, etc.)
- `core/` – shared logic and abstractions
- `examples/` – runnable examples for learning and testing

## 📚 Purpose

This project is **not** production-ready — it's for **learning**, **exploration**, and **experimentation** with how networked systems are structured from the ground up.
