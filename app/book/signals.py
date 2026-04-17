from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import UserPrefrence, Book, Review


@receiver(post_save, sender=Review)
def update_prefrences_on_review(sender, instance, created, **kwargs):
    if created and instance.rating > 3:
        obj, _ = UserPrefrence.objects.get_or_create(
            user=instance.user,
            gener=instance.book.gener,
        )

        obj.score += 1
        obj.save()


@receiver(post_save, sender=Book)
def update_preferences_on_contribution(sender, instance, created, **kwargs):
    if created and instance.rating > 3:
        obj, _ = UserPrefrence.objects.get_or_create(
            user=instance.user,
            gener=instance.book.gener,
        )

        obj.score += 1
        obj.save()
