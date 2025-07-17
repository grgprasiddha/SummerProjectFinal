from django.conf import settings
import os

def get_category_image(category_slug):
    """
    Returns the appropriate image path for a given category.
    Falls back to a default image if the specific category image doesn't exist.
    """
    category_images = {
        'graphic-design': {
            'static': 'core/images/categories/graphic-design.png',
            'fallback': 'https://img.icons8.com/color/96/000000/design.png',
            'placeholder': 'https://via.placeholder.com/300x200/FF6B6B/FFFFFF?text=Graphic+Design'
        },
        'digital-marketing': {
            'static': 'core/images/categories/digital-marketing.png',
            'fallback': 'https://img.icons8.com/fluency/96/marketing.png',
            'placeholder': 'https://via.placeholder.com/300x200/4ECDC4/FFFFFF?text=Digital+Marketing'
        },
        'writing-translation': {
            'static': 'core/images/categories/writing-translation.png',
            'fallback': 'https://img.icons8.com/color/96/000000/translation.png',
            'placeholder': 'https://via.placeholder.com/300x200/45B7D1/FFFFFF?text=Writing+%26+Translation'
        },
        'video-animation': {
            'static': 'core/images/categories/video-animation.png',
            'fallback': 'https://img.icons8.com/color/96/000000/video-editing.png',
            'placeholder': 'https://via.placeholder.com/300x200/96CEB4/FFFFFF?text=Video+%26+Animation'
        },
        'programming': {
            'static': 'core/images/categories/programming.png',
            'fallback': 'https://img.icons8.com/color/96/000000/programming.png',
            'placeholder': 'https://via.placeholder.com/300x200/FFEAA7/000000?text=Programming+%26+Tech'
        },
        'business': {
            'static': 'core/images/categories/business.png',
            'fallback': 'https://img.icons8.com/color/96/000000/business.png',
            'placeholder': 'https://via.placeholder.com/300x200/DDA0DD/FFFFFF?text=Business'
        },
        'lifestyle': {
            'static': 'core/images/categories/lifestyle.png',
            'fallback': 'https://img.icons8.com/color/96/000000/lifestyle.png',
            'placeholder': 'https://via.placeholder.com/300x200/98D8C8/FFFFFF?text=Lifestyle'
        }
    }
    
    if category_slug in category_images:
        return category_images[category_slug]
    
    # Default fallback for unknown categories
    return {
        'static': 'core/images/categories/default.png',
        'fallback': 'https://img.icons8.com/color/96/000000/work.png',
        'placeholder': 'https://via.placeholder.com/300x200/CCCCCC/FFFFFF?text=Service'
    }

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
    
    return category_names.get(category_slug, 'Other')   