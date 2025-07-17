from django import template
from django.template.defaultfilters import slugify

register = template.Library()

@register.simple_tag
def get_category_image(category_slug):
    """
    Returns the appropriate image URL for a given category.
    """
    category_images = {
        'graphic-design': {
            'icon': 'https://img.icons8.com/color/96/000000/design.png',
            'background': '#FF6B6B'
        },
        'digital-marketing': {
            'icon': 'https://img.icons8.com/fluency/96/marketing.png',
            'background': '#4ECDC4'
        },
        'writing-translation': {
            'icon': 'https://img.icons8.com/color/96/000000/translation.png',
            'background': '#45B7D1'
        },
        'video-animation': {
            'icon': 'https://img.icons8.com/color/96/000000/video-editing.png',
            'background': '#96CEB4'
        },
        'programming': {
            'icon': 'https://img.icons8.com/color/96/000000/programming.png',
            'background': '#FFEAA7'
        },
        'business': {
            'icon': 'https://img.icons8.com/color/96/000000/business.png',
            'background': '#DDA0DD'
        },
        'lifestyle': {
            'icon': 'https://img.icons8.com/color/96/000000/spa.png',
            'background': '#98D8C8'
        }
    }
    
    # Convert category to slug if it's not already
    category_key = slugify(category_slug)
    
    if category_key in category_images:
        return category_images[category_key]
    
    # Default fallback
    return {
        'icon': 'https://img.icons8.com/color/96/000000/work.png',
        'background': '#CCCCCC'
    }

@register.simple_tag
def get_category_display_name(category_slug):
    """
    Returns the display name for a category slug.
    """
    category_names = {
        'graphic-design': 'Graphic & Design',
        'digital-marketing': 'Digital Marketing',
        'writing-translation': 'Writing & Translation',
        'video-animation': 'Video & Animation',
        'programming': 'Programming & Tech',
        'business': 'Business',
        'lifestyle': 'Lifestyle',
    }
    
    category_key = slugify(category_slug)
    return category_names.get(category_key, 'Other') 