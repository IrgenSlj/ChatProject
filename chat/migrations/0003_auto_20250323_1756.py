from django.db import migrations

def populate_chat_room(apps, schema_editor):
    Message = apps.get_model('chat', 'Message')
    ChatRoom = apps.get_model('chat', 'ChatRoom')

    # Example: Assign all messages from a specific user to a specific chat room
    try:
        default_chat_room = ChatRoom.objects.get(name="General Chat")
    except ChatRoom.DoesNotExist:
        default_chat_room = ChatRoom.objects.create(name="General Chat")

    for message in Message.objects.all():
        # Replace this with your actual logic to determine the correct ChatRoom
        # Example: Assign all messages from user with id 1 to the default chat room
        if message.sender_id == 1:
            message.chat_room = default_chat_room
            message.save()

def reverse_populate_chat_room(apps, schema_editor):
    # This is optional, but good practice.  Define how to reverse the migration.
    Message = apps.get_model('chat', 'Message')
    for message in Message.objects.all():
        message.chat_room = None  # Or whatever makes sense to reverse
        message.save()

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chatroom_remove_message_receiver_and_more'),  # Replace with the previous migration file
    ]

    operations = [
        migrations.RunPython(populate_chat_room, reverse_populate_chat_room),
    ]