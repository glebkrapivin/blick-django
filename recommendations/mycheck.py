from models import (
    User,
    Session,
    Question,
    Category,
    SessionQuestion,
    Movie,
    SessionRecommendation,
)
from enum import Enum
from abc import abstractmethod
from typing import Dict


class Commands(Enum):
    Start = 1
    StartQuiz = 2
    AnswerQuestion = 3
    RequestAnotherRecommendation = 4
    RequestAnotherMovie = 5
    LikeRecommendation = 6
    DislikeRecommendation = 7
    Undefined = 8


class MessageTypes(Enum):
    New = 1
    Inline = 2


class Processor:
    def __init__(self):
        self.session = None
        self.command = None
        self.user_id = None

    def process(self, user_id: str, message_id: int, command: Dict):
        """ Сделать надо чтобы сессия определялась не пользователем и стейтом
        а ID  сообщения
        :return:
        """
        obj, _ = User.objects.get_orget_or_create_create(tg_name=user_id)
        session, created = Session.objects.get_or_create(
            user=obj, message_id=message_id
        )

        self.session = session
        self.command = command
        self.user_id = user_id

        if session.state is Session.State.START:
            return self.on_welcome()
        elif session.state is Session.State.QUIZ:
            return self.on_quiz()
        elif session.state is Session.State.RECOMMENDATION:
            return self.on_recommendation()

    def on_welcome(self):
        if self.command is Commands.StartQuiz:
            self.session.state = Session.State.QUIZ
            self.session.save()
            self.make_questions()
            return self.render_question()
        else:
            return self.render_welcome()

    def on_quiz(self):
        """
        Реагируем на
        * запрос остановки
        * ответ на вопрос
        
        На другие сообщения не делаем ничего
        """
        if self.command is Commands.RequestRecommendation:
            self.session.state = Session.State.RECOMMENDATION
            self.session.state.save()
            return self.render_recommendation()
        elif self.command is Commands.AnswerQuestion:
            self.record_answer()
            if not SessionQuestion.has_question(session=self.session):
                # Если у юзера кончились вопросы, то кидаем его в стейт рекомендации
                # и отправлямем рекомендацию
                self.session.state = Session.State.RECOMMENDATION
                self.session.save()
                return self.render_recommendation()
            return self.render_question()

    def on_recommendation(self):
        if self.command is Commands.RequestAnotherRecommendation:
            return self.render_recommendation()
        elif self.command is Commands.StartQuiz:
            # Отправлем новое welcome сообщение, получим новую сессии
            # и юзер сможет начать все сначала
            return self.render_welcome()
        elif self.command in (
            Commands.LikeRecommendation,
            Commands.DislikeRecommendation,
        ):
            sr: SessionRecommendation = (
                SessionRecommendation.objects.filter(session=self.session)
                .order_by("-created_at")
                .first()
            )
            if self.command is Commands.LikeRecommendation:
                sr.reaction = SessionRecommendation.Reactions.LIKE
            else:
                sr.reaction = SessionRecommendation.Reactions.DISLIKE
            sr.save()
            self.render_rate_callback()

    @abstractmethod
    def render_rate_callback(self):
        return "Nice recommendation"

    @abstractmethod
    def record_answer(self):
        print("записали ответик")

    def make_questions(self):
        """Рандомно выбираем вопросы для сессии,
        дергаем один вопрос для каждой категории
        """
        questions = []
        categories = Category.objects.all()
        for category in categories:
            question = Question.objects.filter(category=category).order_by("?").first()
            questions.append(SessionQuestion(session=self.session, question=question))
        SessionQuestion.objects.bulk_create(questions)

    @abstractmethod
    def render_recommendation(self):
        return (MessageTypes.Inline, "Советуем тебе фильм ВудиВудпекер")

    @abstractmethod
    def render_question(self):
        question = SessionQuestion.objects.filter(
            session=self.session, answer=None
        ).first()
        return (MessageTypes.Inline, question.text)

    def render_welcome(self):
        return (MessageTypes.New, "Чтобы начать что-то делать, нажмите /start")
