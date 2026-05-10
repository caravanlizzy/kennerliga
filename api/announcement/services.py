from announcement.models import Announcement


def delete_registration_announcements():
    """
    Deletes all active registration announcements.
    """
    Announcement.objects.filter(type=Announcement.AnnouncementType.REGISTER).delete()
