from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from django.views import View
from django.views.generic import ListView

import json
import logging

logging.basicConfig(level="DEBUG")

from .models import User, Session, Question, Category, SessionQuestion, Movie

import django_tables2 as tables

from django.utils.html import format_html


class ImageColumn(tables.Column):
    def render(self, value):

        return format_html('<img src="{value}" width=300px/>', value=value)


class SimpleTable(tables.Table):
    name = tables.Column()

    main_url = ImageColumn()
    url1 = ImageColumn(linkify=True)
    url2 = ImageColumn(linkify=True)


table = SimpleTable(Movie.objects.all())


class MovieImages(View):
    def get(self, request, *args, **kwargs):

        if request.GET.get("movie"):
            m = Movie.objects.get(pk=request.GET.get("movie"))
            m.main_url = request.GET.get("main_url")
            m.save()

        return render(request, "recommendations/movietable.html", {"table": table})


#
# class MovieImages(ListView):
#     model = Movie
#     template_name = "recommendations/movietable.html"


class Bot(View):
    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)

        user_id = data["message"]["from"]["id"]

        obj, _ = User.objects.get_orget_or_create_create(tg_name=user_id)
        session, created = Session.objects.get_or_create(user=obj, state__lt=2)

        __command__ = None

        if __command__ == "/reset":
            session.state = 2
            session.save()

        if session.state == 2:
            return self.make_prediction()
        elif session.state == 1:
            self.process_answer(session, 3, 1)
            if not SessionQuestion.objects.filter(
                session=session, answer=None
            ).exists():
                session.state = 2
                session.save()
                return self.make_prediction()

            return self.ask_question(session)
        elif session.state == 0:

            self.make_questions(session)
            session.state = 1
            session.save()
            return self.ask_question(session)

    @staticmethod
    def make_questions(session: Session):
        questions = []
        categories = Category.objects.all()
        for category in categories:
            question = Question.objects.filter(category=category).order_by("?").first()
            questions.append(SessionQuestion(session=session, question=question))
        SessionQuestion.objects.bulk_create(questions)

    @staticmethod
    def ask_question(session):
        question = SessionQuestion.objects.filter(session=session, answer=None).first()

        return JsonResponse(
            {
                "method": "sendMessage",
                "chat_id": msg["chat"]["id"],
                "text": "Что-то пошло не так, боту пришло сообщение из группы.",
            }
        )

    @staticmethod
    def process_answer(session: Session, question: int, answer: bool):
        question = SessionQuestion.objects.filter(
            session=session, question_id=question
        ).first()
        question.answer = answer
        question.save()

    @staticmethod
    def make_prediction():
        return Bot.send_message("predicted")

    @staticmethod
    def send_message():
        pass

    @staticmethod
    def get_command():
        return "1"

    def start_quiz(self):
        pass
