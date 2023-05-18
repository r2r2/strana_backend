import tortoise
from typing import NewType
from common import requests, session
from src.floors import repos as floors_repos
from src.booking import repos as booking_repos
from src.projects import repos as projects_repos
from src.buildings import repos as buildings_repos


PropertyORM = NewType("PropertyORM", tortoise.Tortoise)
PropertyFloor = NewType("PropertyFloor", floors_repos.Floor)
PropertyBooking = NewType("PropertyBooking", booking_repos.Booking)
PropertyProject = NewType("PropertyProject", projects_repos.Project)
PropertySession = NewType("PropertySession", session.SessionStorage)
PropertyBuilding = NewType("PropertyBuilding", buildings_repos.Building)
PropertyFloorRepo = NewType("PropertyFloorRepo", floors_repos.FloorRepo)
PropertyBookingRepo = NewType("PropertyBookingRepo", booking_repos.BookingRepo)
PropertyProjectRepo = NewType("PropertyProjectRepo", projects_repos.ProjectRepo)
PropertyGraphQLRequest = NewType("PropertyGraphQLRequest", requests.GraphQLRequest)
PropertyBuildingRepo = NewType("PropertyBuildingRepo", buildings_repos.BuildingRepo)
