import re

from django import template


register = template.Library()


@register.filter
def youtube_url(url):
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^\/]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return f"https://www.youtube.com/embed/{match.group(1)}"
    return ''


@register.filter
def vkvideo_url(url):
    video_id = url.split('/')[-1].replace('video-', '')
    return f'https://vk.com/video_ext.php?oid=-{video_id.split("_")[0]}&id={video_id.split("_")[1]}'
