import requests
from hashlib import md5


class LK:
    URL = "https://lks.strana.com/basket"
    SALT = "strana5zKCOSp3"
    ROOMS_CONVERT = {
        0: "Студия",
        1: "Одно",
        2: "Двух",
        3: "Трех",
        4: "Четырех",
        5: "Пяти",
        6: "Шести",
        7: "Семи",
        8: "Восьми",
        9: "Девяти",
    }

    def __init__(self, reservation):
        self.reservation = reservation
        self.data = dict()

    def send_lead(self):
        response = requests.post(self.URL, data=self.get_payload())
        return response

    def get_payload(self) -> dict:
        token = str()
        payload = dict(
            name=self.get_name(),
            city=self.get_city(),
            image=self.get_image(),
            floor=self.get_floor(),
            house=self.get_house(),
            users_region=self.get_city(),
            image_plan=self.get_image_plan(),
            booking_period=self.get_booking_period(),
            booking_price=self.get_booking_price(),
            project=self.reservation.project.name,
            price=str(self.reservation.property.price)[:-3],
            number=str(self.reservation.property.number),
            profitbase_id=str(self.reservation.property.id),
            amo_pipeline_id=str(self.reservation.project.amo_pipeline_id),
            amo_responsible_user_id=str(self.reservation.project.amo_responsible_user_id),
            address=str(),
        )
        for _, value in payload.items():
            token += f"{value}."
        token += self.SALT
        payload["token"] = md5(token.encode("utf-8")).hexdigest()
        self.data = payload
        return payload

    def get_name(self):
        name = str(
            (
                f"{self.ROOMS_CONVERT[self.reservation.property.rooms]}комнатная"
                if self.reservation.property.rooms
                else "Квартира"
            )
            + " "
            + str(self.reservation.property.area)
            + " м\u00B2"
        )
        return name

    def get_image(self):
        image = str()
        if self.reservation.property.plan_png:
            image = self.reservation.property.plan_png.url
        elif self.reservation.property.plan:
            image = self.reservation.property.plan.url
        return image

    def get_image_plan(self):
        image_plan = str()
        if self.reservation.property.floor:
            if self.reservation.property.floor.plan:
                image_plan = self.reservation.property.floor.plan.url
        return image_plan

    def get_house(self):
        house = str()
        if self.reservation.property.building:
            if self.reservation.property.building.name:
                house = self.reservation.property.building.name
        return house

    def get_floor(self):
        floor = str()
        if self.reservation.property.floor:
            if self.reservation.property.floor.number:
                floor = str(self.reservation.property.floor.number)
        return floor

    def get_booking_period(self):
        period = str()
        if self.reservation.property.building:
            if self.reservation.property.building.booking_period:
                period = str(self.reservation.property.building.booking_period)
        return period

    def get_booking_price(self):
        price = str()
        if self.reservation.property.building:
            if self.reservation.property.building.booking_price:
                price = str(self.reservation.property.building.booking_price)
        return price

    def get_city(self):
        city = str()
        if self.reservation.project.city:
            if self.reservation.project.city.name:
                city = str(self.reservation.project.city.name)
        return city
