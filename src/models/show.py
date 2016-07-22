from src.common.database import Database


class Show(object):

    def __init__(self, title, rating, poster, trailer, release_date):
        self.title=title
        self.rating=rating
        self.poster=poster
        self.trailer=trailer
        self.release_date=release_date


    def json(self):
        return {
            "title":self.title,
            "rating":self.rating,
            "poster":self.poster,
            "trailer":self.trailer,
            "release_date":self.release_date,
        }

    def save_to_mongo(self,genre):
        Database.insert(genre,self.json())

    @classmethod
    def from_mongo(cls,genre,id):
        data=Database.find(genre,{"_id":id})
        return cls(**data)