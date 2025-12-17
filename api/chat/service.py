from chat.models import Chat
from user.models import User


def create_chat_announcement(text):
    haligh = User.objects.get(username='haligh')
    Chat.objects.create(user=haligh, text='Announcement!', label=text)