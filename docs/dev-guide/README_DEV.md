# 📘 Iteradraw — Developer README

## 🧭 Purpose
Iteradraw is a performance-focused rewrite of *Draw-This*, a drawing slideshow app designed for structured art practice.

**Primary Goals**
- Replace **Tkinter → PySide6** for flexibility and scaling.
- Reduce Python overhead in hot loops (possible Rust migration later).
- Strengthen backend modularity via **immutable dataclasses + service layer**.
- Provide a polished **cross-platform** experience for artists.
- Provide CLI entry point for enthusiast use/scripting.

---

## 🧩 Architecture Overview
- `core/` — slideshow logic, timers, image selection.
- `data/` — persistence (SQLite + JSON modules).
- `services/` — high-level runtime controllers (render, session, settings).
- `gui/` — PySide 6 interface.
- `assets/` — images and UI resources.

---

## ⚙️ Running
```bash
python -m iteradraw.main

