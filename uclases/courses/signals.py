from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from courses.models import Rating

@receiver([post_save, post_delete], sender=Rating)
def update_profile_rating_on_change(sender, instance, **kwargs):
    """
    Recalcula y actualiza `rating_promedio` y `total_ratings`
    en el perfil calificado cuando se crea/elimina un Rating.
    Usa agregaciones para mantener consistencia.
    """
    calificado = getattr(instance, 'calificado', None)
    if calificado is None:
        return

    agg = calificado.ratings_recibidos.aggregate(
        promedio=Avg('valoracion'),
        total=Count('id')
    )
    promedio = agg['promedio'] or 0
    total = agg['total'] or 0

    # Guardar únicamente los campos que cambiaron
    calificado.rating_promedio = round(promedio, 2)
    calificado.total_ratings = total
    calificado.save(update_fields=['rating_promedio', 'total_ratings'])