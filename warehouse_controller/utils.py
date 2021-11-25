from django.utils.text import slugify
import string
import random

def generate_rand(size=5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=size))

def generate_slug(instance, slug=None):
    class_inst = instance.__class__
    if not slug:
        slug = slugify(instance.name)
    slug_exist = class_inst.objects.filter(slug=slug)
    if slug_exist.exists():
        rand = generate_rand()
        slug = slug + rand
        return generate_slug(instance, slug)
    return slug