from enum import Enum, unique


@unique
class EmojiEnum(str, Enum):
    fire = "U+1F525"
    check_mark_button = "U+2705"
    thumbs_up = "U+1F44D"
    thumbs_down = "U+1F44E"
    red_heart = "U+2764"
    folded_hands = "U+1F64F"
    eyes = "U+1F440"
    ok_hand = "U+1F44C"
    star_struck = "U+1F929"
    smiling_face_with_sunglasses = "U+1F60E"
    loudly_crying_face = "U+1F62D"

    @classmethod
    def server_default(cls) -> str:
        return cls.fire.value
