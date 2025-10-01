# Django Signals & ORM Project

This project demonstrates how to use **Django Signals**, **ORM basics**, **advanced ORM**, and **caching** in a messaging app.

## 📌 Objective
Automatically notify users when they receive a new message.

## 🏗 Project Setup

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/alx-backend-python.git
cd alx-backend-python/Django-signals_orm-0x04
### Objective: Automatically clean up related data when a user deletes their account

**Instructions Implemented:**
- Added a `delete_user` view to allow users to delete their account.
- Implemented a `post_delete` signal on the `User` model to ensure cleanup of:
  - Messages (sent and received by the user).
  - Notifications related to the user.
  - Message history edits created by the user.
- Ensured foreign key constraints use `CASCADE` to handle automatic deletion.

**Files Modified:**
- `messaging/models.py` – set foreign keys with `on_delete=models.CASCADE`.
- `messaging/signals.py` – added `post_delete` cleanup signal for users.
- `messaging/views.py` – created `delete_user` view.
- `messaging/tests.py` – added tests to confirm cleanup behavior.
### Objective: Implement threaded conversations where users can reply to specific messages

**Instructions Implemented:**
- Modified the `Message` model to include a `parent_message` self-referential foreign key.
- Implemented `get_thread()` recursive method to fetch nested replies.
- Optimized queries using `select_related` and `prefetch_related` to avoid N+1 query problems.
- Added a view (`conversation_view`) to retrieve and display a threaded conversation.
- Wrote unit tests to verify threaded reply functionality.

**Files Modified:**
- `messaging/models.py`
- `messaging/views.py`
- `messaging/tests.py`