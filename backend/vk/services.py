from common.vk import VkScraper
from common.tasks import save_remote_image
from .models import VkPost, VkPostImages


def scrape_posts_vk():
    """
    Парсинг постов vk
    """
    vk = VkScraper()

    if response_posts := vk.get_posts().get("response"):
        if posts := response_posts.get('items'):
            for post in posts:
                group_name = vk.params.get("domain")
                from_id = post.get("from_id")
                _id = post.get('id')
                link = f"https://vk.com/{group_name}?w=wall{from_id}_{_id}"
                obj, created = VkPost.objects.get_or_create(
                    shortcode=_id,
                    link=link,
                    defaults={
                        "descriptions": post.get("text"),
                        "likes": post["likes"]["count"],
                        "timestamp": post.get("date"),
                    }
                )
                main_photo = False
                if created and post.get("attachments"):
                    if attachments := post.get("attachments"):

                        for i, attachment in enumerate(attachments):
                            if image := attachment.get('photo'):
                                url = ""
                                if sizes := image.get("sizes"):
                                    for size in sizes:
                                        if size.get('height') == 1080:
                                            url = size['url']
                                if not url:
                                    VkPost.objects.filter(id=obj.id).delete()
                                    break
                                if not main_photo:
                                    save_remote_image.delay(
                                        "vk", "VkPost", obj.id, "image", url
                                    )
                                    main_photo = True
                                else:
                                    slide_obj, created = VkPostImages.objects.get_or_create(
                                        id_image=image.get('id'),
                                        defaults={"post": obj, "order": i}
                                    )

                                    if created and image:
                                        save_remote_image.delay(
                                            "vk",
                                            "VkPostImages",
                                            slide_obj.id,
                                            "image",
                                            url,
                                        )
                elif obj_post := obj:
                    update_post(obj_post.link)


def update_post(link_post):
    """
    Обновление данных поста
    """
    vk = VkScraper()
    if link_post:
        if request_json := vk.get_post(post=link_post.split('?w=wall')[1]).get("response"):
            post = request_json[0]
            group_name = vk.params.get("domain")
            from_id = post.get("from_id")
            _id = post.get('id')
            desc = post.get("text")
            likes = post["likes"]["count"]
            link = f"https://vk.com/{group_name}?w=wall{from_id}_{_id}"
            VkPost.objects.filter(link=link).update(
                descriptions=desc,
                likes=likes,
            )
