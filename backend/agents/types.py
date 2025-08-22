from pydantic import BaseModel
from typing import List

class ScheduleItem(BaseModel):
    time: str
    activity: str

class ItineraryDay(BaseModel):
    day: int
    date: str
    schedule: List[ScheduleItem]

class Restaurant(BaseModel):
    name: str
    location: str
    specialty: str
    cost: str

class Attraction(BaseModel):
    name: str
    highlight: str
    ticket: str

class Accommodation(BaseModel):
    name: str
    location: str
    feature: str
    price: str

class TravelRecommendation(BaseModel):
    itinerary: List[ItineraryDay]
    restaurants: List[Restaurant]
    attractions: List[Attraction]
    accommodations: List[Accommodation]
    tips: List[str]