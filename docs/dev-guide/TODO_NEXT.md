
---

## ✅ `docs/TODO_NEXT.md`

This one is your **tactical list**, updated almost daily or per commit.  
It should be super short and always reflect the next small *move* — not big goals.

```markdown
# ✅ TODO — Iteradraw Next Steps

_Last updated: 2025-10-29_

---

Here is that to-do list in markdown format.

## ✅ Phase 1: The Core Slideshow Pipeline (The "Happy Path")
This phase is focused on getting *one image* from the database onto the screen, proving the main slideshow pipeline. We will use a *synchronous* loader and no caching for now.

- [ ] **Database:**
  - [ ] Define the `images` table schema in your database.
  - [ ] Implement the `ImageRepo` with a simple, synchronous `add_image_paths_for_folder` method (for testing) and a `get_all_image_paths` method.
  - [ ] *Test:* Manually add a few image paths to the database.

- [ ] **Domain & Application:**
  - [ ] Define the `SessionValidated` and `ImageDisplayed` domain events.
  - [ ] Create the synchronous `PlaylistService`.
  - [ ] Give `PlaylistService` a `start_session(event: SessionValidated)` handler that queries the `ImageRepo` for all paths and stores them in a list.
  - [ ] Implement `handle_next_image` (as a command handler) that increments `self.index`, gets the next path, and publishes `ImageDisplayed`.

- [ ] **Presentation & Infrastructure:**
  - [ ] Define the `IImageLoader` interface (in domain) and implement `ImageLoader` (in infrastructure) to synchronously load a file path into a `QImage`.
  - [ ] Create the "dumb" `SlideshowView` (`QOpenGLWidget`) with a method like `set_texture_to_render(texture_id)`.
  - [ ] Create the `RendererService` (in presentation).
  - [ ] Have the `RendererService` subscribe to `ImageDisplayed`.
  - [ ] In its `on_image_displayed` slot:
    1.  Call `self.image_loader.load_image_data(...)`.
    2.  Create a new `QOpenGLTexture` from the `QImage`.
    3.  (Destroy the *old* texture to prevent leaks).
    4.  Call `self.view.set_texture_to_render(...)` with the new texture ID.

---

## ✅ Phase 2: The Async Data Pipeline (Background Population)
This phase builds the complex, asynchronous crawling system that feeds the database, replacing the manual adding of images.

- [ ] **Database:**
  - [ ] Upgrade the `images` table schema to include `last_crawled_at`.
  - [ ] Implement the "mark-and-sweep" logic in the `ImageRepo`.

- [ ] **Application Services:**
  - [ ] Create the `CrawlerService` (async).
  - [ ] Implement its thread-pool logic to process a queue of "crawl jobs."
  - [ ] Make the `CrawlerService` use the `ImageRepo`'s mark-and-sweep methods for each job.
  - [ ] Create the `FileDiscoveryService` (async).
  - [ ] Implement its logic to watch for `FolderSetAdded`/`FolderModified` events and dispatch "crawl jobs" to the `CrawlerService`.

- [ ] **Crawler Pausing:**
  - [ ] Define `FolderEnabledStatusChanged` event.
  - [ ] Make the `CrawlerService` subscribe to this event.
  - [ ] Implement the logic to find, pause, or resume/re-queue a crawl job based on a folder's `is_enabled` status.

---

## ✅ Phase 3: The Optimized Slideshow (Buffering & Safety)
This phase upgrades the "Phase 1" slideshow pipeline from a simple, one-at-a-time loader to the high-performance, safe, and buffered system we designed.

- [ ] **Async Safety ("Zombie" Protection):**
  - [ ] Modify the `PlaylistService` to maintain a `generation` ID, incrementing it on every state change (`next`, `prev`, `stop`).
  - [ ] Update the `ImageDisplayed` event to include the `generation` ID.
  - [ ] Make the `RendererService` store the `current_generation`.
  - [ ] Make the `ImageLoader` asynchronous (e.g., using a `QThreadPool` or `asyncio`).
  - [ ] Implement the check: When an async load finishes, it must check its `generation` tag against the `RendererService`'s `current_generation`. If they don't match, discard the result.

- [ ] **Buffering (The Two-Window System):**
  - [ ] In `RendererService`, create the texture cache (`dict` mapping `path -> QOpenGLTexture`).
  - [ ] Define the "Narrow Load Window" (e.g., `index ± 3`).
  - [ ] Define the "Wide Eviction Window" (e.g., `index ± 8`).
  - [ ] In `on_image_displayed`:
    1.  Update the windows based on the new `index`.
    2.  **Evict:** Loop through the cache. Any texture *outside* the "Wide Window" gets `destroy()`ed and removed.
    3.  **Load:** Loop through the indices *inside* the "Narrow Window." Any index *not* in the cache gets a new async load job queued (tagged with the `current_generation`).
    4.  **Render:** Get the *current* image's texture from the cache and render it (it should have been pre-loaded by a previous step).

---

### 💤 Parking Lot (not urgent)
- [ ] Stats collection system (post-session data)
- [ ] Undo/Redo domain design
- [ ] CLI-only mode for headless operation
- [ ] Move constants to `config/` module
- [ ] Add `__all__` exports for domain packages

