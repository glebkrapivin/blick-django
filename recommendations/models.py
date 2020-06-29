from django.db import models


class User(models.Model):
    tg_name = models.CharField(max_length=256)
    joined_at = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    abbreviation = models.CharField(max_length=256)
    description = models.CharField(max_length=256)


class Movie(models.Model):

    main_url = models.URLField()

    url1 = models.URLField()
    url2 = models.URLField()

    title = models.CharField(max_length=256)
    description = models.TextField()

    def get_absolute_url(self):
        return "/recommendations/movies?movie={}".format(self.id)


class Session(models.Model):
    class State(models.TextChoices):
        START = 0
        QUIZ = 1
        RECOMMENDATION = 2

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    message_id = models.IntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    state = models.IntegerField(choices=State.choices, default=State.START)


class Question(models.Model):
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class SessionQuestion(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.BooleanField(default=None, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def has_question(self, session: Session):
        return  self.objects.filter(session=session, answer=None).exists()


class MovieCategory(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SessionRecommendation(models.Model):
    class Reactions(models.TextChoices):
        UNDEFINED = 0
        LIKE = 1
        DISLIKE = 2
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    reaction = models.CharField(choices=Reactions)
    created_at = models.DateTimeField(auto_now_add=True)
