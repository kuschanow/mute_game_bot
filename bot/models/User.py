from django.db import models

class User(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False, editable=False, blank=False)
    username = models.TextField(null=True)
    first_name = models.TextField(null=False, blank=False)
    last_name = models.TextField(null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[id {self.id}] - [username {self.username}] - [name {self.first_name}{f' {self.last_name}' if self.last_name is not None else ''}]"
