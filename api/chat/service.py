from chat.models import Chat
from user.models import User


def create_chat_announcement(text):
    """
    Creates a chat message labeled with the given text, sent by user 'haligh' or the first superuser.
    Used for automated system announcements in the chat.
    """
    try:
        haligh = User.objects.get(username="haligh")
    except User.DoesNotExist:
        # Fallback for tests or if user 'haligh' is missing
        haligh = User.objects.filter(is_superuser=True).first()

    if haligh:
        Chat.objects.create(user=haligh, text="Announcement!", label=text)
