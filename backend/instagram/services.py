from common.instagram import InstagramScraper
from common.tasks import save_remote_image
from .models import InstagramPost, InstagramPostImages, InstagramAccount
from .constants import POST_LINK


def scrape_posts_instagram(id, first):
    """
    Парсинг постов инстаграмм
    """
    i = InstagramScraper()
    i.authenticate()
    account = InstagramAccount.objects.filter(id=id, first=first).first()
    request_json = i.get_posts(id, first)
    posts = request_json["data"]["user"]["edge_owner_to_timeline_media"]["edges"]

    for post in posts:
        post = post["node"]
        obj, created = InstagramPost.objects.get_or_create(
            id_instagram=post["id"],
            defaults={
                "descriptions": post["edge_media_to_caption"]["edges"][0]["node"]["text"],
                "shortcode": post["shortcode"],
                "likes": post["edge_media_preview_like"]["count"],
                "timestamp": post["taken_at_timestamp"],
                "account": account,
                "link": POST_LINK + post["shortcode"],
            },
        )

        if created and post["display_url"]:
            save_remote_image.delay(
                "instagram", "InstagramPost", obj.id, "image", post["display_url"]
            )

        if post["__typename"] == "GraphSidecar":
            post_slide_images = post["edge_sidecar_to_children"]["edges"]

            for i, slide in enumerate(post_slide_images):
                slide = slide["node"]
                slide_obj, created = InstagramPostImages.objects.get_or_create(
                    id_instagram=slide["id"], defaults={"post": obj, "order": i}
                )

                if created and slide["display_url"]:
                    save_remote_image.delay(
                        "instagram",
                        "InstagramPostImages",
                        slide_obj.id,
                        "image",
                        slide["display_url"],
                    )


def update_post(shortcode):
    """
    Обновление данных поста
    """
    i = InstagramScraper()
    i.authenticate()
    request_json = i.get_post(shortcode)
    post = request_json["data"]["shortcode_media"]
    InstagramPost.objects.filter(shortcode=shortcode).update(
        likes=post["edge_media_preview_like"]["count"]
    )
